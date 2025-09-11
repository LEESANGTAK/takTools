//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_TYPE_INFO_H
#define AMINO_CORE_INTERNAL_TYPE_INFO_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file TypeInfo.h
/// \see Amino::Internal::TypeInfo

#include <Amino/Core/CoreExport.h>

#include <Amino/Core/ArrayFwd.h>
#include <Amino/Core/PtrFwd.h>
#include <Amino/Core/StringView.h>

#include "ConfigMacros.h"

#include <cassert>
#include <cstdint>
#include <cstring>
#include <type_traits>
#include <typeinfo>

//==============================================================================
// NAMESPACE Amino::Internal
//==============================================================================

namespace Amino {
namespace Internal {

/// \brief Forward declare internal class with priviledged access to \ref
/// TypeInfo and \ref TypeId.
class TypeInfoDetails;
class RuntimeTypeInfo;

/// \brief Internal tag used by \ref TypeId to allow creating null \ref TypeId.
struct NullTypeInfo {};

//==============================================================================
// CLASS TypeInfo
//==============================================================================

/// \brief Type information associated with a type `T`.
///
/// This is the internal implementation class of \ref TypeId.
class TypeInfo {
public:
    /*----- static member functions -----*/

    /// \brief Get the singleton \ref TypeInfo for the given type `T`.
    template <typename T>
    static TypeInfo const& get() noexcept {
        return GetInstance<std::remove_cv_t<T>>::s_instance;
    }

    /*----- member functions -----*/

    /// \brief Comparison operators.
    ///
    /// Used to know it two \ref TypeInfo are the same, for example to allow
    /// accessing the payload of an \ref Any. Also used to make \ref TypeInfo
    /// and \ref TypeId usable in ordered containers.
    /// \{
    bool operator==(TypeInfo const& o) const noexcept {
        // runtime type info are always unique
        if (isRuntime() && o.isRuntime()) return this == &o;
        const bool result =
            (m_category == o.m_category && m_nesting == o.m_nesting) &&
            (getRawName().data() == o.getRawName().data() ||
             getRawName() == o.getRawName());
        return result;
    }
    bool operator<(TypeInfo const& o) const noexcept {
        if (m_nesting != o.m_nesting) return m_nesting < o.m_nesting;
        if (m_category != o.m_category) return m_category < o.m_category;
        if (getRawName().data() == o.getRawName().data()) return false;
        return getRawName() < o.getRawName();
    }
    bool operator>(TypeInfo const& o) const noexcept {
        if (m_nesting != o.m_nesting) return m_nesting > o.m_nesting;
        if (m_category != o.m_category) return m_category > o.m_category;
        if (getRawName().data() == o.getRawName().data()) return false;
        return getRawName() > o.getRawName();
    }
    bool operator!=(TypeInfo const& o) const noexcept { return !(*this == o); }
    bool operator>=(TypeInfo const& o) const noexcept { return !(*this < o); }
    bool operator<=(TypeInfo const& o) const noexcept { return !(*this > o); }
    /// \}

    /// \brief Computes and returns a hash value for this \ref TypeInfo.
    ///
    /// Used to make \ref TypeInfo and \ref TypeId usable in unordered
    /// containers.
    AMINO_CORE_SHARED_DECL size_t computeHash() const noexcept;

private:
    friend RuntimeTypeInfo;
    friend TypeInfoDetails;

    /*----- types -----*/

    enum class Kind : uint8_t {};
    enum class Category : uint8_t { eOther, eEnum, ePtr };

    /// \brief Helper struct use by static_assert in templates specializations
    /// meant to always fail.
    template <typename T>
    struct Fail : public std::false_type {};

    /// \brief Traits to extract the fields to construct a TypeInfo for a given
    /// type.
    /// \{
    template <typename T, Category Cat, uint32_t Nesting>
    struct Traits {
        using type = T;
        /// \brief Get the type name of the type `T` (using rtti).
        ///
        /// \note We use `typeid(T*)` rather than `typeid(T)` to enable uses
        /// of \ref TypeInfo on forward declared types. This is necessary to
        /// capture \ref TypeInfo for `Amino::Ptr<T>` where `T` is forward
        /// declared.
        static StringView name() {
#if !AMINO_INTERNAL_OPTION_HAS_RTTI
            constexpr bool isRttiEnabled = Fail<T>::value;
            static_assert(isRttiEnabled, "Can't use TypeInfo without rtti!");
            AMINO_INTERNAL_UNREACHABLE("Can't be instantiated");
#elif AMINO_INTERNAL_PLATFORM_IS_WINDOWS
            char const* v = typeid(T*).raw_name(); // LCOV_EXCL_BR_LINE
            assert(v);
            assert(v[0] == '.' && v[1] == 'P' && v[2] == 'E' && v[3] == 'A');
            return {v + 4, std::strlen(v + 4)}; // drop the front '.PEA'
#else
            char const* v = typeid(T*).name(); // LCOV_EXCL_BR_LINE
            assert(v && v[0] == 'P');
            return {v + 1, std::strlen(v + 1)}; // drop the front 'P'
#endif
        }
        static constexpr Category category = Cat;
        static constexpr uint32_t nesting  = Nesting;
    };

    template <typename T>
    struct GetTraits;
    template <typename T>
    using GetTraits_t = typename GetTraits<T>::type;

    template <typename T>
    struct GetTraits {
        static constexpr auto category =
            std::is_enum<T>::value ? Category::eEnum : Category::eOther;
        using type = Traits<T, category, 0>;
    };
    template <typename T>
    struct GetTraits<Ptr<T>> {
        using type = Traits<T, Category::ePtr, 0>;
    };
    template <typename T>
    struct GetTraits<Ptr<Array<T>>> {
        using TT   = GetTraits_t<T>;
        using type = Traits<typename TT::type, TT::category, TT::nesting + 1>;
    };
    template <typename T>
    struct GetTraits<Array<T>> {
        static_assert(
            Fail<T>::value,
            "Bad TypeInfo usage! "
            "Amino::Array should always be managed by Amino::Ptr!");
    };
    /// \}

    /// \brief Helper struct to get the singleton static \ref TypeInfo instance
    /// for a given type.
    template <typename T>
    struct GetInstance {
        static_assert(
            std::is_same<T, std::remove_cv_t<T>>::value,
            "Should have removed const/volatile qualifiers!");
        static_assert(
            std::alignment_of<T>::value != 0,
            "T must be complete, it can't be forward declared only.");
        static TypeInfo const s_instance;
    };

    /*----- member functions -----*/

    template <typename T, Category Cat, uint32_t Nesting>
    explicit TypeInfo(Traits<T, Cat, Nesting>) noexcept
        : m_rawname(Traits<T, Cat, Nesting>::name()),
          m_kind{static_cast<Kind>(0)},
          m_category(Cat),
          m_nesting(Nesting) {}

    /// \brief Constructor.
    constexpr TypeInfo(
        StringView name,
        Kind       kind,
        Category   category,
        uint32_t   nesting) noexcept
        : m_rawname(name),
          m_kind(kind),
          m_category(category),
          m_nesting(nesting) {}

    /// \brief Get the raw name of the type `T` of this \ref TypeInfo.
    StringView getRawName() const noexcept {
        assert(m_rawname.data());
        return m_rawname;
    }

    /// \brief Get the kind of this TypeInfo instance.
    ///
    /// See \ref RuntimeTypeInfo for details.
    Kind getKind() const noexcept { return m_kind; }

    /// \brief Whether the type `T` of this \ref TypeInfo was wrapped in an
    /// \ref Amino::Ptr, or is an enum, or none of the above.
    Category getCategory() const noexcept { return m_category; }

    /// \brief Returns the array dimension of the type `T` of this \ref TypeInfo
    ///
    /// For example, given a non \ref Amino::Array type `U`, then the nesting
    /// for `T` corresponds to:
    ///   - 0 if `T` = `U`
    ///   - 1 if `T` = `Ptr<Array<U>>`
    ///   - 2 if `T` = `Ptr<Array<Ptr<Array<U>>>`
    ///   - etc.
    uint32_t getNesting() const noexcept { return m_nesting; }

    /// \brief Whether this is a \ref RuntimeTypeInfo or not.
    bool isRuntime() const noexcept { return m_kind != static_cast<Kind>(0); }

    /*----- data members -----*/

    /// \brief The RTTI type name of the type `T` of this \ref TypeInfo.
    StringView m_rawname;

    /// \copydoc getKind
    Kind m_kind;

    /// \copydoc getCategory
    Category m_category;

    /// \copydoc getNesting
    uint32_t m_nesting;

    /*----- static data members -----*/

    /// \brief Singleton instance for TypeInfo of void.
    AMINO_CORE_SHARED_DECL static TypeInfo const s_void;
};

//------------------------------------------------------------------------------
//
static_assert(
    sizeof(TypeInfo) == sizeof(void*) * 3,
    "TypeInfo should be 3 times the size of a pointer.");
static_assert(
    alignof(TypeInfo) == alignof(void*),
    "TypeInfo should have the same alignment than a pointer.");

//------------------------------------------------------------------------------
//
template <typename T>
TypeInfo const TypeInfo::GetInstance<T>::s_instance{GetTraits_t<T>{}};

//------------------------------------------------------------------------------
//
template <>
inline TypeInfo const& TypeInfo::get<void>() noexcept {
    return s_void;
}

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

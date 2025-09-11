//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_TYPE_ID_H
#define AMINO_CORE_TYPE_ID_H

/// \file  TypeId.h
/// \brief Type identifier for types.

#include "internal/TypeInfo.h"

//==============================================================================
// NAMESPACE Amino
//==============================================================================

namespace Amino {

//==============================================================================
// FORWARD DECLARATIONS
//==============================================================================

class TypeId;

/// \brief Returns the \ref TypeId for the given Type.
template <typename T>
TypeId getTypeId() noexcept;

//==============================================================================
// CLASS TypeId
//==============================================================================

/// \brief Type identifier for a type.
///
/// Allows comparing types by their identifiers.
/// Used by \ref Any to identify its payload type.
///
/// See \ref getTypeId.
class TypeId {
public:
    /*----- member functions -----*/

    /// \brief Can't default construct a TypeId.
    TypeId() = delete;

    /// \brief Computes a hash for this TypeId.
    ///
    /// \warning This compute hash member functions is only meant to enable the
    /// use of \ref Amino::TypeId in unordered containers. The hashing itself is
    /// arbitrary and subject to change. The computed hash may also differ
    /// between different compilers and platforms.
    size_t computeHash() const { return info().computeHash(); }

    /// \brief TypeId's equality comparison operators.
    /// \{
    bool operator==(TypeId o) const noexcept { return info() == o.info(); }
    bool operator!=(TypeId o) const noexcept { return info() != o.info(); }
    /// \}

    /// \brief TypeId's ordering comparison operators, to allow storing \ref
    /// TypeId in ordered containers (ONLY!).
    ///
    /// \warning The ordering comparison operators are ONLY meant to allow
    /// storing \ref TypeId in ordered container. The ordering itself is
    /// arbitrary and subject to changes. The ordering may also differ between
    /// different compilers and platforms.
    ///
    /// \{
    // clang-format off
    bool operator< (TypeId o) const noexcept { return info() <  o.info(); }
    bool operator<=(TypeId o) const noexcept { return info() <= o.info(); }
    bool operator> (TypeId o) const noexcept { return info() >  o.info(); }
    bool operator>=(TypeId o) const noexcept { return info() >= o.info(); }
    // clang-format on
    /// \}

private:
    /// \cond AMINO_INTERNAL_DOCS

    /*----- friend declarations -----*/

    template <typename T>
    friend TypeId getTypeId() noexcept;
    friend ::Amino::Internal::TypeInfoDetails;

    /*----- static member functions -----*/

    /// \brief Implementation of \ref Amino::getTypeId
    template <typename T>
    static TypeId get() noexcept;

    /*----- member functions -----*/

    /// \brief Constructs a invalid (nullptr) TypeId.
    ///
    /// See \ref Amino::getTypeId<Internal::NullTypeInfo>()
    explicit constexpr TypeId(std::nullptr_t) : m_info(nullptr) {}

    /// \brief Constructs a TypeId corresponding the the given \ref
    /// Internal::TypeInfo.
    explicit constexpr TypeId(Internal::TypeInfo const* info) : m_info(info) {
        assert(info);
    }

    /// \brief Get the \ref Internal::TypeInfo of this \ref TypeId.
    Internal::TypeInfo const& info() const {
        assert(m_info);
        return *m_info;
    }

    /*----- data members -----*/

    /// \brief Private implementation.
    Internal::TypeInfo const* m_info = nullptr;

    /// \endcond
};

//------------------------------------------------------------------------------
//
static_assert(
    sizeof(TypeId) == sizeof(void*), "TypeId must be the size of a pointer.");
static_assert(
    alignof(TypeId) == alignof(void*), "TypeId must be aligned like pointer.");

//------------------------------------------------------------------------------
//
/// \cond AMINO_INTERNAL_DOCS
template <typename T>
TypeId TypeId::get() noexcept {
#if AMINO_INTERNAL_OPTION_HAS_RTTI
    return TypeId(&Internal::TypeInfo::get<T>());
#else
    // If no RTTI, fail at compile time, not link time.
    // It's ok to use Amino::TypeId without RTTI, but not ok to create them.
    // This isRttiEnabled will always be false if this function is instantiated,
    // but the dummy expression must depend on the template type T, otherwise
    // the static_assert will fail even if the function isn't instantiated.
    constexpr bool isRttiEnabled = (alignof(T) == -42); // always false
    static_assert(isRttiEnabled, "Can't use getTypeId() without rtti enabled!");
    AMINO_INTERNAL_UNREACHABLE("Can't be instantiated");
#endif
}
/// \brief Get the TypeId for `void`.
///
/// This specialization useful to allow using void \ref TypeId even when
/// compiling modules without RTTI enabled (not all aspects of \ref TypeId
/// require RTTI, only the "capture" of a TypeId for a type `T` does).
template <>
inline TypeId TypeId::get<void>() noexcept {
    return TypeId(&Internal::TypeInfo::get<void>());
}
/// \endcond

//==============================================================================
// FUNCTION getTypeId<T>()
//==============================================================================

//------------------------------------------------------------------------------
//
template <typename T>
TypeId getTypeId() noexcept {
    return TypeId::get<T>();
}

/// \cond AMINO_INTERNAL_DOCS
/// \brief Special case to create a null TypeId
template <>
inline constexpr TypeId getTypeId<Internal::NullTypeInfo>() noexcept {
    return TypeId(nullptr);
}
/// \endcond

} // namespace Amino

#endif

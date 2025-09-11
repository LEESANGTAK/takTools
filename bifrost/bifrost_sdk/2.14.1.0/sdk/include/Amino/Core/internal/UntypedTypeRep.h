//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_UNTYPED_TYPE_REP_H
#define AMINO_CORE_INTERNAL_UNTYPED_TYPE_REP_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  UntypedTypeRep.h
/// \brief Amino untyped representation of a type.

#include "../CoreExport.h"

#include "TypeTraits.h"

#include <cassert>
#include <cstddef>
#include <cstring>

namespace Amino {
namespace Internal {

//==============================================================================
// CLASS UntypedTypeRep
//==============================================================================

/// \brief Untyped representation of a data type.
///
/// This is used by the jitted code to perform memory allocation, deallocation,
/// copy construction and destruction of type erased values. Those values can be
/// either Ptr, Any, native types, POD structs, Non-POD structs (containing
/// Ptr and/or Any).
///
// NOLINTNEXTLINE(cppcoreguidelines-pro-type-union-access)
class UntypedTypeRep {
public:
    /*----- types -----*/

    /// \brief The type of the value type size.
    using size_type = TypeTraits::size_type;

    /// \brief The type of the value type alignment.
    using align_type = TypeTraits::align_type;

public:
    /*----- member functions -----*/

    /// \brief Allocate a block of memory with a size large enough to hold \p n
    /// elements of value size \p m_value_type_size.
    ///
    /// \param n The number of elements to be allocated.
    ///
    /// \return Pointer to the beginning of the allocated block of memory.
    AMINO_CORE_SHARED_DECL void* allocate(size_t n) const;

    /// \brief Release a block of memory previously allocated with the
    /// member function \p allocate.
    ///
    /// \param p Pointer to a block of storage previously allocated with \p
    /// allocate.
    ///
    /// \note The argument \p n is ignored.
    AMINO_CORE_SHARED_DECL void deallocate(void* p, size_t /*n*/) const;

    /// \brief Get the traits of the type this \ref UntypedTypeRep represents
    constexpr TypeTraits const& get_traits() const noexcept { return m_traits; }

    /// \brief Get the size of the type this \ref UntypedTypeRep represents
    constexpr size_type get_sizeof() const noexcept {
        return get_traits().get_sizeof();
    }

    /// \brief Get the alignment of the type this \ref UntypedTypeRep represents
    constexpr align_type get_alignof() const noexcept {
        return get_traits().get_alignof();
    }

protected:
    /*----- types -----*/

    /// \brief Operation ID used to identify the operation to perform for \ref
    /// StructHandler.
    enum class OpID : int {
        eDefaultConstruct,
        eFillConstruct,
        eCopyConstruct,
        eMoveConstruct,
        eCopyAssign,
        eMoveAssign,
        eDestroy
    };

    /// \brief Handler for types with \ref TypeCategory::eCtStruct.
    using StructHandler = //
        void (*)(OpID id, void* dst, void const* src, size_t n);
    using DefaultHandler = void (*)(void* dst);
    using RuntimeHandler = void const*;

    /*----- member functions -----*/

    /// \brief Construct an UntypedTypeRep with the traits and data.
    /// \{
    // NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init)
    constexpr UntypedTypeRep(TypeTraits traits, StructHandler data) noexcept
        : m_traits(traits), m_struct(data) {
        assert(traits.get_category() == TypeCategory::eCtStruct);
    }

    // NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init)
    constexpr UntypedTypeRep(TypeTraits traits, DefaultHandler data) noexcept
        : m_traits(traits), m_default(data) {
        assert(traits.get_category() == TypeCategory::eCtPtr);
    }

    // NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init)
    constexpr UntypedTypeRep(TypeTraits traits, RuntimeHandler data) noexcept
        : m_traits(traits), m_runtime(data) {
        assert(traits.is_runtime());
    }
    /// \}

    /// \brief Construct an UntypedTypeRep with the traits and no runtime data.
    // NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init)
    constexpr explicit UntypedTypeRep(
        TypeTraits traits, std::nullptr_t = nullptr) noexcept
        : m_traits(traits), m_runtime(nullptr) {
        assert(
            get_traits().is_runtime() ||
            !get_traits().is_default_constructible());
    }

    /// \brief Get the handler for the struct type this \ref UntypedTypeRep
    /// represents.
    ///
    /// \pre `get_traits().get_category() == TypeCategory::eCtStruct`
    constexpr StructHandler get_struct_handler() const noexcept {
        assert(get_traits().get_category() == TypeCategory::eCtStruct);
        // NOLINTNEXTLINE(cppcoreguidelines-pro-type-union-access)
        return m_struct;
    }

    /// \brief Get the handler for the Ptr managed type this \ref UntypedTypeRep
    /// represents.
    ///
    /// \pre `get_traits().get_category() == TypeCategory::eCtPtr`
    constexpr DefaultHandler get_default_handler() const noexcept {
        assert(get_traits().get_category() == TypeCategory::eCtPtr);
        // NOLINTNEXTLINE(cppcoreguidelines-pro-type-union-access)
        return m_default;
    }

    /// \brief Get the handler for the runtime type this \ref UntypedTypeRep
    /// represents.
    ///
    /// \pre `get_traits().is_runtime()`
    constexpr RuntimeHandler get_runtime_handler() const noexcept {
        assert(get_traits().is_runtime());
        // NOLINTNEXTLINE(cppcoreguidelines-pro-type-union-access)
        return m_runtime;
    }

private:
    /*----- data members -----*/

    /// \brief The traits of the type this \ref UntypedTypeRep represents
    TypeTraits m_traits;

    // Home-grown variant, because we can't use std::variant/boost::variant
    // for ABI compatibility.
    union {
        /// \brief Handler for types with \ref TypeCategory::eCtStruct category.
        StructHandler m_struct;

        /// \brief Handler for types with \ref TypeCategory::eCtPtr category.
        DefaultHandler m_default;

        /// \brief Handler for types such that \ref TypeTraits::is_runtime.
        RuntimeHandler m_runtime;
    };
};

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_TYPE_TRAITS_H
#define AMINO_CORE_INTERNAL_TYPE_TRAITS_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  TypeTraits.h
/// \brief Structs to describe the properties of a type.

#include <cstdint>
#include <type_traits>

//==============================================================================
// NAMESPACE Amino::Internal
//==============================================================================

namespace Amino {
namespace Internal {

//==============================================================================
// CLASS TypeCategory
//==============================================================================

/// \brief The category of a type.
///
/// Use to know how to apply type erased operations on values.
enum class TypeCategory : uint16_t {
    /// \brief Trivial type.
    ///
    /// Such types don't need to provide extra handler to \ref UntypedTypeRep.
    ePod,

    /// \brief \ref Amino::String type.
    ///
    /// Such types don't need to provide extra handler to \ref UntypedTypeRep.
    eStr,

    /// \brief \ref Amino::Any type.
    ///
    /// Such types don't need to provide extra handler to \ref UntypedTypeRep.
    eAny,

    /// \brief Runtime struct with zero constructible members.
    ///
    /// Type are zero-constructible if they can be zero-initialized and contain
    /// no null \ref Ptr (i.e. setting all the bytes to 0 yields a default
    /// constructed value (for types supported in Amino graphs)).
    ///
    /// Such types need to provide information for all their members to
    /// \ref UntypedTypeRep.
    eStructZero,

    /// \brief Runtime struct with non-zero constructible members.
    ///
    /// Same as \ref eStructZero but some members are not zero constructible.
    eStruct,

    /// \brief Runtime class (type-erased classes).
    ///
    /// Such type need to provide a function pointer to get the static Ptr
    /// pointer to the default value for that user class type.
    /// (see \ref UntypedClassTypeRep).
    eClass,

    /// \brief Runtime array (type-erased arrays).
    ///
    /// Such type need to provide the \ref UntypedTypeRep of its element type.
    /// (see \ref UntypedArrayTypeRep).
    eArray,

    ///< Compile time Ptr managed class/array.
    ///
    /// Such type need to provide a handler function to \ref UntypedTypeRep
    /// to perform a placement new constructing a non-null ptr.
    /// (see \ref UntypedTypeRep::DefaultHandler and \ref UntypedTypeRepT).
    eCtPtr,

    /// \brief Compile time non-pod struct.
    ///
    /// Such type need to provide a handler function to \ref UntypedTypeRep
    /// to perform operation (construct/copy/move/destroy) on such type.
    /// (see \ref UntypedTypeRep::StructHandler and \ref UntypedTypeRepT).
    eCtStruct,

    /// \brief Non-default constructible.
    ///
    /// Such types can't be default constructed in Amino graphs.
    eNonDefaultConstructible,

    /// \brief Uninstantiable / invalid (can't be instantiated in Amino graphs).
    eUninstantiable
};

//==============================================================================
// CLASS TypeTraits
//==============================================================================

/// \brief Structs to describe the properties of a type.
///
/// \note Used by \ref UntypedTypeRep and type-erased operations.
struct TypeTraits {
    /*----- types -----*/

    /// \brief The type of the type size member.
    using size_type = uint32_t;

    /// \brief The type of the type alignment member.
    using align_type = uint16_t;

    /*----- member functions -----*/

    /// \brief Equality comparison
    /// \{
    constexpr bool operator==(TypeTraits o) const noexcept {
        return m_size == o.m_size && m_align == o.m_align &&
               m_category == o.m_category;
    }
    constexpr bool operator!=(TypeTraits o) const noexcept {
        return !(*this == o);
    }
    /// \}

    /// \brief The size in bytes of the type.
    constexpr auto get_sizeof() const noexcept { return m_size; }

    /// \brief The alignment in bytes of the type.
    constexpr auto get_alignof() const noexcept { return m_align; }

    /// \brief The type category of the type.
    constexpr auto get_category() const noexcept { return m_category; }

    /// \brief Return whether the type is trivial or not.
    constexpr bool is_trivial() const noexcept {
        return m_category == TypeCategory::ePod;
    }

    /// \brief Return whether the type is zero constructible or not.
    constexpr bool is_zero_constructible() const noexcept {
        return m_category <= TypeCategory::eStructZero;
    }

    /// \brief Return whether the type is default constructible or not.
    constexpr bool is_default_constructible() const noexcept {
        return m_category < TypeCategory::eNonDefaultConstructible;
    }

    /// \brief Return whether or not the type is runtime.
    ///
    /// Such types correspond to \ref UntypedTypeRep with a \ref
    /// UntypedTypeRep::RuntimeHandler (even though it can be null).
    constexpr bool is_runtime() const noexcept {
        return m_category <= TypeCategory::eArray;
    }

    /// \brief Return whether the type is supported or not.
    ///
    /// \warning Without reflections in C++, we can't be 100% sure that the
    /// type really is supported in a Amino graph. But this tells us if a type
    /// satisfy the minimal requirements to be used in an Amino graph.
    constexpr bool is_supported() const noexcept {
        return m_category < TypeCategory::eNonDefaultConstructible;
    }

    /// \brief Return whether the type is instantiable or not.
    constexpr bool is_instantiable() const noexcept {
        return m_category != TypeCategory::eUninstantiable;
    }

    /// \brief The size in bytes of the type.
    size_type m_size = 0;

    /// \brief The alignment in bytes of the type.
    align_type m_align = 0;

    /// \brief The type category of the type.
    TypeCategory m_category = TypeCategory::eUninstantiable;
};

//------------------------------------------------------------------------------
//
template <typename T>
struct GetTypeCategory {
    static_assert(std::alignment_of<T>::value != 0, "Must be complete type");
    static constexpr auto value =
        std::is_trivial<T>::value ? TypeCategory::ePod
        : (std::is_default_constructible<T>::value && //
           std::is_copy_constructible<T>::value &&    //
           std::is_move_constructible<T>::value &&    //
           std::is_copy_assignable<T>::value &&       //
           std::is_move_assignable<T>::value &&       //
           std::is_destructible<T>::value)
            ? TypeCategory::eCtStruct
            : TypeCategory::eUninstantiable;
};

//------------------------------------------------------------------------------
//
template <typename T>
constexpr TypeTraits getTypeTraits() {
    return {sizeof(T), std::alignment_of<T>::value, GetTypeCategory<T>::value};
};

//------------------------------------------------------------------------------
//
static_assert(std::has_unique_object_representations<TypeTraits>::value);

template <typename T>
static inline constexpr TypeCategory TypeCategory_v = GetTypeCategory<T>::value;

template <typename T>
static inline constexpr TypeTraits TypeTraits_v = getTypeTraits<T>();

} // namespace Internal
} // namespace Amino
/// \endcond

#endif // AMINO_ALLOCATOR_IMPL_H

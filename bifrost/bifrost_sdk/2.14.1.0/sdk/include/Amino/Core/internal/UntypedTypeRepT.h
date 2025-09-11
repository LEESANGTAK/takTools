//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_UNTYPED_TYPE_REP_T_H
#define AMINO_CORE_INTERNAL_UNTYPED_TYPE_REP_T_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  UntypedTypeRepT.h
/// \brief Amino untyped representation for a concrete type T.

#include "UntypedTypeRep.h"

#include <cstddef>
#include <cstring>
#include <utility>

namespace Amino {

// Forward declarations.
struct PtrDefaultFlag;

namespace Internal {

//==============================================================================
// CLASS UntypedTypeRepCompile
//==============================================================================

/// \brief Base class of \ref UntypedTypeRepT bellow.
///
/// Used to help providing traits and compile data for type `T`.
class UntypedTypeRepCompile : public UntypedTypeRep {
protected:
    /*----- types -----*/

    /// \brief Similar to std::type_identity, used by derived class \ref
    /// UntypedTypeRepT.
    template <typename T>
    struct type_identity {};

    /*----- member functions -----*/

    /// \brief Construct an \ref UntypedTypeRep representing the given type `T`.
    template <typename T>
    constexpr explicit UntypedTypeRepCompile(type_identity<T>) noexcept
        : UntypedTypeRep(getTypeTraits<T>(), GetHandler<T>::value) {}

private:
    /*----- static member functions -----*/

    /// \brief Handler for types with category \ref TypeCategory::eCtStruct.
    ///
    /// This handler needs to provide implementations for all operations.
    template <typename T>
    static void struct_handler(OpID id, void* dst_, void const* src_, size_t n);

    /// \brief Handler for types with category \ref TypeCategory::eCtPtr.
    ///
    /// This handler only needs to provide implementation to placement new
    /// the `Ptr<U>` with the default value for `U`.
    template <typename T>
    static void default_handler(void* dst);

    /*----- types -----*/

    /// \brief Traits to get the compile data (apply function) for T.
    /// \{
    template <typename T, TypeCategory Category = GetTypeCategory<T>::value>
    struct GetHandler {
        static constexpr std::nullptr_t value = nullptr;
    };
    template <typename T>
    struct GetHandler<T, TypeCategory::eCtPtr> {
        static constexpr DefaultHandler value = default_handler<T>;
    };
    template <typename T>
    struct GetHandler<T, TypeCategory::eCtStruct> {
        static constexpr StructHandler value = struct_handler<T>;
    };
    /// \}

    /// \brief Trick to get the type `Type` but only when we need to do
    /// something with `T`.
    ///
    /// \note Used by \ref default_handler
    template <typename T, typename Type>
    struct Second {
        using type = Type;
    };
};

//==============================================================================
// CLASS UntypedTypeRepT<T>
//==============================================================================

/// \brief Untyped representation corresponding to the type `T`.
template <typename T>
class UntypedTypeRepT : public UntypedTypeRepCompile {
private:
    static_assert(
        std::is_same<std::remove_cv_t<T>, T>::value,
        "UntypedTypeRepT must have a non-const, non-volatile value_type");

public:
    /*----- member functions -----*/

    /// \brief Constructor.
    constexpr UntypedTypeRepT() noexcept
        : UntypedTypeRepCompile{type_identity<T>{}} {
        static_assert(
            sizeof(UntypedTypeRepT) == sizeof(UntypedTypeRep),
            "Must be binary compatible with UntypedTypeRep!");
    }

    /// \brief Allocate a block of memory with a size large enough to hold \p n
    /// elements of type \p value_type.
    ///
    /// \param n The number of elements to be allocated.
    ///
    /// \return Pointer to the beginning of the allocated block of memory.
    T* allocate(size_t n) const {
        return static_cast<T*>(UntypedTypeRepCompile::allocate(n));
    }

    /// \brief Release a block of memory previously allocated with the member
    /// function \p allocate.
    ///
    /// The elements in the array are not destroyed by this call.
    ///
    /// \param p Pointer to a block of storage previously allocated with \p
    /// allocate.
    ///
    /// \param n The number of elements originally allocated by \p allocate.
    ///
    /// \note The argument \p n is ignored.
    void deallocate(T* p, size_t n) const {
        UntypedTypeRepCompile::deallocate(p, n);
    }

    /// \brief Construct an element on the location pointed by \p p.
    ///
    /// This call does not allocate the memory storage for the element. The
    /// storage should already be available at \p p. This call constructs an
    /// instance of type \p value_type using the given arguments.
    ///
    /// \param p Pointer to a location with enough storage space to contain an
    /// element of type \p value_type.
    ///
    /// \param args The arguments to be passed to the constructor.
    ///
    /// \see allocate
    template <typename... Args>
    void construct(T* p, Args&&... args) const {
        ::new (p) T(std::forward<Args>(args)...);
    }

    /// \brief Copy assign an element on the location pointed by \p p.
    ///
    /// \param p Pointer to a valid assignable value of type \p value_type.
    ///
    /// \param value the value to assign to the element.
    ///
    void assign(T* p, T const& value) const { *p = value; }

    /// \brief Move assign an element on the location pointed by \p p.
    ///
    /// \param p Pointer to a valid assignable value of type \p value_type.
    ///
    /// \param value the value to assign to the element.
    ///
    void assign(T* p, T&& value) const { *p = std::move(value); }

    /// \brief Destroy (in-place) the object pointed by \p p.
    ///
    /// This call does not deallocate the memory storage for the element.
    ///
    /// \param p Pointer to the element to be destroyed.
    ///
    /// \see deallocate.
    void destroy(T* p) const { p->~T(); }

    /// \brief Get the maximum number of elements of type \p value_type that
    /// could be allocated by an \p allocate call.
    ///
    /// \return The maximum number of elements that could be allocated.
    constexpr static size_t max_size() noexcept {
        return ~size_t{} / sizeof(T);
    }
};

//------------------------------------------------------------------------------
//
template <typename T>
void UntypedTypeRepCompile::struct_handler(
    OpID id, void* dst_, void const* src_, size_t n) {
    static_assert(!std::is_trivial<T>::value, "Should not need to instantiate");
    static_assert(
        GetTypeCategory<T>::value == TypeCategory::eCtStruct,
        "Should be instantiated for struct only!");
    constexpr auto rep = UntypedTypeRepT<T>{};

    T*       dst = static_cast<T*>(dst_);
    T* const end = dst + n;
    switch (id) {
        case OpID::eDefaultConstruct: {
            for (; dst != end; ++dst) rep.construct(dst);
        } break;
        case OpID::eFillConstruct: {
            T const* const src = static_cast<T const*>(src_);
            for (; dst != end; ++dst) rep.construct(dst, *src);
        } break;
        case OpID::eCopyConstruct: {
            T const* src = static_cast<T const*>(src_);
            for (; dst != end; ++dst, ++src) rep.construct(dst, *src);
        } break;
        case OpID::eMoveConstruct: {
            T* src = const_cast<T*>(static_cast<T const*>(src_));
            for (; dst != end; ++dst, ++src)
                rep.construct(dst, std::move(*src));
        } break;
        case OpID::eCopyAssign: {
            T const* src = static_cast<T const*>(src_);
            for (; dst != end; ++dst, ++src) rep.assign(dst, *src);
        } break;
        case OpID::eMoveAssign: {
            T* src = const_cast<T*>(static_cast<T const*>(src_));
            for (; dst != end; ++dst, ++src) rep.assign(dst, std::move(*src));
        } break;
        case OpID::eDestroy: {
            for (; dst != end; ++dst) rep.destroy(dst);
        } break;
    }
}

//------------------------------------------------------------------------------
//
template <typename T>
void UntypedTypeRepCompile::default_handler(void* dst) {
    static_assert(
        GetTypeCategory<T>::value == TypeCategory::eCtPtr,
        "Should be instantiated for Ptr only!");
    new (dst) T{typename Second<T, PtrDefaultFlag>::type{}};
}

//------------------------------------------------------------------------------
//
template <typename T>
static inline constexpr UntypedTypeRep UntypedTypeRep_v{UntypedTypeRepT<T>{}};

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file  Any.h
///
/// \brief A generic value object
///
/// \see Amino::Any

#ifndef AMINO_ANY_H
#define AMINO_ANY_H

//==============================================================================
// EXTERNAL DECLARATIONS
//==============================================================================

#include "internal/AnyImpl.h"

namespace Amino {
class StringView;

//==============================================================================
// CLASS AnyPayloadTraits
//==============================================================================

/// \brief Traits about the to-be-payload of an \ref Amino::Any.
///
/// This is used to check that a given type T can be used as the payload type of
/// an \ref Amino::Any. If not, an error will be emitted at compile time.
class AnyPayloadTraits {
private:
    /// \brief Whether the type T is an Amino::Array type or not.
    ///
    /// Any's should not set their payload to be an unmanaged Amino::Array,
    /// because such payload would never be extractable within an Amino graph.
    /// The payload has to be an Amino::Ptr<Amino::Array<T>> for it to be
    /// used within an Amino graph.
    /// \{
    template <typename T>
    struct is_amino_array : std::false_type {};
    template <typename T>
    struct is_amino_array<Amino::Array<T>> : std::true_type {};
    /// \}

    template <bool Bool>
    using bool_t = std::integral_constant<bool, Bool>;

public:
    /// \brief Whether a Any can be queried to extract its payload as type T.
    template <typename ValueType, typename T = std::decay_t<ValueType>>
    using is_cast_enabled = bool_t<(
        // The payload must not be an Any.
        !std::is_same<Any, T>::value &&

        // The payload should not be an Amino::Array directly.
        // Need to be wrapped in an Amino::Ptr (i.e. Ptr<Array<T>>).
        !is_amino_array<T>::value &&

        // Must not be Amino::StringView.
        // This is almost certainly a programming error since StringView
        // is not value semantics. Most likely need to store a String instead.
        !std::is_same<Amino::StringView, T>::value &&

        // Must not be raw pointer type.
        !std::is_pointer<T>::value &&

        // Must not be raw array type.
        !std::is_array<ValueType>::value &&
        !std::is_array<std::remove_reference_t<ValueType>>::value)>;

    /// \brief Whether a type T is a valid payload type.
    /// (i.e. can be assigned in an \ref Any).
    template <typename ValueType, typename T = std::decay_t<ValueType>>
    using is_valid = bool_t<(
        // The type must be queriable
        is_cast_enabled<ValueType>::value &&

        // Must be copy constructible (to allow copying
        // the Any with such payload).
        std::is_copy_constructible<T>::value &&

        // Must be standard layout.
        std::is_standard_layout<T>::value)>;

    /// \brief Enable if the type is a valid payload type.
    template <typename ValueType>
    using enable_if_valid = std::enable_if_t<is_valid<ValueType>::value>;

    /// \brief Enable if the type can be constructed from the given arguments.
    template <typename ValueType, typename... Args>
    using enable_if_constructible = std::enable_if_t<
        std::is_constructible<std::decay_t<ValueType>, Args...>::value>;
};

//==============================================================================
// CLASS Any
//==============================================================================

//------------------------------------------------------------------------------
/// \brief Generic value class that allows for storage of a value of any type.
///
/// \warning \ref Amino::Any is NOT a replacement for standard anys (like
/// std::any). It is only meant to be used within Amino graphs. Therefore
/// if a value never needs to flow directly into a graph, a standard any
/// (like std::any) should be used instead.
///
/// This follows the interface of std::any reasonably closely with the primary
/// difference being no exceptions being thrown -- in the case of an invalid
/// cast operation, a default value of the target type will be created and
/// returned. (This event - invalid_cast - may be logged). This has the
/// consequence, in contrast to std::any, that the payload type of \ref Any
/// must have a default constructor. An additional constraint vs std::any is
/// the constness requirements of the payload. Details of this are discussed in
/// the notes below.
///
/// Variables of type \ref Any are not completely unlimited in what they can
/// store; there are some minimal preconditions. A value stored in a variable
/// of type \ref Any must be copy-constructible. Therefore, it is not possible
/// for example to store a C array, since C arrays are not copy-constructible.
///
/// Unlike std::any, the internals of this class are well defined and known to
/// the Amino compiler, so that it can issue code to properly manipulate these
/// (correctly apply copy, move and destroy semantics) as they are passed into,
/// out from, and through the Amino graph.
///
/// \note As the Amino Graph execution model does not support C++ exceptions,
/// \ref Any should not be used to store objects that throw exceptions when
/// being constructed, copied, moved or deleted.
///
/// \note \ref Any has stricter alignment requirements than those satisfied by
/// default allocators for std containers (like std::vector). This is so that
/// SSE vectors can be stored in an \ref Any without performance penalties
/// from misalignment.
///
/// \note Objects that have overridden allocators (override operator new and
/// delete) must have those allocators public if they are to be stored in an
/// \ref Any.
///
/// \note In the Amino system, \ref Array is intended to be managed via
/// \ref Ptr -- to enforce this, their allocators are overridden and not part
/// of the public interface, and as a result you will not be able to store an
/// "unwrapped" \ref Array in \ref Any -- you will need to wrap them in an
/// \ref Ptr before storing in an \ref Any
///
/// For example for an 'elem_count' array of T stored in an \ref Any named
/// 'anyArray', you could use a statement like this;
///
/// \code {.cpp}
/// \ref Any anyArray(Amino::newClassPtr<Amino::Array<T>>(elem_count));
/// \endcode
///
/// To retrieve the Ptr to the Array stored in an \ref Any;
///
/// \code {.cpp}
/// auto arrayPtr = Amino::any_cast<Amino::Ptr<Amino::Array<T>>>(anyArray);
/// \endcode
///
/// \warning \ref Any does not reference count its payload or attempt any
/// optimizations like copy-on-write. When you copy an \ref Any, the payload
/// is copied immediately. In Amino, the means for getting copy-on-write
/// behaviour is to use \ref Ptr. If you want reference counted, copy-on-write
/// behaviour, and the genericity of \ref Any, you can store a \ref Ptr as the
/// payload of an \ref Any -- then you get the best of both worlds.
///
/// \note For the purposes of RTTI, Amino::Any discards const and volatile
/// type qualifiers on the payload type when storing/extracting payloads in
/// \ref Any instances.
///
/// \note There are five ways to extract the payload of an \ref Any (see \ref
/// any_cast). They either return a value of the payload type or a
/// pointer (const if the Any is const) to the payload of the Any.
///
class Any : private Internal::AnyImpl::AnyUntyped {
    using Base   = Internal::AnyImpl::AnyUntyped;
    using Traits = AnyPayloadTraits;

public:
    /// \brief Default constructor
    ///
    /// Constructs an empty \ref Any.
    ///
    /// \post `has_value() == false`
    Any() noexcept = default;

    /// \brief Copy constructor
    ///
    /// Constructs an \ref Any object as a copy of another \ref Any. A copy of
    /// the payload of \p other will be contained in this Any.
    ///
    /// \post `has_value() == other.has_value()`
    ///
    /// \param other The \ref Any to copy construct this \ref Any from.
    Any(Any const& other) = default;

    /// \brief Move constructor
    ///
    /// Constructs an \ref Any object by moving the contents of another
    /// \ref Any into this instance.
    ///
    /// \post `other.has_value() == false`
    Any(Any&& other) noexcept = default;

    /// \brief Move constructor
    ///
    /// Constructs an \ref Any object from something that is not also an
    /// \ref Any. This will move the object into this instance of \ref Any
    /// as its payload.
    ///
    /// \note Used only if \p v is not an \ref Any.
    ///
    /// \tparam ValueType The payload type
    /// \param v The value this \ref Any will contain.
    template <typename ValueType, typename = Traits::enable_if_valid<ValueType>>
    explicit Any(ValueType&& v) noexcept : Base(std::forward<ValueType>(v)) {}

    /// \brief Destructor
    ///
    /// Destroys the payload, if any (using reset)
    ~Any() = default;

    /// \brief Copy assignment operator.
    ///
    /// The payload of \p rhs will be copied and the copy will be assigned to
    /// this \ref Any.
    Any& operator=(Any const& rhs) = default;

    /// \brief Move assignment operator.
    ///
    /// The payload of \p rhs will be stolen from \p rhs and assigned to
    /// this \ref Any.
    ///
    /// \post `rhs.has_value() == false`
    ///
    /// \param rhs The \ref Any to move assign to this \ref Any.
    Any& operator=(Any&& rhs) noexcept = default;

    /// \brief Move assignment conversion.
    ///
    /// \note Used only if \p rhs is not an \ref Any (or anything that
    /// decays into an \ref Any) and is a valid payload type (see \ref Any for
    /// details about constraints on payload types).
    ///
    /// \tparam ValueType The payload type
    /// \param rhs The value to assign to this \ref Any
    template <typename ValueType, typename = Traits::enable_if_valid<ValueType>>
    Any& operator=(ValueType&& rhs) & noexcept {
        Any(std::forward<ValueType>(rhs)).swap(*this);
        return *this;
    }

    /// \brief Replaces the contained object of this \ref Any
    ///
    /// Changes the contained object to one of type `std::decay_t<ValueType>`
    /// constructed from the given arguments `Args`.
    ///
    /// First destroys the current contained object (if any) by `reset()`, then:
    /// constructs an object of type `std::decay_t<ValueType>`,
    /// direct-non-list-initialized from `std::forward<Args>(args)...`, as the
    /// contained object.
    ///
    /// This overload only participates in overload resolution if `ValueType`
    /// is a valid payload type to be stored in an \ref Any (see \ref Any for
    /// details about constraints on payload types) and is constructible from
    /// the given arguments \p args.
    template <
        typename ValueType,
        typename... Args,
        typename = Traits::enable_if_valid<ValueType>,
        typename = Traits::enable_if_constructible<ValueType, Args...>>
    void emplace(Args&&... args) noexcept {
        Base::emplace<ValueType>(std::forward<Args>(args)...);
    }

    /// \brief Replaces the contained object of this \ref Any
    ///
    /// Changes the contained object to one of type `std::decay_t<ValueType>`
    /// constructed from the given arguments `Args`.
    ///
    /// First destroys the current contained object (if any) by `reset()`, then:
    /// constructs an object of type std::decay_t<ValueType>,
    /// direct-non-list-initialized from \p il, `std::forward<Args>(args)...`,
    /// as the contained object.
    ///
    /// This overload only participates in overload resolution if `ValueType`
    /// is a valid payload type to be stored in an \ref Any (see \ref Any for
    /// details about constraints on payload types) and is constructible from
    /// the given initializer_list \p il and arguments \p args.
    template <
        typename ValueType,
        typename Up,
        typename... Args,
        typename IL = std::initializer_list<Up>,
        typename    = Traits::enable_if_valid<ValueType>,
        typename    = Traits::enable_if_constructible<ValueType, IL&, Args...>>
    void emplace(std::initializer_list<Up> il, Args&&... args) noexcept {
        Base::emplace<ValueType>(il, std::forward<Args>(args)...);
    }

    /// \brief Reset this \ref Any object
    ///
    /// Causes the contained object to be destroyed (if present).
    ///
    /// \post `has_value() == false`
    void reset() noexcept { Base::reset(); }

    /// \brief Swap payloads with another \ref Any object
    Any& swap(Any& rhs) noexcept {
        Base::swap(*this, rhs);
        return rhs;
    }

    /// \brief Return true if this \ref Any object contains a payload.
    bool has_value() const noexcept { return Base::has_value(); }

    AMINO_INTERNAL_DEPRECATED("Use any.type() == other.type() instead.")
    bool has_same_type(Any const& other) const noexcept {
        return type() == other.type();
    }

    /// \brief Returns the \ref TypeId of the value in this \ref Any, or the
    ///        \ref TypeId of `void` if this Any does not have a value.
    TypeId type() const noexcept { return Base::type(); }

private:
    /// \cond Doxygen_Suppress
    friend struct AnyArray;
    friend Internal::RuntimeAny;
    friend Internal::AnyCast;
    /// \endcond
};

//------------------------------------------------------------------------------
//
// enforce expected layout, size and alignment of Amino::Any
static_assert(
    std::is_standard_layout<Any>::value,
    "Amino::Any must be standard layout. ");
static_assert(
    sizeof(Any) == Internal::AnyTraits::sBufferSize + sizeof(void*),
    "Incorrect Amino::Any size");
static_assert(
    alignof(Any) == Internal::AnyTraits::sBufferAlign,
    "Incorrect Amino::Any alignment");

//==============================================================================
// NON MEMBER FUNCTIONS
//==============================================================================

//------------------------------------------------------------------------------
//
/// \brief Swap the payloads of two instances of \ref Any
inline void swap(Any& lhs, Any& rhs) noexcept { lhs.swap(rhs); }

//==============================================================================
// ANY CAST FUNCTIONS
//==============================================================================

//------------------------------------------------------------------------------
//
/// \brief Cast an instance of \ref Any to a payload type
///
/// If the requested type `ValueType` is the same as the payload type of the
/// \ref Any instance, a const pointer to the payload of the any will be
/// returned.
///
/// If the requested type `ValueType` is not the same as the payload type of the
/// \ref Any instance, a nullptr will be returned.
///
/// \tparam ValueType The payload type
/// \param  v         The instance of \ref Any to be casted to the ValueType
template <
    class ValueType,
    typename = std::enable_if_t<!std::is_same<void, ValueType>::value>>
inline std::add_pointer_t<std::add_const_t<ValueType>> any_cast(
    Any const* v) noexcept {
    static_assert(
        AnyPayloadTraits::is_cast_enabled<ValueType>::value,
        "ValueType must be a valid payload type");
    if (!v) return nullptr; // assert?
    return Internal::AnyCast::cast<ValueType>(v);
}

//------------------------------------------------------------------------------
//
/// \brief Cast an instance of \ref Any to a payload type
///
/// If the requested type `ValueType` is the same as the payload type of the
/// \ref Any instance, a pointer to the payload of the any will be returned.
///
/// If the requested type `ValueType` is not the same as the payload type of the
/// \ref Any instance, a nullptr will be returned.
///
/// \tparam ValueType The payload type
/// \param  v         The instance of \ref Any to be casted to the ValueType
template <
    class ValueType,
    typename = std::enable_if_t<!std::is_same<void, ValueType>::value>>
inline std::add_pointer_t<ValueType> any_cast(Any* v) noexcept {
    static_assert(
        AnyPayloadTraits::is_cast_enabled<ValueType>::value,
        "ValueType must be a valid payload type");
    if (!v) return nullptr; // assert?
    return Internal::AnyCast::cast<ValueType>(v);
}

//------------------------------------------------------------------------------
//
/// \brief Get the pointer the payload of the \ref Any as const void*.
///
/// This is a special syntax for extracting the raw payload of an \ref Any. If
/// the \ref Any has a value, a void pointer to the payload value is returned.
/// Otherwise, a nullptr will be returned. This can be used in cases where the
/// caller knows something about the payload (base class, memory layout, etc.),
/// but not the exact precise type.
///
/// This can also be useful if the payload is known to be a \ref Ptr but the
/// type of the pointee is unknown, and the caller just needs to get the type
/// erased `Ptr<void>`.
///
/// \warning Must be very carefull when dealing with type erased types. Recall
/// the static_cast from void pointer does not offset pointers like it does for
/// non-void types. This can lead to hard to debug bugs with wrong pointer
/// alignements for classes with multiple inheritance.
///
/// \param  v The instance of \ref Any to be casted to the ValueType
template <
    class ValueType,
    typename = std::enable_if_t<std::is_same<void, ValueType>::value>>
AMINO_INTERNAL_DEPRECATED("Use any_cast<ValueType> instead.")
inline void const* any_cast(Any const* v) noexcept {
    if (!v) return nullptr; // assert?
    return Internal::AnyCast::cast<void>(v);
}

//------------------------------------------------------------------------------
//
/// \brief Cast an instance of \ref Any to a payload type
///
/// If the requested type `ValueType` is the same as the payload type of the
/// \ref Any, then the returned value will be copy constructed from the payload
/// of the \ref Any.
///
/// If the requested type `ValueType` is not the same as the payload type of the
/// \ref Any instance, a default value of the requested type will be returned.
///
/// \tparam ValueType The payload type
/// \param  v         The instance of \ref Any to be casted to the ValueType
template <typename ValueType>
inline ValueType any_cast(Any const& v) noexcept {
    static_assert(
        AnyPayloadTraits::is_valid<ValueType>::value,
        "ValueType must be a valid payload type");
    using Tp = std::add_const_t<std::remove_reference_t<ValueType>>;
    Tp* tmp  = any_cast<Tp>(&v);
    return tmp ? *tmp : ValueType();
}

//------------------------------------------------------------------------------
//
/// \brief Cast an instance of \ref Any to a payload type.
///
/// If the requested type `ValueType` is the same as the payload type of the
/// \ref Any, then the returned value will be move constructed from the payload
/// of the \ref Any.
///
/// If the requested type `ValueType` is not the same as the payload type of the
/// \ref Any instance, a default value of the requested type will be returned.
///
/// In both cases, the rvalue \ref Any will be reset after this call (the \ref
/// Any argument is a sink argument).
///
/// \tparam ValueType The payload type
/// \param  v The instance of \ref Any to be casted to the `ValueType`
template <typename ValueType>
inline ValueType any_cast(Any&& v) noexcept {
    static_assert(
        AnyPayloadTraits::is_valid<ValueType>::value,
        "ValueType must be a valid payload type");
    using Tp = std::add_const_t<std::remove_reference_t<ValueType>>;
    Any any{std::move(v)};
    Tp* tmp = any_cast<Tp>(&any);
    return tmp ? std::move(*tmp) : ValueType();
}

} // namespace Amino

#endif

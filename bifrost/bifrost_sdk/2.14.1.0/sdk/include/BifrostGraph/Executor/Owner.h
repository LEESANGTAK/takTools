//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file Owner.h
/// \brief BifrostGraph Executor Owner helper class.
///
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_OWNER_H
#define BIFROSTGRAPH_EXECUTOR_OWNER_H

#include <BifrostGraph/Executor/internal/OwnerRep.h>
#include <BifrostGraph/Executor/internal/PointeeTraits.h>

#include <type_traits>
#include <utility>

namespace BifrostGraph {
namespace Executor {

/// \ingroup BifrostGraphExecutor

/// \brief The Owner<T> class template represents ownership of an object pointer.
/// It indicates that the pointed object must either be transferred to another owner
/// (like another Owner, or a std::unique_ptr) or deleted. Owner provides exception safety
/// to classes and functions that handle objects with dynamic lifetime, by guaranteeing
/// deletion of the pointed object on both normal exit or exit through exception.
/// \tparam T the owned object's exposed type used by indirection operators and by accessors.
template <typename T>
class Owner : private Internal::OwnerRep<T> {
private:
    /// \brief Functor for enabling overloaded conversions.
    /// Meta-programming functor for selectively enabling some templated constructors
    /// and member methods only when `P*` is implicitly convertible to a type `T*`.
    /// \tparam P The type of the pointed object to be converted to a `T*`.
    template <typename P>
    using if_convertible_from =
        typename std::enable_if<std::is_convertible<P*, T*>::value>::type;

    /// \brief Functor for enabling overloaded conversions taking raw pointers.
    /// The raw pointer `P*` must be compliant to be held in an Owner and it must be
    /// implicitly convertible to a type `T*`.
    /// \tparam P the storage type used for the owned object.
    template <typename P>
    using if_compliant_and_convertible_from =
        typename std::enable_if<std::is_convertible<P*, T*>::value &&
                                Internal::PointeeTraits::is_compliant<P>::value>::type;

    /// \brief Internal representation (and private implementations)
    using OwnerRep = Internal::OwnerRep<T>;

public:
    // Requirements
    static_assert(Internal::PointeeTraits::is_compliant<T>::value,
                  "Owner class template requires an object type T, "
                  "and T cannot be a pointer or a reference or an array (e.g. int[]), "
                  "and T must not include `const` nor `volatile` qualifiers.");

    /// \brief Construct an empty Owner.
    Owner() noexcept : OwnerRep() {}

    /// \brief Construct an \ref Owner that owns the object pointed by \p p.
    /// The owned object will be destructed using the expression `delete p`.
    /// The pointer \p p used for deletion is captured at the construction time of
    /// the \ref Owner.
    ///
    /// This constructor is only considered if a `P*` can be implicitly converted to a `T*`.
    ///
    /// If an error occurs while initializing the new \ref Owner, the object pointed by \p p
    /// is deleted before returning control to the caller and the resulting \ref Owner will
    /// be empty.
    ///
    /// \post `get() == p` if the initialization of the new \ref Owner succeeded;
    /// `get() == nullptr` otherwise.
    ///
    /// \tparam P the storage type used for the owned object.
    /// \param [in] p a pointer to an object to be owned by the Owner or a null pointer.
    template <typename P, typename = if_compliant_and_convertible_from<P>>
    Owner(P* p) noexcept {
        OwnerRep::template init<P>(p);
    }

    /// \brief The signature for the custom pointer deleter of a pointee \p p.
    /// This is the custom deleter type to use with the constructor `Owner(P* p, DeleterFunc d)`.
    /// \tparam P the storage type used for the owned object.
    /// \param [in] p a pointer to the owned object to destruct. Can be nullptr.
    template <typename P>
    using DeleterFunc = void (*)(P* p);

    /// \brief Construct an \ref Owner that owns the object pointed by \p p, with a custom
    /// pointer deleter set to \p d. The owned object will be destructed using the
    /// expression `d(p)`. The deleter (if any) is invoked in all cases, even when the
    /// object pointer \p p is null. The pointer \p p used for deletion is captured at the
    /// construction time of the \ref Owner.
    ///
    /// This constructor is only considered if a `P*` can be implicitly converted to a `T*`.
    ///
    /// If an error occurs while initializing the new \ref Owner and the custom deleter is
    /// valid, the object pointed by \p p is deleted using the custom deleter before
    /// returning control to the caller; if the custom deleter is invalid (nullptr),
    /// the object pointed by \p p is not deleted before returning control to the caller.
    /// In all error cases, the resulting \ref Owner will be empty.
    ///
    /// \pre   the custom pointer deleter must not be null
    /// \post `get() == p` if the initialization of the new \ref Owner succeeded;
    /// `get() == nullptr` otherwise.
    ///
    /// \tparam P the storage type used for the owned object.
    /// \param [in] p a pointer to an object to be owned by the Owner or a null pointer.
    /// \param [in] d the deleter to invoke when this Owner is destructed.
    template <typename P, typename = if_compliant_and_convertible_from<P>>
    Owner(P* p, DeleterFunc<P> d) noexcept {
        OwnerRep::template init<P>(p, d);
    }

    /// \brief Destruct this Owner.
    /// If no custom deleter was provided, the owned object is disposed using a
    /// `delete p` expression, otherwise the owned object is disposed using a `d(p)`
    /// expression.
    ~Owner() noexcept = default;

    /// \brief Move constructor
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    /// \param [in] rhs the Owner to be moved
    Owner(Owner&& rhs) noexcept = default;

    /// \brief Move conversion
    /// This move conversion is only considered if a `P*` can be implicitly converted to a `T*`.
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    /// \tparam P the storage type used for the owned object.
    /// \param [in] rhs the Owner to be moved
    template <typename P, typename = if_convertible_from<P>>
    Owner(Owner<P>&& rhs) noexcept : OwnerRep(std::move(rhs)) {}

    /// \brief Move assignment operator
    /// Move assign the Owner \p rhs to *this.
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    /// \param [in] rhs the source of the assignment
    /// \return `*this`
    Owner& operator=(Owner&& rhs) noexcept = default;

    /// \brief Check if the wrapped pointer is null.
    /// \return true if the wrapped pointer is not null; false otherwise.
    explicit constexpr operator bool() const noexcept { return OwnerRep::operator bool(); }

    /// \brief Indirection operator
    /// \pre    the wrapped pointer must not be null
    /// \return The reference to the pointed object
    const T& operator*() const noexcept { return OwnerRep::operator*(); }

    /// \brief Indirection operator
    /// \pre    the wrapped pointer must not be null
    /// \return The reference to the pointed object
    T& operator*() noexcept { return OwnerRep::operator*(); }

    /// \brief Indirection operator
    /// \pre    the wrapped pointer must not be null
    /// \return The pointer to the pointed object
    const T* operator->() const noexcept { return OwnerRep::operator->(); }

    /// \brief Indirection operator
    /// \pre    the wrapped pointer must not be null
    /// \return The pointer to the pointed object
    T* operator->() noexcept { return OwnerRep::operator->(); }

    /// \brief Accessor
    /// \return The pointer to the pointed object
    const T* get() const noexcept { return OwnerRep::get(); }

    /// \brief Accessor
    /// \return The pointer to the pointed object
    T* get() noexcept { return OwnerRep::get(); }

    /// \brief Reset this Owner object to its uninitialized state, deleting the
    /// currently owned object (if any).
    /// \post `get() == nullptr`
    /// \return `*this`
    Owner& reset() noexcept {
        OwnerRep::reset();
        return *this;
    }

    /// \brief Swap the content of this Owner with another one.
    /// \param [inout] other The other Owner to swap with.
    /// \post `*this` contains the old value of \p other
    /// \post \p other contains the old value of `*this`
    void swap(Owner& other) noexcept { OwnerRep::swap(other); }

private:
    /// Disabled
    /// \{
    Owner(const Owner&) = delete;
    Owner& operator=(const Owner&) = delete;
    /// \}

    /// \brief Friendship to allow conversion between Owners of different types.
    template <class P>
    friend class Owner;
};

} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_OWNER_H

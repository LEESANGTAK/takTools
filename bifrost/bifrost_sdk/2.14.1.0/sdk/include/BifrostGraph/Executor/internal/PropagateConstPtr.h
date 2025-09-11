//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file PropagateConstPtr.h
/// \brief BifrostGraph Executor PropagateConstPtr internal class.
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_PROPAGATE_CONST_PTR_H
#define BIFROSTGRAPH_EXECUTOR_PROPAGATE_CONST_PTR_H

#include <BifrostGraph/Executor/internal/PointeeTraits.h>
#include <BifrostGraph/Executor/internal/Utility.h>
#include <cassert>
#include <type_traits>

namespace BifrostGraph {
namespace Executor {
namespace Internal {

/// \brief Indicate if a pointer wrapper owns the pointee object. The wrapper's destructor
/// is responsible to delete the pointee object if it is owned.
enum class Owned : int {
    kNo, ///< The pointee object is not owned nor managed by the pointer wrapper.
    kYes ///< The pointee object is owned and managed by the pointer wrapper.
};

/// \brief The PropagateConstPtr<T,Owned> helper class template wraps an object pointer and
/// ensures constness propagation to this pointee. It can be used to wrap raw pointers
/// storage in objects, like in the PIMPL idiom, and ensures that a const object cannot
/// have non-const access to the raw pointer.
///
/// It has been inspired from a proposal to add a const-propagating wrapper to the C++ standard,
/// (see https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/n4388.html) but is implemented
/// to support pointer storage only, with the addition of optional ownership of the pointee.
///
/// \tparam T       the pointee's exposed type used by indirection operators and by accessors.
/// \tparam Owned   the ownership flag for the pointee.
template <typename T, Owned owned>
class PropagateConstPtr {
public:
    // Requirements
    static_assert(Internal::PointeeTraits::is_compliant<T>::value,
                  "PropagateConstPtr class template requires an object type T, "
                  "and T cannot be a pointer or a reference or an array (e.g. int[]), "
                  "and T must not include `const` nor `volatile` qualifiers.");

    /// \brief Construct an empty \ref PropagateConstPtr.
    PropagateConstPtr() noexcept : m_pointee(nullptr) {}

    /// \brief Construct a \ref PropagateConstPtr from a given object pointer.
    /// \param p the object pointer to wrap
    PropagateConstPtr(T* p) noexcept : m_pointee(nullptr) { _set(p); }

    /// \brief Destruct this \ref PropagateConstPtr by first resetting it (see \ref reset()).
    ~PropagateConstPtr() noexcept { reset(); }

    /// \brief Move constructor.
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    /// \param [in] rhs the PropagateConstPtr to be moved
    PropagateConstPtr(PropagateConstPtr&& rhs) noexcept : m_pointee(rhs.m_pointee) {
        rhs.m_pointee = nullptr;
    }

    /// \brief Move assignment operator. Moves assign the \p rhs to *this.
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    /// \param [in] rhs the source of the assignment
    /// \return `*this`
    PropagateConstPtr& operator=(PropagateConstPtr&& rhs) noexcept {
        if (this != &rhs) {
            reset();
            swap(rhs);
        }
        return *this;
    }

    /// \brief Check if this \ref PropagateConstPtr is not empty (the wrapped pointer
    /// is not nullptr).
    /// \return true if the wrapped pointer is not nullptr; false otherwise.
    explicit constexpr operator bool() const noexcept { return (m_pointee != nullptr); }

    /// \brief Indirection operator
    /// \pre    This \ref PropagateConstPtr must not be empty; otherwise this method has
    /// undefined behavior.
    /// \return a reference to the pointee object
    const T& operator*() const { return *m_pointee; }

    /// \brief Indirection operator
    /// \pre    This \ref PropagateConstPtr must not be empty; otherwise this method has
    /// undefined behavior.
    /// \return a reference to the pointee object
    T& operator*() { return *m_pointee; }

    /// \brief Indirection operator
    /// \pre    This \ref PropagateConstPtr must not be empty; otherwise this method has
    /// undefined behavior.
    /// \return a pointer to the pointee object
    const T* operator->() const { return m_pointee; }

    /// \brief Indirection operator
    /// \pre    This \ref PropagateConstPtr must not be empty; otherwise this method has
    /// undefined behavior.
    /// \return a pointer to the pointee object
    T* operator->() { return m_pointee; }

    /// \brief Accessor
    /// \return a pointer to the pointee object
    const T* get() const noexcept { return m_pointee; }

    /// \brief Accessor
    /// \return a pointer to the pointee object
    T* get() noexcept { return m_pointee; }

    /// \brief Reset this wrapper object, replacing the wrapped pointer by nullptr, and
    /// if the pointer is not nullptr, delete the pointee object. If pointee's destructor
    /// throws an exception, this exception is not propagated to the caller.
    /// \post `get() == nullptr`
    /// \return `*this`
    template <Owned _owned                                               = owned,
              typename std::enable_if<_owned == Owned::kYes, int>::type* = nullptr>
    PropagateConstPtr& reset() noexcept {
        static_assert(PointeeTraits::is_type_complete<T>::value,
                      "Attempting to delete an incomplete type. "
                      "Make sure the pointee object of type T has a complete type prior to "
                      "declare a PropagateConstPtr<T,Owned::kYes> type.");
        try {
            delete m_pointee;
        } catch (...) {
        }
        m_pointee = nullptr;
        return *this;
    }

    /// \brief Reset this wrapper object, replacing the wrapped pointer by nullptr.
    /// \post `get() == nullptr`
    /// \return `*this`
    template <Owned _owned                                              = owned,
              typename std::enable_if<_owned == Owned::kNo, int>::type* = nullptr>
    PropagateConstPtr& reset() noexcept {
        m_pointee = nullptr;
        return *this;
    }

    /// \brief First reset this \ref PropagateConstPtr, then set its content from a
    /// given object pointer.
    /// \param p        the new object pointer to wrap
    /// \return `*this`
    PropagateConstPtr& reset(T* p) noexcept {
        reset();
        _set(p);
        return *this;
    }

    /// \brief Swap the content of this \ref PropagateConstPtr with another one.
    /// \param [inout] other The other PropagateConstPtr to swap with.
    /// \post `*this` contains the old value of \p other
    /// \post \p other contains the old value of `*this`
    void swap(PropagateConstPtr& other) noexcept { _swap<T*>(m_pointee, other.m_pointee); }

private:
    /// \brief Set the content of this \ref PropagateConstPtr from a given object pointer.
    /// \param p the object pointer to wrap
    void _set(T* p) noexcept {
        // This method must not be called when this PropagateConstPtr is already set:
        assert(m_pointee == nullptr);
        m_pointee = p;
    }

    /// Disabled
    /// \{
    PropagateConstPtr(const PropagateConstPtr&) = delete;
    PropagateConstPtr& operator=(const PropagateConstPtr&) = delete;
    /// \}

private:
    T* m_pointee; // Pointer to the object to which this wrapper propagates constness.
};

} // namespace Internal
} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_PROPAGATE_CONST_PTR_H

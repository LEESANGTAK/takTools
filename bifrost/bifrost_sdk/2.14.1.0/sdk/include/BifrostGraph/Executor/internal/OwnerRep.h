//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file OwnerRep.h
/// \brief BifrostGraph Executor OwnerRep helper class.
///
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_OWNER_REP_H
#define BIFROSTGRAPH_EXECUTOR_OWNER_REP_H

#include <BifrostGraph/Executor/internal/ExecutorExport.h>
#include <BifrostGraph/Executor/internal/PointeeTraits.h>
#include <BifrostGraph/Executor/internal/Utility.h>
#include <cassert>

namespace BifrostGraph {
namespace Executor {
namespace Internal {

//=================================================================================================
// Types
//=================================================================================================

/// \brief The signature for the custom pointer deleter of a pointee \p p.
/// \tparam P the storage type used for the owned object.
/// \param [in] p a pointer to the owned object to destruct. \p p can be nullptr.
template <typename P>
using DeleterFunc = void(*)(P* p);

//=================================================================================================
// Implementation Classes
//=================================================================================================

/// \brief Base class for \ref OwnerCtrlBlkTyped and \ref OwnerCtrlBlkTypedWithDeleter.
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL OwnerCtrlBlkBase {
public:
    /// \brief Destruct this object, deleting the currently owned object (if any).
    /// Derived classes must implement this destructor to properly release the owned
    /// object using any proper mechanism.
    virtual ~OwnerCtrlBlkBase() noexcept;
};

/// \brief Internal template class OwnerCtrlBlkTyped used to manage a owned object
/// (pointee) `p`.
/// Upon destruction of the \ref OwnerCtrlBlkTyped, the owned object is deleted using a
/// `delete p` expression.
///
/// \tparam P the storage type used for the owned object.
template <typename P>
class OwnerCtrlBlkTyped : public OwnerCtrlBlkBase {
public:
    /// \brief Construct an OwnerCtrlBlkTyped without custom deleter.
    /// Takes a snapshot of the pointer to the owned object \p p.
    /// The owned object will be disposed using a `delete p` expression.
    ///
    /// \param [in] p a pointer to the owned object
    explicit OwnerCtrlBlkTyped(P* p) noexcept : m_pointee(p) {}

    /// \brief Destruct this object, deleting the currently owned object (if any)
    /// by invoking the expression `delete p`.
    ~OwnerCtrlBlkTyped() noexcept override {
        dispose(m_pointee);
    }

    /// \brief Dispose of the pointee object \p p using the expression `delete p`.
    /// \param [in] p a pointer to the owned object
    /// The C++ Standard states that deleting an object from an incomplete class type,
    /// while the complete class has a non-trivial destructor or a custom deallocation
    /// function, has undefined behavior.
    /// Hence, this method will fail to compile if template type \p P refers to an
    /// incomplete class type. It avoids issues when the destructor is actually declared
    /// virtual, because in this case, `delete p` would not perform a virtual function
    /// call unless the definition of the class is in scope.
    static void dispose(P* p) noexcept {
        static_assert(PointeeTraits::is_type_complete<P>::value,
                      "Attempting to delete an incomplete type. "
                      "Make sure the pointee object of type T has a complete type prior to "
                      "declare an Owner<T> type.");

        // The operator delete does not throw, but the destructor of pointee object could throw.
        try {
            delete p;
        } catch(...) {
        }
    }

private:
    /// Disabled
    /// \{
    OwnerCtrlBlkTyped(const OwnerCtrlBlkTyped&)            = delete;
    OwnerCtrlBlkTyped& operator=(const OwnerCtrlBlkTyped&) = delete;
    OwnerCtrlBlkTyped(OwnerCtrlBlkTyped&&)                 = delete;
    OwnerCtrlBlkTyped& operator=(OwnerCtrlBlkTyped&&)      = delete;
    /// \}

private:
    /// A pointer to the owned object.
    P*  m_pointee;
};

/// \brief Internal template class OwnerCtrlBlkTypedWithDeleter used to manage a owned object
/// (pointee) `p`.
/// Upon destruction of the \ref OwnerCtrlBlkTypedWithDeleter, the owned object is deleted using
/// a custom pointer deleter `d` with the `d(p)` expression.
///
/// \tparam P the storage type used for the owned object.
template <typename P>
class OwnerCtrlBlkTypedWithDeleter : public OwnerCtrlBlkBase {
public:
    /// \brief Construct an OwnerCtrlBlkTypedWithDeleter
    /// Takes a snapshot of the pointer to the owned object \p p and the deleter \p d.
    /// The owned object will be disposed using a `d(p)` expression.
    /// Upon destruction of this OwnerCtrlBlkTypedWithDeleter, or when another
    /// OwnerCtrlBlkTypedWithDeleter is moved-assigned into this one, the custom deleter is
    /// always called on the owned object, even if it is nullptr.
    /// \param [in] p a pointer to the owned object
    /// \param [in] d the custom deleter that will be used to dispose of the owned object
    OwnerCtrlBlkTypedWithDeleter(P* p, DeleterFunc<P> d) noexcept : m_pointee(p), m_deleter(d) {}

    /// \brief Destruct this object.
    /// Given the owned object `p` and the custom deleter `d`, this method deletes the
    /// currently owned object (if any) by invoking the custom deleter with the expression
    /// `d(p)`. The custom deleter is invoked even if the owned object is nullptr.
    ~OwnerCtrlBlkTypedWithDeleter() noexcept override {
        dispose(m_pointee, m_deleter);
    }

    /// \brief Dispose of the pointee object \p p by invoking the provided custom
    /// deleter \p d using the expression `d(p)`.
    /// \param [in] p a pointer to the owned object
    /// \param [in] d the custom deleter that will be used to dispose of the owned object
    static void dispose(P* p, DeleterFunc<P> d) noexcept {
        try {
            d(p);
        } catch(...) {
        }
    }

private:
    /// Disabled
    /// \{
    OwnerCtrlBlkTypedWithDeleter(const OwnerCtrlBlkTypedWithDeleter&)            = delete;
    OwnerCtrlBlkTypedWithDeleter& operator=(const OwnerCtrlBlkTypedWithDeleter&) = delete;
    OwnerCtrlBlkTypedWithDeleter(OwnerCtrlBlkTypedWithDeleter&&)                 = delete;
    OwnerCtrlBlkTypedWithDeleter& operator=(OwnerCtrlBlkTypedWithDeleter&&)      = delete;
    /// \}

private:
    /// A pointer to the owned object.
    P*              m_pointee;
    /// The custom deleter that will be used to dispose of the owned object.
    DeleterFunc<P>  m_deleter;
};

/// \brief The internal class OwnerRep that is used to implement the template class \ref Owner.
/// \tparam T the owned object's exposed type used by indirection operators and by accessors.
template <typename T>
class OwnerRep {
public:
    /// \brief Construct an empty \ref OwnerRep.
    OwnerRep() noexcept : m_pointee(nullptr), m_ctrlBlk(nullptr) {}

    /// \brief Destruct this \ref OwnerRep, deleting the currently owned object (if any).
    ~OwnerRep() noexcept {
        delete m_ctrlBlk;
    }

    /// \brief Initialize an \ref OwnerRep without a custom deleter.
    /// This method takes a snapshot of the pointer to the owned object \p p,
    /// capturing all information required to delete the owned object.
    /// The owned object will be disposed using a `delete p` expression.
    /// \tparam P the storage type used for the owned object.
    /// \param [in] p a pointer to the owned object
    template<typename P>
    void init(P* p) noexcept {
        try {
            // The OwnerCtrlBlkTyped must be constructed with the original type P, not T,
            // so it can dispose of the pointee using its original type:
            m_ctrlBlk = new OwnerCtrlBlkTyped<P>(p);
            m_pointee = p;
        } catch(...) {
            // The previous memory allocation failed, but this OwnerRep object is already
            // responsible to manage the pointee object. Dispose of the pointee object
            // immediately and return to the uninitialized state:
            OwnerCtrlBlkTyped<P>::dispose(p);
            m_pointee = nullptr;
            m_ctrlBlk = nullptr;
        }
    }

    /// \brief Initialize an \ref OwnerRep with a custom deleter.
    /// This method takes a snapshot of the pointer to the owned object \p p and the custom
    /// deleter \p d, capturing all information required to delete the owned object.
    /// The owned object will be disposed using a `d(p)` expression.
    /// Upon destruction of this OwnerRep, or when another OwnerRep is moved-assigned into
    /// this one, the custom deleter is always called on the owned object, even if it is
    /// nullptr.
    /// \tparam P the storage type used for the owned object.
    /// \param [in] p a pointer to the owned object
    /// \param [in] d the custom deleter that will be used to dispose of the owned object
    template<typename P>
    void init(P* p, DeleterFunc<P> d) noexcept {
        if (!d) {
            // Providing an invalid custom deleter is a critical error.
            // The Owner will remain empty and the object will not be deleted:
            return;
        }
        try {
            // The OwnerCtrlBlkTypedWithDeleter must be constructed with the original type P,
            // not T, so it can dispose of the pointee using its original type:
            m_ctrlBlk = new OwnerCtrlBlkTypedWithDeleter<P>(p, d);
            m_pointee = p;
        } catch(...) {
            // The previous memory allocation failed, but this OwnerRep object is already
            // responsible to manage the pointee object. Dispose of the pointee object
            // immediately and return to the uninitialized state:
            OwnerCtrlBlkTypedWithDeleter<P>::dispose(p, d);
            m_pointee = nullptr;
            m_ctrlBlk = nullptr;
        }
    }

    /// \brief Move constructor
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    /// \param [in] rhs the OwnerRep to be moved
    OwnerRep(OwnerRep&& rhs) noexcept : m_pointee(rhs.m_pointee), m_ctrlBlk(rhs.m_ctrlBlk) {
        rhs.m_pointee = nullptr;
        rhs.m_ctrlBlk = nullptr;
    }

    /// \brief Move conversion
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    /// \tparam P the storage type used for the owned object.
    /// \param [in] rhs the OwnerRep to be moved
    template <typename P>
    explicit OwnerRep(OwnerRep<P>&& rhs) noexcept
        : m_pointee(rhs.m_pointee), m_ctrlBlk(rhs.m_ctrlBlk) {
        rhs.m_pointee = nullptr;
        rhs.m_ctrlBlk = nullptr;
    }

    /// \brief Move assignment operator
    /// Move assign the OwnerRep \p rhs to *this.
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    /// \param [in] rhs the source of the assignment
    /// \return `*this`
    OwnerRep& operator=(OwnerRep&& rhs) noexcept {
        if (this != &rhs) {
            reset();
            swap(rhs);
        }
        return *this;
    }

    /// \brief Check if the wrapped pointer is null.
    /// \return true if the wrapped pointer is not null; false otherwise.
    explicit constexpr operator bool() const noexcept {
        return (get() != nullptr);
    }

    /// \brief Indirection operator
    /// \pre    the wrapped pointer must not be null
    /// \return the reference to the pointed object
    const T& operator*() const noexcept {
        assert(get());
        return *get();
    }

    /// \brief Indirection operator
    /// \pre    the wrapped pointer must not be null
    /// \return the reference to the pointed object
    T& operator*() noexcept {
        assert(get());
        return *get();
    }

    /// \brief Indirection operator
    /// \pre    the wrapped pointer must not be null
    /// \return the pointer to the pointed object
    const T* operator->() const noexcept {
        assert(get());
        return get();
    }

    /// \brief Indirection operator
    /// \pre    the wrapped pointer must not be null
    /// \return the pointer to the pointed object
    T* operator->() noexcept {
        assert(get());
        return get();
    }

    /// \brief Accessor
    /// \return the pointer to the pointed object
    const T* get() const noexcept {
        return m_pointee;
    }

    /// \brief Accessor
    /// \return the pointer to the pointed object
    T* get() noexcept {
        return m_pointee;
    }

protected:
    /// \brief Reset this \ref OwnerRep object to its uninitialized state, deleting the
    /// currently owned object (if any).
    /// \post `get() == nullptr`
    void reset() noexcept {
        m_pointee = nullptr;
        delete m_ctrlBlk;
        m_ctrlBlk = nullptr;
    }

    /// \brief Swap the content of this \ref OwnerRep with another one.
    /// \param [inout] other The other OwnerRep to swap with.
    /// \post `*this` contains the old value of \p other
    /// \post \p other contains the old value of `*this`
    void swap(OwnerRep& other) noexcept {
        _swap<T*>(m_pointee, other.m_pointee);
        _swap<OwnerCtrlBlkBase*>(m_ctrlBlk, other.m_ctrlBlk);
    }

private:
    /// Disabled
    /// \{
    OwnerRep(const OwnerRep&)            = delete;
    OwnerRep& operator=(const OwnerRep&) = delete;
    /// \}

    /// \brief Friendship to allow conversion between OwnerReps of different types.
    template <class P>
    friend class OwnerRep;

private:
    /// A pointer to the owned object.
    T*                  m_pointee;
    /// A typed control block to manage the owned object.
    OwnerCtrlBlkBase*   m_ctrlBlk;
};

} // namespace Internal
} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_OWNER_REP_H

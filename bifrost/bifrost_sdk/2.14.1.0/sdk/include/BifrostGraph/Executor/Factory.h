//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file  Factory.h
/// \brief Provide factory functions for Executor core classes.
/// \note The contents of this file belong to a feature that is still
/// under development, and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_FACTORY_H
#define BIFROSTGRAPH_EXECUTOR_FACTORY_H

#include <BifrostGraph/Executor/Owner.h>
#include <stdexcept>
#include <utility>

namespace BifrostGraph {
namespace Executor {
/// \ingroup BifrostGraphExecutor
/// \defgroup BifrostGraphExecutorFactory BifrostGraph Executor Factory
/// \brief Factory functions for Executor core classes.
///@{

/// \brief Create a new T object, constructed from the given arguments, and validate it
/// with the expression `T::isValid()`.
///
/// If the object is successfully created and it is valid, then an Owner<T> pointing to
/// the newly created object is returned.
///
/// If an exception is thrown during memory allocation or during the object's constructor
/// execution, this exception is propagated to the caller.
/// If after its construction the newly created T object is invalid, it is deleted and
/// an exception is thrown.
///
/// Whenever the new T object must be deleted (by this \ref makeOwner function or by the
/// returned \ref Owner object), it will be destructed using the expression `delete p`,
/// where `p` is a pointer to the T object.
///
/// \tparam     T     the type of object to create
/// \tparam     Args  the types of the constructor arguments
///
/// \param [in] args  the arguments to pass to the constructor of the object
/// \return           An \ref Owner containing the object if the construction has succeeded
/// and if the new object is valid; an exception is thrown otherwise.
///
/// \exception std::logic_error Thrown if the newly created T object is invalid after its
/// construction. This is usually caused by wrong arguments passed to the constructor.
/// \exception <other> An exception may be thrown during memory allocation or during the
/// object's constructor execution. Such exceptions are not handled by \ref makeOwner but
/// they are propagated to the caller.
template <typename T, typename... Args>
Owner<T> makeOwner(Args&&... args) {
    Owner<T> owner{new T(std::forward<Args>(args)...)};
    if (!owner || !owner->isValid()) {
        throw std::logic_error(
            "makeOwner<T>(...) failed: "
            "the newly allocated object was invalid.");
    }
    return owner;
}

/// \brief The signature for the custom pointer deleter of a pointee \p p.
/// This is the custom deleter type to use with the constructor `Owner(P* p, DeleterFunc d)`.
/// \tparam P the storage type used for the owned object.
/// \param [in] p a pointer to the owned object to destruct. Can be nullptr.
template <typename P>
using DeleterFunc = void (*)(P* p);

/// \brief Create a new T object, constructed from the given arguments, and validate it
/// with the expression `T::isValid()`.
///
/// If the object is successfully created and it is valid, then an Owner<T> pointing to
/// the newly created object is returned.
///
/// If an exception is thrown during memory allocation or during the object's constructor
/// execution, this exception is propagated to the caller.
/// If after its construction the newly created T object is invalid, it is deleted and
/// an exception is thrown.
///
/// Whenever the new T object must be deleted (by this \ref makeOwner function or by the
/// returned \ref Owner object), it will be destructed by calling the given custom
/// deleter \p d using the expression `d(p)`, where `p` is a pointer to the T object.
///
/// \tparam     T     the type of object to create
/// \tparam     Args  the types of the constructor arguments
///
/// \param [in] d     the deleter to invoke when the new object is destructed.
/// \param [in] args  the arguments to pass to the constructor of the object
/// \return           An \ref Owner containing the object if the construction has succeeded
/// and if the new object is valid; an exception is thrown otherwise.
///
/// \exception std::logic_error Thrown if the newly created T object is invalid after its
/// construction. This is usually caused by wrong arguments passed to the constructor.
/// \exception <other> An exception may be thrown during memory allocation or during the
/// object's constructor execution. Such exceptions are not handled by \ref makeOwner but
/// they are propagated to the caller.
template <typename T, typename... Args>
Owner<T> makeOwner(DeleterFunc<T> d, Args&&... args) {
    Owner<T> owner{new T(std::forward<Args>(args)...), d};
    if (!owner || !owner->isValid()) {
        throw std::logic_error(
            "makeOwner<T>(DeleterFunc<T>, ...) failed: "
            "the newly allocated object was invalid.");
    }
    return owner;
}

/// \brief Helper macro to declare friend the makeOwner<> factory functions.
#define EXECUTOR_DECLARE_MAKE_OWNER_FRIENDSHIP()                                               \
    template <typename T, typename... Args>                                                    \
    friend BifrostGraph::Executor::Owner<T> BifrostGraph::Executor::makeOwner(Args&&... args); \
    template <typename T, typename... Args>                                                    \
    friend BifrostGraph::Executor::Owner<T> BifrostGraph::Executor::makeOwner(                 \
        void (*deleterFunc)(T * p), Args&&... args)

///@}

} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_FACTORY_H

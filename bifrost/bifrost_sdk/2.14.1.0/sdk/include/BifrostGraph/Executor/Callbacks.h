//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file Callbacks.h
/// \brief BifrostGraph Executor Callbacks.
/// \note The contents of this file belong to a feature that is still
/// under development, and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_CALLBACKS_H
#define BIFROSTGRAPH_EXECUTOR_CALLBACKS_H

#include <BifrostGraph/Executor/internal/ExecutorExport.h>

namespace BifrostGraph {
namespace Executor {

/// \ingroup BifrostGraphExecutor

/// \brief BifrostGraph Executor Callbacks
///
/// An instance of class Callbacks can be used by the host to be notified by Bifrost upon specific
/// events.
///
/// An instance of class Callbacks should be allocated on the heap, not on the stack.
/// The \ref Workspace will manage its lifetime and delete it by calling
/// \ref Callbacks::deleteThis when the Workspace gets unloaded.
///
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL Callbacks {
public:
    /// \brief Constructor
    Callbacks() noexcept;

    /// \brief Destructor.
    virtual ~Callbacks() noexcept;

    /// \brief The signature of the function used to create an instance of class Callbacks.
    using CreateFunc = BifrostGraph::Executor::Callbacks* (*)();

    /// \brief Get the name of the function used to create new instance of class Callbacks.
    ///
    /// This function is the C entry point used to register new instance of class Callbacks
    /// from a shared library.
    ///
    /// The client code must declare and define the entry point.
    /// The function must have the CreateFunc signature.
    ///
    /// Note that `BIFROSTGRAPH_EXECUTOR_SHARED_DECL` is for symbol visiblity,
    /// see ExecutorExport.h file.
    ///
    /// \code {.cpp}
    /// extern "C" {
    /// BIFROSTGRAPH_EXECUTOR_SHARED_DECL BifrostGraph::Executor::Callbacks*
    /// registerBifrostCallbacks(void);
    ///
    /// BIFROSTGRAPH_EXECUTOR_SHARED_DECL BifrostBoardExecutorCallbacks*
    /// registerBifrostCallbacks(void) {
    ///     // Return a pointer to my class that implements
    ///     // BifrostGraph::Executor::Callbacks interface.
    ///     return new MyCallbacks());
    /// }
    /// \endcode
    ///
    /// The Callbacks shared library is exposed to Bifrost via
    /// a config file. The JSON config file will need a `callbackLibs`
    /// section. Note that, to be portable and depending on the platform,
    /// Bifrost config file parsing will automatically add the prefix "lib" and
    /// suffix  "dll", "so", or "dylib".
    ///
    /// \code{.json}
    /// {
    ///     "AminoConfigurations": [
    ///         {
    ///             "vendorName": "MyCompany",
    ///             "libraryVersion": "0.0.1",
    ///             "libraryName": "MyPackName",
    ///             "callbackLibs": [
    ///                 {
    ///                     "path": "Directory containing the shared lib",
    ///                     "files": [
    ///                         "MyCallbacks"
    ///                     ]
    ///                 }
    ///             ]
    ///         }
    ///     ]
    /// }
    /// \endcode
    ///
    /// \return "registerBifrostCallbacks"
    static const char* createFuncName() noexcept;

    /// \brief Instruct this class instance to delete itself.
    virtual void deleteThis() noexcept = 0;

    /// \brief The notification method called when the feedback port values have been cleared.
    virtual void onStateValuesTornDown() noexcept;
};

} // nanespace Executor
} // namespace BifrostGraph
#endif

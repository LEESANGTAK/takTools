//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file Types.h
/// \brief BifrostGraph Executor common types.
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_TYPES_H
#define BIFROSTGRAPH_EXECUTOR_TYPES_H

#include <BifrostGraph/Executor/internal/ExecutorExport.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/String.h>

namespace BifrostGraph {
namespace Executor {

/// \ingroup BifrostGraphExecutor
/// \defgroup BifrostGraphExecutorTypes BifrostGraph Executor Types
/// \brief BifrostGraph Executor common types and helpers.
///@{

/// \brief The category of a reported message.
enum class MessageCategory : int {
    kError,   ///< The message refers to an error that prevents the
              ///  regular execution of the current action.
    kWarning, ///< The message refers to a warning that doesn't
              ///  prevent the execution of the current action.
    kInfo     ///< The message refers to user information.
};

/// \brief The source object of a reported message.
enum class MessageSource : int {
    kWorkspace,      ///< The message is sent by the Workspace.
    kLibrary,        ///< The message is sent by the Library.
    kGraphContainer, ///< The message is sent by a GraphContainer.
    kJob,            ///< The message is sent by a Job.
    kTranslation     ///< The message is sent by a TypeTranslation.
};

/// \brief The mode controlling the behavior of GraphContainer::setGraph.
enum class SetGraphMode : int {
    kDefault = 0, ///< Set the designated graph as the new graph of this GraphContainer.
    kCopy    = 1  ///< Make a copy of the designated graph then set the copy as the new graph of
                  ///< this GraphContainer.
};

/// \brief Tag for explicitly specifying that a constructor should not initialize
/// any data members, leaving the object in an invalid state.
enum class Uninitialized : int {
    kUninitialized ///< Uninitialized and in an invalid state.
};

/// \brief The port class. This is to indicate if a port is a regular input
/// or output port, a terminal output or a job port input.
enum class PortClass : int {
    eRegular, ///< Regular input or output port. Known before graph
              ///< compilation.

    eTerminal, ///< Terminal output port. Known after graph compilation.

    eJobPort ///< Job input port. Known after graph compilation.
};

/// \brief The direction of a port.
enum class PortDirection : int {
    kUndefined = 0, ///< The port is invalid and the I/O mode is undetermined.
    kInput     = 1, ///< The port is an input port
    kOutput    = 2  ///< The port is an output port
};

/// \brief Modes for graph compilation.
enum class GraphCompilationMode : int {
    kInit,  ///< Compile the graph. This implies resetting the Amino runtime services
            ///< instance and clearing any feedback port values.
    kUpdate ///< Update the compiled graph. This implies that the Amino runtime services
            ///< instance and any feedback port values should be kept.
};

/// \brief Status of graph compilation.
enum class GraphCompilationStatus : int {
    kInvalid,  ///< The GraphContainer is invalid.
    kFailure,  ///< The graph compilation was unsuccessful: the graph contains errors.
    kSuccess,  ///< The graph compilation was successful.
    kUnchanged ///< The graph compilation was successful, and has no change compared to
               ///< previous compilation.
};

/// \brief Modes for job execution
enum class JobExecutionMode : int {
    kDefault     = 0, ///< Execute the job normally.
    kResetStates = 1  ///< Reset the job states (feedback ports) before execution.
};

/// \brief Status of job execution.
enum class JobExecutionStatus : int {
    kInvalid, ///< The Job is invalid.
    kFailure, ///< The job execution was completed with errors.
    kSuccess  ///< The job execution was completed successfully.
};

/// \brief Type alias to simplify usage of Amino::Array<Amino::String>.
using StringArray = Amino::Array<Amino::String>;

///@}

} // namespace Executor
} // namespace BifrostGraph

/// \addtogroup BifrostGraphExecutorTypes
/// \brief Helpers for BifrostGraph::Executor::JobExecutionMode manipulation
/// \{
inline BifrostGraph::Executor::JobExecutionMode operator|(
    BifrostGraph::Executor::JobExecutionMode lhs, BifrostGraph::Executor::JobExecutionMode rhs) {
    return static_cast<BifrostGraph::Executor::JobExecutionMode>(static_cast<int>(lhs) |
                                                                 static_cast<int>(rhs));
}
inline BifrostGraph::Executor::JobExecutionMode& operator|=(
    BifrostGraph::Executor::JobExecutionMode&      lhs,
    const BifrostGraph::Executor::JobExecutionMode rhs) {
    return lhs = lhs | rhs;
}
inline BifrostGraph::Executor::JobExecutionMode operator&(
    BifrostGraph::Executor::JobExecutionMode lhs, BifrostGraph::Executor::JobExecutionMode rhs) {
    return static_cast<BifrostGraph::Executor::JobExecutionMode>(static_cast<int>(lhs) &
                                                                 static_cast<int>(rhs));
}
/// \}

#endif // BIFROST_GRAPH_EXECUTOR_TYPES_H

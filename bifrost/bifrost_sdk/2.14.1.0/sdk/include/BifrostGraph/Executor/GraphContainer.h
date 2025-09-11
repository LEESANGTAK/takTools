//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file GraphContainer.h
/// \brief BifrostGraph Executor GraphContainer.
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_GRAPHCONTAINER_H
#define BIFROSTGRAPH_EXECUTOR_GRAPHCONTAINER_H

#include <BifrostGraph/Executor/Factory.h>
#include <BifrostGraph/Executor/Owner.h>
#include <BifrostGraph/Executor/Types.h>

#include <BifrostGraph/Executor/internal/ExecutorExport.h>
#include <BifrostGraph/Executor/internal/PropagateConstPtr.h>

#include <Amino/Core/String.h>

//-------------------------------------------------------------------------------------------------
// Forward declarations
//-------------------------------------------------------------------------------------------------

namespace BifrostGraph {
namespace Executor {

class Job;
class Workspace;

namespace Private {
class GraphContainerImpl;
class JobImpl;
class IGraphContainerOwner;
class IRestrictedGraphContainerServices;
} // namespace Private

/// \ingroup BifrostGraphExecutor

//-------------------------------------------------------------------------------------------------
// CLASS GraphContainer
//-------------------------------------------------------------------------------------------------

/// \brief The GraphContainer class that loads a graph to be executed and manages the Jobs
/// that execute this graph.
///
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL GraphContainer {
protected:
    //---------------------------------------------------------------------------------------------
    // Initialization
    //---------------------------------------------------------------------------------------------

    /// \brief Construct a GraphContainer. The new GraphContainer is owned and managed by the
    /// \ref Workspace.
    ///
    /// If an error occurs during the construction of this GraphContainer then
    /// \ref BifrostGraph::Executor::GraphContainer::isValid will return false and all future
    /// operations on this GraphContainer will fail.
    /// If a class is derived from GraphContainer, it is recommended to keep protected the
    /// constructors on the derived class, and still use the factory functions
    /// \ref BifrostGraph::Executor::makeOwner (see Factory.h) to create a derived class
    /// instance.
    ///
    /// \param [in] owner The GraphContainer's owner. Only the Workspace can create an
    ///                   IGraphContainerOwner object required by this constructor, hence only
    ///                   the Workspace can initiate the construction of a GraphContainer (see
    ///                   Workspace's addGraphContainer template method).
    explicit GraphContainer(Private::IGraphContainerOwner& owner) noexcept;

    /// \brief Constructor that leaves the GraphContainer in an uninitialized state.
    ///
    /// After this constructor returns, the method \ref
    /// BifrostGraph::Executor::GraphContainer::isValid will return false and all future
    /// operations on the GraphContainer will fail.
    ///
    /// \param [in] uninitialized  an Uninitialized enum value.
    /// \warning This constructor is used internally by the Executor. Use with caution.
    explicit GraphContainer(Uninitialized uninitialized) noexcept;

    /// \brief Allow the makeOwner<> factory functions to access the constructors of this class.
    EXECUTOR_DECLARE_MAKE_OWNER_FRIENDSHIP();

    struct SetGraphInfo;

public:
    /// \brief Destructor.
    ///
    /// The destructor should not be called directly since the GraphContainers are managed by
    /// the Workspace. To delete a GraphContainer, use the Workspace's method
    /// \ref Workspace::deleteGraphContainer.
    ///
    virtual ~GraphContainer() noexcept;

    /// \brief Check if this GraphContainer has been successfully initialized.
    ///
    /// If an error occurs during the construction of a GraphContainer, isValid() will
    /// return false and all future operations on the GraphContainer will fail.
    ///
    /// \return true if this GraphContainer has been successfully initialized and is ready to
    /// be used; false otherwise.
    virtual bool isValid() const noexcept;

    /// \brief Get a statically allocated GraphContainer that is uninitialized, invalid and not
    /// owned by any Workspace. Any operation on this instance will always fail and
    /// \ref GraphContainer::isValid will return false.
    static GraphContainer& getInvalid() noexcept;

    /// \brief Access the \ref Workspace which owns this GraphContainer.
    /// \return A reference to the \ref Workspace which owns this GraphContainer, if this instance
    /// is valid (see \ref GraphContainer::isValid); an invalid \ref Workspace otherwise.
    /// \{
    const Workspace& getWorkspace() const noexcept;
    Workspace&       getWorkspace() noexcept;
    /// \}

    //---------------------------------------------------------------------------------------------
    // Graph Management
    //---------------------------------------------------------------------------------------------

    /// \brief Set the graph in this GraphContainer.
    ///
    /// The definition of the graph designated by \p name must have been previously loaded in the
    /// \ref Library (see \ref Workspace::loadConfigFiles or \ref Library::loadDefinitionFile).
    ///
    /// If \p mode is \ref SetGraphMode::kCopy, the copy of the graph will have a new unique fully
    /// qualified name to avoid name collisions (see \ref GraphContainer::SetGraphInfo).
    ///
    /// If the graph does not exist in the \ref Library, or if the \p mode is
    /// \ref SetGraphMode::kCopy and the attempt to copy the existing graph fails, then this
    /// method aborts and does not set the graph.
    /// Otherwise, the onBeginSetGraph and onEndSetGraph notification handlers will be
    /// called respectively just before and after setting the graph in this GraphContainer,
    /// allowing a class derived from \ref GraphContainer to do any additional work it may need
    /// to do when the graph is set or replaced by another one.
    ///
    /// \param [in] name    The fully qualified name of the graph to be set.
    /// \param [in] mode    The mode controlling the behavior of setGraph.
    /// \return true if the graph exists and has been successfully copied (if required) and set
    /// in this GraphContainer; false otherwise.
    bool setGraph(const Amino::String& name, SetGraphMode mode = SetGraphMode::kDefault) noexcept;

    /// \brief Get the name of the graph currently set in this GraphContainer.
    ///
    /// \return The name of the currently set graph, if any, an empty string otherwise.
    Amino::String getGraphName() const noexcept;

    /// \brief Get the fully qualified name of the graph currently set in this GraphContainer.
    ///
    /// \return The fully qualified name of the currently set graph, if any, an empty string
    /// otherwise.
    Amino::String getGraphQualifiedName() const noexcept;

    /// \brief Compile the graph for job execution.
    ///
    /// The onBeginCompileGraph and onEndCompileGraph notification handlers will be
    /// called respectively just before and after compiling the graph of this GraphContainer,
    /// allowing a class derived from \ref GraphContainer to do any additional work it may need
    /// to do when the graph is compiled.
    ///
    /// \param [in] mode The mode on how to compile the graph (i.e. full compile or update),
    /// (see \ref GraphCompilationMode).
    /// \return The graph compilation status (see \ref GraphCompilationStatus).
    ///
    /// \note When the graph is compiled, whatever is the specified \p mode, the inputs and outputs
    /// of the associated \ref Job are updated. This implies that the Job input values must be
    /// set again (see \ref Job::getInputs and \ref Job::setInputValue) and the Job must be
    /// executed again (see \ref Job::execute) in order to retrieve the Job output values
    /// (see \ref Job::getOutputs and \ref Job::getOutputValue).
    GraphCompilationStatus compile(GraphCompilationMode mode) noexcept;

    //---------------------------------------------------------------------------------------------
    // Job Management
    //---------------------------------------------------------------------------------------------

    /// \brief Get a reference to the \ref Job currently set in this GraphContainer.
    /// \return A reference to the \ref Job if this instance is valid (see
    /// \ref GraphContainer::isValid); an invalid \ref Job otherwise.
    /// \{
    const Job& getJob() const noexcept;
    Job&       getJob() noexcept;
    /// \}

protected:
    /// \brief Report a message from this GraphContainer to its Workspace owner. The source of the
    /// reported message will be set to MessageSource::kGraphContainer.
    ///
    /// \param [in] category The message category.
    /// \param [in] message  The message itself.
    void reportMessage(MessageCategory category, const Amino::String& message) const noexcept;

    /// \brief The information that is passed to onBeginSetGraph and onEndSetGraph
    /// notification handlers.
    struct SetGraphInfo {
        Amino::String name;          ///< The name of the graph. If setGraph's mode parameter was
                                     ///< \ref SetGraphMode::kCopy, then this is the name of the
                                     ///< graph copy, otherwise it is the name of the original
                                     ///< graph.
        Amino::String qualifiedName; ///< The fully qualified name of the graph. If setGraph's mode
                                     ///< parameter was \ref SetGraphMode::kCopy, then this is the
                                     ///< fully qualified name of the graph copy, otherwise it
                                     ///< is the same name as the one that was passed to setGraph.
        Amino::String filePath;      ///< The absolute path of the file that contains the
                                     ///< definition of the graph.
                                     ///< This path can be empty if the graph has not been loaded
                                     ///< from a file.
                                     ///< If non-empty, this path is normalized (see
                                     ///< \ref BifrostGraph::Executor::Utility::getNormalizedPath).
        SetGraphMode mode;           ///< The mode controlling the behavior of setGraph. This
                                     ///< is the same mode that was passed to setGraph.
    };

private:
    friend class Private::GraphContainerImpl;

    /// \brief The notification method called by setGraph just before a new graph is set.
    ///
    /// When this method is called, the previously set graph, if any, is still set in this
    /// GraphContainer.
    /// If the setGraph's mode parameter was \ref SetGraphMode::kCopy and the attempt to
    /// copy the existing graph fails, then this notification method will not be called.
    ///
    /// \param [in] graphInfo The information about the graph that is about to be set.
    ///
    /// \note The default implementation does nothing.
    virtual void onBeginSetGraph(const SetGraphInfo& graphInfo) noexcept;

    /// \brief The notification method called by setGraph just after a new graph is set.
    ///
    /// If the setGraph's mode parameter was \ref SetGraphMode::kCopy and the attempt to
    /// copy the existing graph fails, then this notification method will not be called.
    ///
    /// \param [in] graphInfo The information about the graph that has just been set.
    ///
    /// \note The default implementation does nothing.
    virtual void onEndSetGraph(const SetGraphInfo& graphInfo) noexcept;

    /// \brief The notification method called by \ref compile when the graph is about to be compiled.
    ///
    /// \note The default implementation does nothing.
    virtual void onBeginCompileGraph() noexcept;

    /// \brief The notification method called by \ref compile once the graph has been compiled.
    ///
    /// \param [in] status The status of the compile operation.
    /// \note The default implementation does nothing.
    virtual void onEndCompileGraph(GraphCompilationStatus status) noexcept;

public:
    //---------------------------------------------------------------------------------------------
    // IRestrictedGraphContainerServices
    //---------------------------------------------------------------------------------------------

    /// \brief Obtain an interface giving access to private GraphContainer services.
    ///
    /// \pre This GraphContainer must be valid
    /// (\ref BifrostGraph::Executor::GraphContainer::isValid).
    /// Calling this method on an invalid GraphContainer will produce undefined behavior.
    /// \note This is an internal method used by the Executor SDK.
    ///
    /// \return A reference to the IRestrictedGraphContainerServices interface of this
    /// GraphContainer.
    /// \{
    const Private::IRestrictedGraphContainerServices& getRestrictedServices() const noexcept;
    Private::IRestrictedGraphContainerServices&       getRestrictedServices() noexcept;
    /// \}

private:
    /// Disabled
    /// \{
    GraphContainer(const GraphContainer&)            = delete;
    GraphContainer(GraphContainer&&)                 = delete;
    GraphContainer& operator=(const GraphContainer&) = delete;
    GraphContainer& operator=(GraphContainer&&)      = delete;
    /// \}

private:
    Internal::PropagateConstPtr<Private::GraphContainerImpl, Internal::Owned::kYes> m_impl;
    static GraphContainer                                                           s_invalid;
};

} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_GRAPHCONTAINER_H

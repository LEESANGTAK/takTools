//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file Workspace.h
/// \brief BifrostGraph Executor Workspace.
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_WORKSPACE_H
#define BIFROSTGRAPH_EXECUTOR_WORKSPACE_H

#include <BifrostGraph/Executor/internal/ExecutorExport.h>
#include <BifrostGraph/Executor/internal/PropagateConstPtr.h>

#include <BifrostGraph/Executor/Factory.h>
#include <BifrostGraph/Executor/GraphContainer.h>
#include <BifrostGraph/Executor/Owner.h>
#include <BifrostGraph/Executor/TypeTranslation.h>
#include <BifrostGraph/Executor/Types.h>

#include <Amino/Core/String.h>

#include <utility>

//-------------------------------------------------------------------------------------------------
// Forward declarations
//-------------------------------------------------------------------------------------------------

namespace Amino {
class TypeId;
} // namespace Amino

namespace BifrostGraph {
namespace Executor {

class Library;
class Watchpoint;
class WatchpointLayoutFactory;

namespace Private {
class IGraphContainerOwner;
class IRestrictedWorkspaceServices;
class WorkspaceImpl;
} // namespace Private

/// \defgroup BifrostGraphExecutor BifrostGraph Executor
/// \brief SDK to execute Bifrost graphs.
///@{
//-------------------------------------------------------------------------------------------------
// CLASS Workspace
//-------------------------------------------------------------------------------------------------
/// \brief The Workspace is the central element of the BifrostGraph Executor.
///
/// A Workspace object holds a Library that stores all Bifrost resources and GraphContainers
/// that represent the graphs to be executed.
/// For the time being, a Library should not be shared by multiple Workspaces, since the
/// Library modifications are not yet thread safe. On the other hand, creating a Library,
/// loading resources into it and then sharing it in read-only with another Workspace could
/// be supported in the future, but there are no mechanism that enforces the read-only mode,
/// so users would have to be careful here.
///
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL Workspace {
protected:
    //---------------------------------------------------------------------------------------------
    // Initialization
    //---------------------------------------------------------------------------------------------

    /// \brief Construct a Workspace. The Workspace is initialized with a newly created
    /// \ref BifrostGraph::Executor::Library with the given name.
    ///
    /// If an error occurs during the construction of this Workspace, or its underlying
    /// \ref BifrostGraph::Executor::Library, then \ref BifrostGraph::Executor::Workspace::isValid
    /// will return false and all future operations on this Workspace will fail.
    ///
    /// This constructor is protected to force the usage of factory functions
    /// \ref BifrostGraph::Executor::makeOwner (see Factory.h) to create it.
    /// If a class is derived from Workspace, it is recommended to keep protected the constructors
    /// on the derived class, and still use the factory functions to create a derived class
    /// instance.
    ///
    /// \param [in] name An optional name for the \ref BifrostGraph::Executor::Library.
    explicit Workspace(const Amino::String& name) noexcept;

    /// \brief Constructor that leaves the Workspace in an uninitialized state.
    ///
    /// After this constructor returns, the method \ref BifrostGraph::Executor::Workspace::isValid
    /// will return false and all future operations on the Workspace will fail.
    ///
    /// \param [in] uninitialized  an Uninitialized enum value.
    /// \warning This constructor is used internally by the Executor. Use with caution.
    explicit Workspace(Uninitialized uninitialized) noexcept;

    /// \brief Allow the makeOwner<> factory functions to access the constructors of this class.
    EXECUTOR_DECLARE_MAKE_OWNER_FRIENDSHIP();

public:
    /// \brief Destructor.
    virtual ~Workspace() noexcept;

    /// \brief Check if this Workspace has been successfully initialized.
    ///
    /// If an error occurs during the construction of a Workspace, isValid() will return
    /// false and all future operations on the Workspace will fail.
    /// If this method is overridden, the deriving implementation should first call the
    /// base class implementation to check if this Workspace is valid, then do its own
    /// subclass validation.
    ///
    /// \return true if this Workspace has been successfully initialized and is ready to
    /// be used; false otherwise.
    virtual bool isValid() const noexcept;

    /// \brief Get a statically allocated Workspace that is uninitialized, invalid and not
    /// linked to any Library, GraphContainer or Job. Any operation on this instance will
    /// always fail and \ref Workspace::isValid will return false.
    static Workspace& getInvalid() noexcept;

    //---------------------------------------------------------------------------------------------
    // Library
    //---------------------------------------------------------------------------------------------

    /// \brief Get the Library that is used by this Workspace.
    ///
    /// If the Workspace is valid, then the returned Library will also be valid.
    /// Otherwise, the returned Library will be invalid (see
    /// \ref BifrostGraph::Executor::Library::isValid).
    ///
    /// \return A reference to the Library that is used by this Workspace.
    /// \{
    const Library& getLibrary() const noexcept;
    Library&       getLibrary() noexcept;
    /// \}

    //---------------------------------------------------------------------------------------------
    // Configuration Files
    //---------------------------------------------------------------------------------------------

    /// \brief Read the Bifrost configuration JSON files listed in \p configFiles,
    /// excluding from them the packs listed in \p disabledPacks, and then load all
    /// resources listed in these files.
    ///
    /// The details about the errors that may occur while reading the configuration data, or
    /// while loading the resources, are reported by calls to Workspace's onReportedMessage.
    /// All configuration files are read even if errors are detected while reading them.
    /// If any error is detected while reading the configuration files, none of the resources
    /// they list will be loaded and false will be returned.
    ///
    /// \param [in] configFiles     A list of Bifrost configuration JSON files to read.
    /// \param [in] disabledPacks   The list of packs to skip, designated by their library
    ///                             names in the Bifrost configuration JSON files.
    /// \return true if all Bifrost configuration JSON files have been successfully read and all
    /// resources have been successfully loaded; false if an error occurred while reading the
    /// Bifrost configuration JSON files or while loading the resources they list.
    bool loadConfigFiles(const StringArray& configFiles,
                         const StringArray& disabledPacks = StringArray()) noexcept;

    //---------------------------------------------------------------------------------------------
    // Resources Services
    //---------------------------------------------------------------------------------------------

    /// \brief Let the TypeTranslations register any plugins or data types they need.
    ///
    /// This method will call \ref TypeTranslation::registerHostPlugins with the \p hostData
    /// argument on each registered TypeTranslation resource object.
    ///
    /// \param hostData The host data to pass to each registerHostPlugins function to call.
    /// \return true if all registerHostPlugins called functions have returned true;
    /// false otherwise.
    bool registerTypeTranslationsPlugins(TypeTranslation::PluginHostData* hostData) const noexcept;

    /// \brief Let the TypeTranslations unregister any previously registered plugins or data types.
    ///
    /// This method will call \ref TypeTranslation::unregisterHostPlugins with the \p hostData
    /// argument on each registered TypeTranslation resource object.
    ///
    /// \param hostData The host data to pass to each unregisterHostPlugins function to call.
    /// \return true if all unregisterHostPlugins called functions have returned true;
    /// false otherwise.
    bool unregisterTypeTranslationsPlugins(
        TypeTranslation::PluginHostData* hostData) const noexcept;

    //---------------------------------------------------------------------------------------------
    // GraphContainer Management
    //---------------------------------------------------------------------------------------------

    /// \brief Create a new \ref GraphContainer and add it to this Workspace.
    /// This template method allows one to create and add an instance of their own subclass of the
    /// GraphContainer base class by passing a Functor \p func that creates such an instance of
    /// their subclass.
    ///
    /// \tparam Functor the function used to create a new instance of a GraphContainer,
    /// wrapped in an Owner object. The signature of this function must be:
    ///     Owner<GraphContainer> func(Private::IGraphContainerOwner& owner);
    ///
    /// \param func the function called by this method to create a new GraphContainer.
    /// \return If this Workspace is valid, and if \p func returned a non-empty Owner<>
    /// containing a valid GraphContainer, and if the Workspace has successfully added it,
    /// then a reference to the newly added \ref GraphContainer is returned;
    /// otherwise, a reference to an invalid \ref GraphContainer is returned.
    template <typename Functor>
    GraphContainer& addGraphContainerT(Functor&& func) noexcept {
        if (isValid()) {
            // Make a new GraphContainer (potentially a class derived from GraphContainer).
            Owner<GraphContainer> owner;
            try {
                owner = std::forward<Functor&&>(func)(getGraphContainerOwnerServices());
            } catch (...) {
            }
            // Validate then add the new GraphContainer.
            // Upon failure, validateAndAddGraphContainer will destroy the GraphContainer (if any).
            GraphContainer* container = validateAndAddGraphContainer(std::move(owner));
            if (container) {
                return *container;
            }
        }
        // Upon any failure, return an invalid GraphContainer:
        return GraphContainer::getInvalid();
    }

    /// \brief The signature for the custom pointer deleter of a pointee \p p.
    ///
    /// This is the custom deleter type used by the
    /// \ref Workspace::addGraphContainer(DeleterFunc<GraphContainer>) alias method.
    ///
    /// \tparam T the storage type used for the owned GraphContainer object.
    /// \param [in] p a pointer to the owned object to destruct. Can be nullptr.
    template <typename T>
    using DeleterFunc = void (*)(T* p);

    /// \brief Aliases for adding an instance of a GraphContainer base class, using an
    /// optional custom deleter function.
    /// These alias methods call the generic addGraphContainerT<> template method, passing a
    /// Functor that creates a new instance of a GraphContainer base class.
    /// \{
    GraphContainer& addGraphContainer() noexcept;
    GraphContainer& addGraphContainer(DeleterFunc<GraphContainer> deleter) noexcept;
    /// \}

    /// \brief Delete the \ref GraphContainer referred by \p graphContainer and remove it from
    /// this Workspace. Once deleted, any attempt to access the methods of \p graphContainer
    /// will produce undefined behavior.
    ///
    /// \return true if \p graphContainer is owned by this Workspace and it has been successfully
    /// deleted and removed; false otherwise.
    bool deleteGraphContainer(GraphContainer& graphContainer) noexcept;

    /// \brief Get the Watchpoint registered for the Amino::TypeId \p typeId.
    ///
    /// \param typeId The Amino::TypeId for which to get the Watchpoint.
    ///
    /// \return The Watchpoint registered for \p typeId or nullptr if none is registered for it.
    const Watchpoint* getWatchpoint(const Amino::TypeId& typeId) const noexcept;

    /// \brief Get the watchpoint layout factory.
    /// \return The watchpoint layout factory.
    /// \{
    WatchpointLayoutFactory const& getWatchpointLayoutFactory() const noexcept;
    WatchpointLayoutFactory&       getWatchpointLayoutFactory() noexcept;
    /// \}

protected:
    /// \brief Report a message from this Workspace and call the Workspace's onReportedMessage
    /// notification method. The source of the reported message will be set to
    /// MessageSource::kWorkspace.
    ///
    /// \param category The message category.
    /// \param message  The message itself.
    void reportMessage(MessageCategory category, const Amino::String& message) const noexcept;

private:
    /// \brief The method called by the Workspace to notify the deriving class that a message
    /// was reported by this Workspace, its \ref BifrostGraph::Executor::Library,
    /// a \ref BifrostGraph::Executor::GraphContainer or a Job.
    /// Bifrost can call this method asynchronously in some situations such as reporting
    /// information when loading configuration files, loading definition files, loading a
    /// compound, terminating a job etc.
    /// If overridden, the implementation of this method must be thread safe and
    /// must not throw any exception.
    ///
    /// \param source   The source of this message.
    /// \param category The message category.
    /// \param message  The message itself.
    ///
    /// \note The default implementation writes information (MessageCategory::kInfo)
    /// and warning (MessageCategory::kWarning) messages to the output stream object std::cout,
    /// and writes error (MessageCategory::kError) messages to the output stream object std::cerr.
    ///
    virtual void onReportedMessage(MessageSource        source,
                                   MessageCategory      category,
                                   const Amino::String& message) const noexcept;

    /// \brief Get access to the internal GraphContainer ownership services.
    ///
    /// \pre This Workspace must be valid (\ref BifrostGraph::Executor::Workspace::isValid).
    /// Calling this method on an invalid Workspace will produce undefined behavior.
    ///
    /// \note This is an internal method used by the addGraphContainerT template method.
    /// This method should not be called directly.
    ///
    Private::IGraphContainerOwner& getGraphContainerOwnerServices() noexcept;

    /// \brief Validate then add the given Owner<GraphContainer> to this Workspace.
    /// The Owner<> itself is added to the GraphContainer storage of this Workspace,
    /// not only the pointed GraphContainer, since the Owner<> also captures the custom pointer
    /// deleter (if any) needed to destroy the pointed GraphContainer.
    ///
    /// \post If this method succeeds then \p owner is moved into the GraphContainer
    /// storage of this Workspace; otherwise no GraphContainer is added to this Workspace
    /// and \p owner is reset, deleting its owned GraphContainer (if any).
    ///
    /// \param [in] owner the Owner<GraphContainer> to be added to this Workspace.
    /// \return A pointer to the added GraphContainer if this Workspace is valid,
    /// and if \p owner is not empty, if it owns a valid GraphContainer and if it
    /// could be added to the GraphContainer storage of this Workspace; nullptr otherwise.
    ///
    /// \note This is an internal method used by the addGraphContainerT template method.
    /// This method should not be called directly.
    ///
    GraphContainer* validateAndAddGraphContainer(Owner<GraphContainer>&& owner) noexcept;

public:
    //---------------------------------------------------------------------------------------------
    // IRestrictedWorkspaceServices
    //---------------------------------------------------------------------------------------------

    /// \brief Obtain an interface giving access to private Workspace services.
    ///
    /// \pre This Workspace must be valid (\ref BifrostGraph::Executor::Workspace::isValid).
    /// Calling this method on an invalid Workspace will produce undefined behavior.
    /// \note This is an internal method used by the Executor SDK.
    ///
    /// \return A reference to the IRestrictedWorkspaceServices interface of this Workspace.
    ///
    /// \{
    const Private::IRestrictedWorkspaceServices& getRestrictedServices() const noexcept;
    Private::IRestrictedWorkspaceServices&       getRestrictedServices() noexcept;
    /// \}

private:
    /// Disabled
    /// \{
    Workspace(const Workspace&)            = delete;
    Workspace(Workspace&&)                 = delete;
    Workspace& operator=(const Workspace&) = delete;
    Workspace& operator=(Workspace&&)      = delete;
    /// \}

private:
    friend class Private::WorkspaceImpl;
    Internal::PropagateConstPtr<Private::WorkspaceImpl, Internal::Owned::kYes> m_impl;
    static Workspace                                                           s_invalid;
};
///@}
} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_WORKSPACE_H

//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file Library.h
/// \brief BifrostGraph Executor Library.
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_LIBRARY_H
#define BIFROSTGRAPH_EXECUTOR_LIBRARY_H

#include <BifrostGraph/Executor/internal/ExecutorExport.h>
#include <BifrostGraph/Executor/internal/PropagateConstPtr.h>

#include <BifrostGraph/Executor/Factory.h>
#include <BifrostGraph/Executor/Owner.h>
#include <BifrostGraph/Executor/Types.h>

#include <Amino/Core/String.h>

//-------------------------------------------------------------------------------------------------
// Forward declarations
//-------------------------------------------------------------------------------------------------

namespace BifrostGraph {
namespace Executor {

class Workspace;

namespace Private {
class LibraryImpl;
class IRestrictedLibraryServices;
} // namespace Private

/// \ingroup BifrostGraphExecutor

//-------------------------------------------------------------------------------------------------
// CLASS Library
//-------------------------------------------------------------------------------------------------

/// \brief A Library of types and node definitions that can be used by Bifrost.
///
/// \details Access to types and node definitions is provided through a Library.
/// Types and node definitions are added to the Library by loading resource files.
///
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL Library final {
protected:
    //---------------------------------------------------------------------------------------------
    // Initialization
    //---------------------------------------------------------------------------------------------

    /// \brief Construct a Library with the given name.
    ///
    /// If an error occurs during the construction of this Library, or its underlying
    /// Amino::Context or Amino::Library, then \ref BifrostGraph::Executor::Library::isValid
    /// will return false and all future operations on the Library will fail.
    ///
    /// This constructor is private to force the usage of factory functions
    /// \ref BifrostGraph::Executor::makeOwner (see Factory.h) to create it.
    ///
    /// \param [in] name    An optional name for the Library.
    explicit Library(const Amino::String& name) noexcept;

    /// \brief Constructor that leaves the Library in an uninitialized state.
    ///
    /// After this constructor returns, the method \ref BifrostGraph::Executor::Library::isValid
    /// will return false and all future operations on the Library will fail.
    ///
    /// \param [in] uninitialized  an Uninitialized enum value.
    /// \warning This constructor is used internally by the Executor. Use with caution.
    explicit Library(Uninitialized uninitialized) noexcept;

    /// \brief Allow the makeOwner<> factory functions to access the constructors of this class.
    EXECUTOR_DECLARE_MAKE_OWNER_FRIENDSHIP();

    /// \brief Allow the \ref Workspace class to access the constructors of a Library.
    friend class Workspace;

public:
    /// \brief Destructor.
    ~Library() noexcept;

    /// \brief Check if this Library has been successfully initialized.
    ///
    /// If an error occurs during the construction of a Library, isValid() will
    /// return false and all future operations on the Library will fail.
    ///
    /// \return true if this Library has been successfully initialized and is ready to
    /// be used; false otherwise.
    bool isValid() const noexcept;

    /// \brief Get a statically allocated Library that is uninitialized, invalid and not
    /// owned by any Workspace. Any operation on this instance will always fail and
    /// \ref Library::isValid will return false.
    static Library& getInvalid() noexcept;

    //---------------------------------------------------------------------------------------------
    // Resources Services
    //---------------------------------------------------------------------------------------------

    /// \brief Load into the Library the types, operators, terminal nodes and compounds
    /// found in a Bifrost definition JSON file, if the file has not already been loaded.
    ///
    /// \note If the Bifrost definition JSON file contains nodes that are not compounds, then each
    /// of these nodes is wrapped into a compound wrapper to make it executable. A compound wrapper
    /// is named by adding the suffix "_wrapper_compound" to the node's name being wrapped.
    ///
    /// \param [in] filePath  Path to a Bifrost definition JSON file.
    /// \param [out] nameList The list of fully qualified names of the public compounds loaded
    /// from the Bifrost definition JSON file designated by \p filePath. This returned list is
    /// filled even when the Bifrost definition JSON file was already loaded.
    /// \return true if the Bifrost definition JSON file designated by \p filePath was already
    /// loaded or if it has just been successfully loaded; false otherwise.
    bool loadDefinitionFile(const Amino::String& filePath, StringArray& nameList) noexcept;

    //---------------------------------------------------------------------------------------------
    // IRestrictedLibraryServices
    //---------------------------------------------------------------------------------------------

    /// \brief Obtain an interface giving access to private Library services.
    ///
    /// \pre This Library must be valid (\ref BifrostGraph::Executor::Library::isValid).
    /// Calling this method on an invalid Library will produce undefined behavior.
    /// \note This is an internal method used by the Executor SDK.
    ///
    /// \return A reference to the IRestrictedLibraryServices interface of this Library.
    /// \{
    const Private::IRestrictedLibraryServices& getRestrictedServices() const noexcept;
    Private::IRestrictedLibraryServices&       getRestrictedServices() noexcept;
    /// \}

private:
    /// Disabled
    /// \{
    Library(const Library&)            = delete;
    Library(Library&&)                 = delete;
    Library& operator=(const Library&) = delete;
    Library& operator=(Library&&)      = delete;
    /// \}

private:
    Internal::PropagateConstPtr<Private::LibraryImpl, Internal::Owned::kYes> m_impl;
    static Library                                                           s_invalid;
};

} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_LIBRARY_H

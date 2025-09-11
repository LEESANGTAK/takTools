//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file  Utility.h
/// \brief Helpers functions
/// \note The contents of this file belong to a feature that is still
/// under development, and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_UTILITY_H
#define BIFROSTGRAPH_EXECUTOR_UTILITY_H

#include <BifrostGraph/Executor/internal/ExecutorExport.h>
#include <BifrostGraph/Executor/internal/PropagateConstPtr.h>

#include <BifrostGraph/Executor/Factory.h>
#include <BifrostGraph/Executor/Types.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Core/String.h>

#include <cstdint>

namespace Amino {
class Type;
class Value;
} // namespace Amino

namespace BifrostGraph {
namespace Executor {
namespace Utility {

/// \ingroup BifrostGraphExecutor
/// \defgroup BifrostGraphExecutorUtility BifrostGraph Executor Utility
/// \brief BifrostGraph Executor utility functions and helpers.
///@{

/// \brief Return the fully qualified name of a given type.
/// An empty string is returned to indicate any encountered error.
/// \param [in] type The type whose fully qualified name is queried.
/// \return The fully qualified name of the given type. If the given type is
/// invalid, an empty string is returned.
BIFROSTGRAPH_EXECUTOR_SHARED_DECL Amino::String getTypeName(const Amino::Type& type) noexcept;

/// \brief Given a type whose kind is an array, this function finds the type of
/// the innermost element whose kind is not an array, and it returns its fully
/// qualified name. For example, if the given type is an array of arrays of
/// floats, then "float" is returned.
/// Given a type whose kind is not an array, this function returns its fully
/// qualified name.
/// \param [in] type The array type whose innermost element's type is queried.
/// \return The fully qualified name of the innermost element type of a given
/// array type, or the fully qualified name of a given type that is not an array
/// type. If the given type or any encountered type during traversal is invalid,
/// an empty string is returned.
BIFROSTGRAPH_EXECUTOR_SHARED_DECL Amino::String getInnermostElementTypeName(
    const Amino::Type& type) noexcept;

/// \brief Check if a given type is of array kind.
/// \param [in] type The type whose kind is checked.
/// \return true is the given type is valid and of array kind; false otherwise.
BIFROSTGRAPH_EXECUTOR_SHARED_DECL bool isArrayType(const Amino::Type& type) noexcept;

/// \brief Get the value of an environment variable.
///
/// \note This function is thread-safe as long as the host environment is not modified by
/// another function (like std::setenv, std::unsetenv or std::putenv).
///
/// \param [in] evName The name of the environment variable.
/// \return An empty string if the environment variable is unset; the value of the environment
/// variable otherwise.
BIFROSTGRAPH_EXECUTOR_SHARED_DECL Amino::String getEnv(const Amino::String& evName) noexcept;

/// \brief Get the boolean value of an environment variable.
///
/// If the environment variable is unset, false is returned. If the environment variable is set,
/// then the leading and trailing whitespaces from its value are first discarded, then if the
/// result is "0", false is returned, otherwise true is returned.
///
/// \note This function is thread-safe as long as the host environment is not modified by
/// another function (like std::setenv, std::unsetenv or std::putenv).
///
/// \param [in] evName The name of the environment variable.
/// \return false if the environment variable is "0" or unset; true otherwise.
BIFROSTGRAPH_EXECUTOR_SHARED_DECL bool getEnvBool(const Amino::String& evName) noexcept;

/// \brief Get the integer value of an environment variable.
///
/// If the environment variable is unset then \p defaultValue is returned. If the environment
/// variable is set but its value cannot be converted to an int32 (if its value does not
/// represent an integer, or if its value is too big or too small to fit in an int32, or if
/// the conversion would have left some trailing characters that would not have been interpreted),
/// then \p defaultValue is returned. Otherwise, the integer value of the environment variable
/// is returned.
///
/// \note This function is thread-safe as long as the host environment is not modified by
/// another function (like std::setenv, std::unsetenv or std::putenv).
///
/// \param [in] evName The name of the environment variable.
/// \param [in] defaultValue The default value to use if the environment variable \p evName is unset
/// or if an error is detected when attempting to convert its value to an int32.
/// \return \p defaultValue if the environment variable is unset or if its value cannot be
/// converted to an int32; the integer value of the environment variable otherwise.
BIFROSTGRAPH_EXECUTOR_SHARED_DECL std::int32_t getEnvInt(const Amino::String& evName,
                                                         std::int32_t defaultValue) noexcept;

// clang-format off
/// \brief ConfigEnv represents a map containing (key, values) pairs describing the current
/// Bifrost configuration from known environment variables.
///
/// <table>
///     <tr><th> The Environment Variable Name: </th><th> The (key, values) Pair: </th>
///     <tr>
///         <td> BIFROST_DISABLE_PACKS </td>
///         <td>
///             <code> ("bifrost_disable_packs", StringArray) </code><br>
///             <p>
///                 No (key,values) pair is added to the ConfigEnv if the EV is
///                 not set. Otherwise, `values` contains the names of the
///                 Bifrost packs to be disabled, as listed in the environment
///                 variable. The empty pack names and duplicate pack names are
///                 eliminated.
///             </p>
///         </td>
///     </tr>
///     <tr>
///         <td> BIFROST_LIB_CONFIG_FILES </td>
///         <td>
///             <code> ("bifrost_pack_config_files", StringArray) </code><br>
///             <p>
///                 No (key,values) pair is added to the ConfigEnv if the EV is
///                 not set. Otherwise, `values` contains the paths to the
///                 Bifrost config files to be loaded by Bifrost, as listed in
///                 the environment variable. Empty pathnames are eliminated.
///                 Duplicates of identical pathnames are eliminated, but no
///                 attempt is made to eliminate duplicates of non-identical
///                 pathnames that are equivalent (e.g. /dir/a.json and /dir/./a.json,
///                 or different symbolic links that refer to the same file).
///             </p>
///         </td>
///     </tr>
/// </table>
///
// clang-format on
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL ConfigEnv final {
protected:
    /// \brief Constructor.
    /// If an error occurs during the construction of this ConfigEnv, or while parsing
    /// the environnement variables, then \ref BifrostGraph::Executor::Utility::ConfigEnv::isValid
    /// will return false and all future operations on this ConfigEnv will fail.
    ///
    /// This constructor is protected to force the usage of factory functions
    /// \ref BifrostGraph::Executor::makeOwner (see \file Factory.h) to create it.
    ConfigEnv() noexcept;

public:
    /// \brief Allow the makeOwner<> factory functions to access the constructor of this class.
    EXECUTOR_DECLARE_MAKE_OWNER_FRIENDSHIP();

    /// \brief Destructor.
    ~ConfigEnv() noexcept;

    /// \brief Check if this ConfigEnv has been successfully initialized.
    /// \note If not valid, all future operations on this ConfigEnv will fail.
    /// \return true if this ConfigEnv has been successfully initialized and is ready to
    /// be used; false otherwise.
    bool isValid() const noexcept;

    /// \brief Check if a known Bifrost environment variable with name \p key is set.
    /// \param [in] key The name of an environment variable
    /// \return true if this ConfigEnv is valid and if \p key is the name of a known Bifrost
    /// environment variable and if this environment variable is set; false otherwise.
    bool hasKey(const Amino::String& key) const noexcept;

    /// \brief Get the string values for a known Bifrost environment variable with name \p key.
    /// \param [in] key The name of an environment variable
    /// \return The string values of a known Bifrost environment variable with name \p key if
    /// it is set and if this ConfigEnv is valid; an empty array if \p key is not a known Bifrost
    /// environment variable, or if this environment variable is not set, or if this ConfigEnv is
    /// invalid.
    const StringArray& values(const Amino::String& key) const noexcept;

private:
    ConfigEnv(const ConfigEnv&)            = delete;
    ConfigEnv(ConfigEnv&&)                 = delete;
    ConfigEnv& operator=(const ConfigEnv&) = delete;
    ConfigEnv& operator=(ConfigEnv&&)      = delete;

private:
    class Impl;
    BifrostGraph::Executor::Internal::PropagateConstPtr<Impl, Internal::Owned::kYes> m_impl;
};

/// \brief Get the library prefix to be used on the current platform.
///
/// On windows, the library prefix is just an empty string, while on OSX and Linux the prefix
/// "lib" is used.
///
/// \return The library prefix to be used on the current platform.
BIFROSTGRAPH_EXECUTOR_SHARED_DECL Amino::String getLibraryPrefix() noexcept;

/// \brief Get the library extension to be used on the current platform.
///
/// On windows, the library extension is ".dll", on Linux it is ".so" and on OSX the extension
/// ".dylib" is used.
///
/// \return The library extension to be used on the current platform.
BIFROSTGRAPH_EXECUTOR_SHARED_DECL Amino::String getLibraryExtension() noexcept;

/// \brief Convert a path to a Bifrost normalized path.
///
/// Take the longest leading sequence of elements in \p path that exist, if any,
/// convert it to an absolute pathname that resolves to the same directory entry as this
/// sequence and whose resolution does not involve ".", "..", or symbolic links. Then
/// append the remaining sequence of elements in \p path that do not exist, removing the
/// unnecessary ".", ".." and directory separators from this trailing sequence.
///
/// \note A normalized path in Bifrost uses the generic directory separator '/' (forward slash).
///
/// \param [in] path The path to normalize.
/// \return A Bifrost normalized path.
BIFROSTGRAPH_EXECUTOR_SHARED_DECL Amino::String getNormalizedPath(
    const Amino::String& path) noexcept;

///@}
} // namespace Utility
} // namespace Executor
} // namespace BifrostGraph

#endif

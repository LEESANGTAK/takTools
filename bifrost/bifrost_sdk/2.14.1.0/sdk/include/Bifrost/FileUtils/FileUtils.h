//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

//
/// \file FileUtils.h
///
/// \brief File utilities.
///

#ifndef BIFROST_FILE_UTILS_H
#define BIFROST_FILE_UTILS_H

#include "FileUtilsExport.h"

#include <Amino/Core/String.h>
#include <Amino/Core/StringView.h>

namespace Bifrost {

namespace FileUtils {

/// \defgroup BifrostFileUtils Bifrost File Utilities
/// \brief File utilities.
///@{
/// \brief Checks if a path is absolute.
///
/// \param [in] path The path to check.
/// \return True if absolute, false otherwise.
FILE_UTILS_DECL bool isAbsolute(Amino::StringView path);

/// \brief Creates the directories in path that do not exist.
///
/// \param [in]  path The path of directories to create
/// \param [out] errorMessage On failure, errorMessage will be set to a
/// human-readable error message
/// \return True on success, false otherwise.
FILE_UTILS_DECL bool createDirectories(Amino::StringView path,
                                       Amino::String*    errorMessage = nullptr);

/// \brief Returns the current path.
///
/// The current path as returned by many operating systems is a dangerous global
/// variable. It may be changed unexpectedly by a third-party or system library
/// functions, or by another thread.
///
/// \param [out] currentPath Will be set to the current path
/// \param [out] errorMessage On failure, errorMessage will be set to a
/// human-readable error message
/// \return True on success, false otherwise.
FILE_UTILS_DECL bool currentPath(Amino::String& currentPath, Amino::String* errorMessage = nullptr);

/// \brief Returns the parent path of path.
/// The input is first processed by \ref makePreferred.
/// Then the extraction follows C++17 std::filesystem.
///
/// \code{.unparsed}
/// std::cout << extractParentPath("/foo/bar.txt"); // outputs "/foo"
/// std::cout << extractParentPath("/foo/bar");     // outputs "/foo"
/// std::cout << extractParentPath("/foo/bar/");    // outputs "/foo/bar"
/// std::cout << extractParentPath("/");            // outputs "/"
/// std::cout << extractParentPath(".");            // outputs ""
/// std::cout << extractParentPath("..");           // outputs ""
/// \endcode
///
/// \param [in] path The input path.
/// \return The parent path.
FILE_UTILS_DECL Amino::String extractParentPath(Amino::StringView path);

/// \brief Convert directory separator characters in the given string to the
/// operating system's preferred character. (For unix systems this is a forward
/// slash, and for Windows, a backslash)
///
/// \param [in] path The path to convert
/// \return The converted path
FILE_UTILS_DECL Amino::String makePreferred(Amino::StringView path);

/// \brief Create a file path from a directory and an filename in an operating system / independent way
///
/// \param [in] directory directory name
/// \param [in] filename file name
/// \return constructed file path
FILE_UTILS_DECL Amino::String filePath(Amino::StringView directory, Amino::StringView filename);

/// \brief Construct a file name with the specified frame number and extension.
/// If the file name contains # or @ they will be replaced with the given frame
/// number. # will reserve 4 digits for the frame number, whereas @ will reserve
/// just one. If a target file extension is specified it will be enforced, otherwise
/// will be ignored.
/// \param [in] baseName The file name.
/// \param [in] frame The frame.
/// \param [in] targetExtension The desired extension of the file.
/// \return The baseName, including the specified frame number and file extension.
FILE_UTILS_DECL Amino::String filename(Amino::StringView baseName,
                                       long long         frame,
                                       Amino::StringView targetExtension);

/// \brief Get the filename (with extension) from a file path.
/// The input is first processed by \ref makePreferred.
/// Then the extraction follows C++17 std::filesystem.
/// \code{.unparsed}
/// std::cout << extractFilename("/foo/bar.txt"); // outputs "bar.txt"
/// std::cout << extractFilename("/foo/bar");     // outputs "bar"
/// std::cout << extractFilename("/foo/bar/");    // outputs ""
/// std::cout << extractFilename("/");            // outputs ""
/// std::cout << extractFilename(".");            // outputs "."
/// std::cout << extractFilename("..");           // outputs ".."
/// \endcode
/// \param [in] filePath The file path.
/// \return The filename.  The file name can be empty, ".", or "..".
///     If no directory separators are found then filePath is returned.
FILE_UTILS_DECL Amino::String extractFilename(Amino::StringView filePath);

/// \brief Verify if a file path exists.
/// \param [in] filePath The file path.
/// \param [out] out_errorMessage On failure, errorMessage will be set to a
///              human-readable error message
/// \return True if the file path exists
FILE_UTILS_DECL bool filePathExists(Amino::StringView filePath,
                                    Amino::String*    out_errorMessage = nullptr);

/// \brief Return the valid relative path of the input path with respect to baseDirectory
///
/// Note: If a file path (instead of directory) is passed in baseDirectory
/// parameter the behavior is undefined
///
/// \param [in]  path The path that needs to be processed.
/// \param [in]  baseDirectory Base directory used to build the relative path (relative to).
/// \return Valid relative path with respect to baseDirectory.
FILE_UTILS_DECL Amino::String getRelativePath(Amino::StringView path,
                                              Amino::StringView baseDirectory);

/// \brief Verify if a path exists.
///
/// This will return true if the path exists no matter whether it is a directory, file, symlink etc.
///
/// \param [in] path The path.
/// \param [out] errorMessage On failure, errorMessage will be set to a
///              human-readable error message
/// \return True if the path exists.
FILE_UTILS_DECL bool exists(Amino::StringView path, Amino::String* errorMessage = nullptr);

/// \brief Returns the directory location suitable for temporary files.
/// \param [out] tempDirectoryPath Will be set to temporary directory path.
/// \param [out] errorMessage On failure, errorMessage will be set to a
///              human-readable error message
/// \return True on success, false otherwise.
FILE_UTILS_DECL bool tempDirectoryPath(Amino::String& tempDirectoryPath,
                                       Amino::String* errorMessage = nullptr);

/// Recursively deletes the contents on `path`.
///
/// Deletes the contents of `path` (if it is a directory) and the contents of all
/// its subdirectories, recursively, then deletes `path` itself as if by repeatedly
/// applying the POSIX remove. Symlinks are not followed (symlink is removed, not
/// its target).
///
/// \param [in] path The path.
/// \param [out] errorMessage On failure, errorMessage will be set to a
///              human-readable error message
/// \return True on success, false otherwise.
FILE_UTILS_DECL bool removeAll(Amino::StringView path, Amino::String* errorMessage = nullptr);

///@}
} // namespace FileUtils
} // namespace Bifrost

#endif // BIFROST_FILE_UTILS_H

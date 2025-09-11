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
/// \file FileTypes.h
///
/// \brief Graph file types.
///

#ifndef BIFROST_FILE_UTIL_TYPES_H
#define BIFROST_FILE_UTIL_TYPES_H

#include <Bifrost/FileUtils/FileTypes.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Core/String.h>
#include <Amino/Core/internal/ConfigMacros.h>
#include <Amino/Cpp/Annotate.h>
#include <Bifrost/Object/Object.h>

#define BIFROST_IGNORE_NAMESPACE AMINO_ANNOTATE("Amino::Namespace ignore")
namespace Bifrost BIFROST_IGNORE_NAMESPACE {
#undef BIFROST_IGNORE_NAMESPACE

namespace File {

namespace Common {

struct AMINO_ANNOTATE("Amino::Struct") FileOperationSingleResult {
    /// Objects read or written
    Amino::Ptr<Amino::Array<Amino::Ptr<Bifrost::Object>>> objects{Amino::PtrDefaultFlag{}};

    /// True if the file operation succeeded
    bool success{};
};

struct AMINO_ANNOTATE("Amino::Struct") FileOperationMultiResults {
    /// Objects read or written
    Amino::Ptr<Amino::Array<Amino::Ptr<Bifrost::Object>>> meshes{Amino::PtrDefaultFlag{}};
    Amino::Ptr<Amino::Array<Amino::Ptr<Bifrost::Object>>> points{Amino::PtrDefaultFlag{}};
    Amino::Ptr<Amino::Array<Amino::Ptr<Bifrost::Object>>> strands{Amino::PtrDefaultFlag{}};
    Amino::Ptr<Amino::Array<Amino::Ptr<Bifrost::Object>>> volumes{Amino::PtrDefaultFlag{}};

    /// True if the file operation succeeded
    bool success{};
};

enum class AMINO_ANNOTATE("Amino::Enum") FileOperationKind { ReadFile, WriteFile };

} // namespace Common

namespace Project {

struct AMINO_ANNOTATE("Amino::Struct") SceneInfo {
    Amino::String scene;             /**< Scene file name */
    Amino::String scene_directory;   /**< Scene directory path */
    Amino::String project_directory; /**< Project directory path */
    bool          has_project;       /**< Define if a project exists */
};

} // namespace Project

} // namespace File

// clang-format off
} // namespace Bifrost
// clang-format on

#endif

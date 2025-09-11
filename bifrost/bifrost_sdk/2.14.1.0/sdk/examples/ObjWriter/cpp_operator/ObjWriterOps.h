//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file ObjWriterOps.h
/// \brief Save a mesh as an obj file.

#ifndef OBJ_WRITER_OPS_H
#define OBJ_WRITER_OPS_H

#include "ObjWriterOpsExport.h"
#include <Bifrost/Object/Object.h>
#include <Amino/Core/String.h>
#include <Amino/Cpp/Annotate.h>

namespace Examples {
namespace GeoSDK {

/// \brief Simple node to export a bifrost mesh as an obj file.
///
/// \param [in] mesh The Bifrost mesh geometry object to export.
/// \param [in] filename Destination file.
/// \return If the operation succeeded or not.
OBJ_WRITER_OPS_DECL
bool WriteObj(const Bifrost::Object& mesh, const Amino::String &filename)
    AMINO_ANNOTATE("Amino::Node outName=WriteObj");

} // namespace GeoSDK
} // namespace Examples

#endif // OBJ_WRITER_OPS_H

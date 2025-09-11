//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file MeshWeldUVOps.h
/// \brief Mesh weld UVs operation.

#ifndef MESH_WELD_UV_OPS_H
#define MESH_WELD_UV_OPS_H

#include "MeshWeldUVOpsExport.h"

#include <Bifrost/Object/Object.h>

#include <Amino/Cpp/Annotate.h>

namespace Examples {
namespace GeoSDK {

MESH_WELD_UV_OPS_DECL
void weld_uvs(Bifrost::Object& mesh            AMINO_ANNOTATE("Amino::InOut outName=out_mesh"),
              float tolerance                  AMINO_ANNOTATE("Amino::Port value=0.1"),
              Amino::String const& uv_set_name AMINO_ANNOTATE("Amino::Port value=face_vertex_uv"))
    AMINO_ANNOTATE("Amino::Node");

} // namespace GeoSDK
} // namespace Examples

#endif // MESH_WELD_UV_OPS_H

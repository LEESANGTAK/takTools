//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file MeshAreaOps.h
/// \brief Mesh area computation operator.

#ifndef MESH_AREA_OPS_H
#define MESH_AREA_OPS_H

#include "MeshAreaOpsExport.h"

#include <Bifrost/Object/Object.h>

#include <Amino/Cpp/Annotate.h>

namespace Examples {
namespace GeoSDK {

/// \brief Enum to select the area computation method.
///
/// Newell mode is from: Sunday, Daniel, Fast Polygon Area and Newell Normal Computation,
///                      Journal of Graphics Tools, 2002.
///
/// Shoelace mode is from: Shoelace Formula - Wikipedia -
///                        https://en.wikipedia.org/wiki/Shoelace_formula
///
/// FanOut mode is from: Hill, J.S., Computer Graphics, McMillan, 1990.
enum class AMINO_ANNOTATE("Amino::Enum") MeshAreaComputeMode { Newell, Shoelace, FanOut };

/// \brief Compute polygon mesh area.
///
/// \param [in] mesh The Bifrost mesh geometry object to compute the area of.
/// \param [in] mode The area computation method to use.
/// \return Area of the mesh.
MESH_AREA_OPS_DECL
float compute_mesh_area(Bifrost::Object const& mesh, MeshAreaComputeMode mode)
    AMINO_ANNOTATE("Amino::Node outName=mesh_area");

} // namespace GeoSDK
} // namespace Examples

#endif // MESH_AREA_OPS_H

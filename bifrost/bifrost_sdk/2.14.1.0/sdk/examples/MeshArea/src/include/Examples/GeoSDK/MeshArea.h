//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file MeshArea.h
/// \brief Class to help compute the area of a mesh.

#ifndef MESH_AREA_H
#define MESH_AREA_H

#include "MeshAreaExport.h"

#include <Bifrost/Geometry/GeoPropertyKey.h>
#include <Bifrost/Math/Types.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/Array.h>

namespace Examples {
namespace GeoSDK {

class MESH_AREA_DECL FaceMeshView {
    /// \brief  Class to access the underlying data of a Bifrost mesh object.
    /// \note   This class is for read-only access only.
public:
    FaceMeshView()                       = delete;
    FaceMeshView(FaceMeshView const&)    = delete;
    FaceMeshView(FaceMeshView&&)         = delete;
    FaceMeshView(Bifrost::Object&& mesh) = delete;
    explicit FaceMeshView(Bifrost::Object const& mesh);

public:
    /// \brief Compute the area of the mesh using the Newell method.
    /// \note: From Sunday, Daniel, Fast Polygon Area and Newell Normal Computation,
    ///        Journal of Graphics Tools, 2002..
    float computeAreaNewell() const;

    /// \brief Compute the area of the mesh using the Shoelace method.
    /// \note From: Shoelace Formula - Wikipedia - https://en.wikipedia.org/wiki/Shoelace_formula
    float computeAreaShoelace() const;

    /// \brief Compute the area of the mesh using the classic method.
    /// \note From: Hill, J.S., Computer Graphics, McMillan, 1990.
    float computeAreaFanOut() const;

private:
    // The necessary data to compute the area of the mesh.
    Amino::Array<Bifrost::Math::float3> const&    m_vertices;
    Amino::Array<Bifrost::Geometry::Index> const& m_faceOffsets;
    Amino::Array<Bifrost::Geometry::Index> const& m_faceVertices;
};

} // namespace GeoSDK
} // namespace Examples

#endif // MESH_AREA_H

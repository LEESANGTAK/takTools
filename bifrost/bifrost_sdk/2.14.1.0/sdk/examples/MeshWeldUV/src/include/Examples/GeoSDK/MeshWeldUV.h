//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file MeshWeldUV.h
/// \brief Class to help weld UVs of a mesh.

#ifndef MESH_WELD_UV_H
#define MESH_WELD_UV_H

#include "MeshWeldUVExport.h"

#include <Bifrost/Geometry/GeoPropertyKey.h>
#include <Bifrost/Math/Types.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/String.h>

namespace Examples {
namespace GeoSDK {

/// \brief  Class to weld UVs of a mesh.
class MESH_WELD_UV_DECL MeshUVWelder {
public:
    MeshUVWelder()                       = delete;
    MeshUVWelder(MeshUVWelder const&)    = delete;
    MeshUVWelder(MeshUVWelder&&)         = delete;
    MeshUVWelder(Bifrost::Object&& mesh) = delete;

    /// \brief Construct a welder for the given mesh.
    /// \param mesh The mesh to weld.
    explicit MeshUVWelder(Bifrost::Object& mesh);

public:
    /// \brief Welds the UVs of the mesh.
    /// \param tolerance UVs within this distance will be welded. The value is clamped to [0,1]
    /// \param uvSetName The name of the UV set to weld. If non-existent, the mesh is be unchanged.
    /// \pre The mesh passed into the welder must be a validate mesh.
    void weld(float tolerance, Amino::String const& uvSetName);

private:
    Bifrost::Object& m_mesh;

    void weld_impl(float tolerance, Amino::String const& uvSetName);
};

} // namespace GeoSDK
} // namespace Examples

#endif // MESH_WELD_UV_H

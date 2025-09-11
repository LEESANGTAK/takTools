//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include <Examples/GeoSDK/MeshWeldUV.h>

#include <Examples/GeoSDK/Float2Utils.h>

#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Geometry/GeoPropertyGuard.h>
#include <Bifrost/Geometry/Validator.h>

#include <Amino/Core/Any.h>

#include <vector>

using namespace Examples::Math;
using Bifrost::Geometry::Index;

Examples::GeoSDK::MeshUVWelder::MeshUVWelder(Bifrost::Object& mesh) : m_mesh(mesh) {}

void Examples::GeoSDK::MeshUVWelder::weld(float tolerance, Amino::String const& uvSetName) {
    tolerance = std::min(std::max(tolerance, 0.0F), 1.0F); // Clamp to [0, 1].

    weld_impl(tolerance, uvSetName);

    // The mesh should be valid after the weld operation.
    assert(Bifrost::Geometry::validateMesh(m_mesh));
}

void Examples::GeoSDK::MeshUVWelder::weld_impl(float tolerance, Amino::String const& uvSetName) {
    auto const kInvalidIndex = Bifrost::Geometry::kInvalidIndex;

    // Get pertinent data from the mesh.
    const auto pointCount =
        Bifrost::Geometry::getElementCount(m_mesh, Bifrost::Geometry::sPointComp);

    auto faceVertIndices =
        Bifrost::Geometry::getDataGeoPropValues<Index>(m_mesh, Bifrost::Geometry::sFaceVertex);

    // The face vertex indices are a canonical property of the mesh. Since it is a precondition
    // that the mesh is valid before being passed into this function, we can safely assume that
    // this pointer is valid.
    assert(faceVertIndices);

    // Get the UV data and indices from the mesh. Since the UV set is not a canonical property of
    // the mesh, we need to check they exist before proceeding.
    auto uvData = Bifrost::Geometry::getDataGeoPropValues<Bifrost::Math::float2>(m_mesh, uvSetName);
    if (!uvData) {
        return;
    }

    auto const uvSetIndicesName = Bifrost::Geometry::getGeoPropTargetName(m_mesh, uvSetName);

    // Get write access to the indices of the UVs through a property guard.
    // The indices are a range geo property that contains indices into the UV data array.
    //
    // The guard will extract the data array from the mesh, and provide non-const/write access to it.
    // Upon destruction, the guard will set the data back into the mesh. If there are no other
    // references to the data, they will be modified in-place and no copy-on-write will occur.
    // See Amino::MutablePtr
    auto uvIndicesGuard = Bifrost::Geometry::createRangeGeoPropGuard(m_mesh, uvSetIndicesName);
    if (!uvIndicesGuard) {
        return;
    }

    // If the UV is welded, the root index points to the UV that its welded to.
    // Otherwise, it points to itself.
    std::vector<Index> uvRootIndices(uvData->size());
    for (size_t i = 0; i < uvRootIndices.size(); ++i) {
        uvRootIndices[i] = static_cast<Index>(i);
    }

    // Map points to their associated UVs.
    std::vector<std::vector<Index>> pointToUv(pointCount);
    for (size_t faceVertIndex = 0; faceVertIndex < faceVertIndices->size(); ++faceVertIndex) {
        auto const pointIndex = (*faceVertIndices)[faceVertIndex];
        auto const uvIndex    = uvIndicesGuard.indices()[faceVertIndex];

        auto& uvs = pointToUv[pointIndex];

        // Multiple face vertices may reference the same UV.
        // Make sure the uv index is added only once.
        if (std::find(uvs.begin(), uvs.end(), uvIndex) == uvs.end())
            pointToUv[pointIndex].push_back(uvIndex);
    }

    // The indices of other UVs that are welded into this UV.
    std::vector<std::vector<Index>> uvWeldedIndices(uvData->size());

    size_t uniqueUVCount = uvData->size();
    for (auto& uvs : pointToUv) {
        if (uvs.size() < 2) continue; // If only one UV associated to the point, nothing to weld.

        // Weld UVs that are close to each other. Note this is done per-point because only UVs
        // that are associated to the same point can be welded. (i.e. the UV must be on a
        // texture seam)
        for (size_t i = 0; i < uvs.size(); ++i) {
            for (size_t j = i + 1; j < uvs.size(); ++j) {
                if (uvRootIndices[uvs[j]] != uvs[j]) continue; // already welded

                auto const dist = Examples::Math::dist((*uvData)[uvs[i]], (*uvData)[uvs[j]]);
                if (dist <= tolerance) {
                    uvRootIndices[uvs[j]] = uvRootIndices[uvs[i]];
                    uvWeldedIndices[uvs[i]].push_back(uvs[j]);
                    assert(uniqueUVCount > 0);
                    uniqueUVCount--;
                }
            }
        }
    }
    assert(uniqueUVCount > 0 && uniqueUVCount <= uvData->size());

    // Build a mapping from each element in the new array to an element in the original array.
    std::vector<Index> uvDstToSrc(uniqueUVCount);
    size_t             nextDstIndex = 0;
    for (size_t uvIndex = 0; uvIndex < uvData->size(); ++uvIndex) {
        if (uvRootIndices[uvIndex] == uvIndex) { // This is an unwelded uv.
            uvDstToSrc[nextDstIndex++] = static_cast<Index>(uvIndex);
        }
    }
    assert(nextDstIndex == uniqueUVCount);

    // Build a map from src to dst indices using the uvDstToSrc array to fill in entries for the
    // UVs that were not welded.
    std::vector<Index> uvSrcToDst(uvData->size(), kInvalidIndex);
    for (size_t uvDstIndex = 0; uvDstIndex < uvDstToSrc.size(); ++uvDstIndex) {
        auto uvSrcIndex        = uvDstToSrc[uvDstIndex];
        uvSrcToDst[uvSrcIndex] = static_cast<Index>(uvDstIndex);
    }

    // Then fill in the entries for the UVs that were welded.
    for (size_t uvSrcIndex = 0; uvSrcIndex < uvSrcToDst.size(); ++uvSrcIndex) {
        if (uvSrcToDst[uvSrcIndex] != kInvalidIndex) continue; // Skip unwelded UVs.

        // Get the src index of the root UV that this UV was welded to.
        auto const rootIndex = uvRootIndices[uvSrcIndex];

        // The root UV should be unwelded.
        assert(uvRootIndices[rootIndex] == rootIndex);

        // Get the dst index of the root UV.
        auto const dstRootIndex = uvSrcToDst[rootIndex];
        assert(dstRootIndex != kInvalidIndex);

        // Set this src UV index to the final dst index of the root UV.
        uvSrcToDst[uvSrcIndex] = dstRootIndex;
    }

    // Copy the UV values, and average the ones that were welded together.
    auto newUvData = Amino::newMutablePtr<Amino::Array<Bifrost::Math::float2>>(uniqueUVCount);
    for (size_t uvDstIndex = 0; uvDstIndex < uvDstToSrc.size(); ++uvDstIndex) {
        auto const srcIndex = uvDstToSrc[uvDstIndex];

        auto         uvValue = (*uvData)[srcIndex];
        unsigned int count   = 1;
        auto const&  weldedIndices = uvWeldedIndices[srcIndex];
        for (Index srcWeldedIndex : weldedIndices) {
            uvValue += (*uvData)[srcWeldedIndex];
            ++count;
        }
        uvValue /= static_cast<float>(count);
        (*newUvData)[uvDstIndex] = uvValue;
    }

    // Replace elements in the UV index array with indices to the newUvData array.
    for (auto& uvSrcIndex : uvIndicesGuard.indices()) {
        auto const uvDstIndex = uvSrcToDst[uvSrcIndex];
        assert(uvDstIndex != kInvalidIndex);
        uvSrcIndex = uvDstIndex;
    }

    // Set the new UV data into the mesh.
    Bifrost::Geometry::setDataGeoPropValues(uvSetName, newUvData.toImmutable(), m_mesh);
}

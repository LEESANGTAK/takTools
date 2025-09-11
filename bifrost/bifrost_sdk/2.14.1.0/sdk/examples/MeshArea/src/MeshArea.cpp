//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include <Examples/GeoSDK/MeshArea.h>

#include <Examples/GeoSDK/Float3Utils.h>

#include <Bifrost/Geometry/GeoProperty.h>

#include <algorithm>
#include <vector>

using namespace Examples::Math;
using Bifrost::Geometry::Index;
static_assert(std::is_same<Index, Amino::uint_t>::value, "Index type mismatch");

namespace {

/// \brief Compute the area of a polygon mesh by dividing the computation into batches.
///
/// The use of batches reduces the accumulation of floating point errors.
///
/// \param [in] computeAreaFunc The function to compute the area of a polygon.
/// \param [in] offsets The array of offsets into the face vertex array.
/// \return The area of the mesh.
template <typename FuncComputeArea>
float computeAreaHarness(FuncComputeArea const&     computeAreaFunc,
                         Amino::Array<Index> const& offsets) {
    // We did not record the number of faces in the FaceMeshView.
    // But we can use the size of the face offsets array to compute the number of faces.
    //
    // For a well-formed Bifrost mesh, the number of faces is the number of face offsets minus one.
    //
    // Note: A Bifrost geometry offset array is a prefix sum (cumulative sum) array with one entry
    // per face. Each entry is the start index of a face into the face vertex array. The extra entry
    // is the total number of vertices == the size of the face vertex array.
    if (offsets.empty()) {
        // This should not happen for a well-formed Bifrost mesh...
        return 0.0F;
    }

    size_t nbFaces = offsets.size() - 1;

    if (nbFaces == 0) {
        return 0.0F;
    }

    size_t batchSize = 256;

    auto area = 0.0F;
    for (size_t faceIndex = 0; faceIndex < nbFaces; faceIndex += batchSize) {
        auto  offsetStart = faceIndex;
        auto  offsetEnd   = offsetStart + std::min(batchSize, nbFaces - faceIndex);
        float subArea     = 0.0F;
        for (size_t offsetIndex = offsetStart; offsetIndex < offsetEnd; ++offsetIndex) {
            // Get the start index and number of vertices of the face.
            // The number of vertices of a face is the difference between two consecutive offsets.
            // index+1 entry will exist because offset arrays have one more entry than the number of
            // components they target (here the number of faces nbFaces).
            auto faceStart = offsets[offsetIndex];
            auto faceSize  = offsets[offsetIndex + 1] - faceStart;
            subArea += computeAreaFunc(faceStart, faceSize);
        }
        area += subArea;
    }
    return area;
}
} // namespace

//
// Implementation of FaceMeshView
//

Examples::GeoSDK::FaceMeshView::FaceMeshView(Bifrost::Object const& mesh)
    : m_vertices(*Bifrost::Geometry::getDataGeoPropValues<Bifrost::Math::float3>(
          mesh, Bifrost::Geometry::sPointPosition)),
      m_faceOffsets(
          *Bifrost::Geometry::getDataGeoPropValues<Index>(mesh, Bifrost::Geometry::sFaceOffset)),
      m_faceVertices(
          *Bifrost::Geometry::getDataGeoPropValues<Index>(mesh, Bifrost::Geometry::sFaceVertex)) {}

float Examples::GeoSDK::FaceMeshView::computeAreaNewell() const {
    auto computePolygonAreaFunc = [&](size_t faceStart, size_t faceSize) -> float {
        if (faceSize < 3) {
            return 0.0F;
        }

        Index const* faceVertices = &m_faceVertices[faceStart];

        // Ref.: Sunday, Daniel, Fast Polygon Area and Newell Normal Computation,
        //       Journal of Graphics Tools, 2002.
        //
        // Compute the Newell normal of the face.
        float xyArea = 0.0F;
        float yzArea = 0.0F;
        float zxArea = 0.0F;

        auto oneAreaPart = [&](size_t p, size_t c, size_t n) {
            Bifrost::Math::float3 const& vj = m_vertices[faceVertices[c]];
            Bifrost::Math::float3 const& vp = m_vertices[faceVertices[p]];
            Bifrost::Math::float3 const& vn = m_vertices[faceVertices[n]];
            xyArea += vj.x * (vn.y - vp.y);
            yzArea += vj.y * (vn.z - vp.z);
            zxArea += vj.z * (vn.x - vp.x);
        };

        // Note: Avoiding modulo computation in the main loop by doing explicit calls for the
        // first and last vertices.
        // First vertex
        // Note: The case faceSize == 0 is guarded against at the beginning of the function.
        oneAreaPart(faceSize - 1, 0, 1);
        // Middle vertices
        for (size_t j = 1; j < faceSize - 1; ++j) {
            oneAreaPart(j - 1, j, j + 1);
        }
        // Last vertex
        oneAreaPart(faceSize - 2, faceSize - 1, 0);

        // Add to the cumulative area.
        return 0.5F * mag(Bifrost::Math::float3{yzArea, zxArea, xyArea});
    };
    return computeAreaHarness(computePolygonAreaFunc, m_faceOffsets);
}

float Examples::GeoSDK::FaceMeshView::computeAreaShoelace() const {
    auto computePolygonAreaFunc = [&](size_t faceStart, size_t faceSize) -> float {
        if (faceSize < 3) {
            return 0.0F;
        }

        Index const* faceVertices = &m_faceVertices[faceStart];

        // Ref.: Shoelace Formula - Wikipedia - https://en.wikipedia.org/wiki/Shoelace_formula
        Bifrost::Math::float3 cumulatedArea = {0.0F, 0.0F, 0.0F};

        auto oneCrossPart = [&](size_t i, size_t j) {
            Bifrost::Math::float3 const& v1 = m_vertices[faceVertices[i]];
            Bifrost::Math::float3 const& v2 = m_vertices[faceVertices[j]];
            cumulatedArea += cross(v1, v2);
        };

        // Note: Avoiding modulo computation in the main loop by doing explicit calls for the
        // last vertex.
        // Note: The case faceSize == 0 is guarded against at the beginning of the function.
        for (size_t i = 0; i < faceSize - 1; ++i) {
            oneCrossPart(i, i + 1);
        }
        // Last vertex
        oneCrossPart(faceSize - 1, 0);

        // Add to the cumulative area.
        return 0.5F * mag(cumulatedArea);
    };
    return computeAreaHarness(computePolygonAreaFunc, m_faceOffsets);
}

float Examples::GeoSDK::FaceMeshView::computeAreaFanOut() const {
    auto computePolygonAreaFunc = [&](size_t faceStart, size_t faceSize) -> float {
        if (faceSize < 3) {
            return 0.0F;
        }

        // Ref.: Hill, J.S., Computer Graphics, McMillan, 1990.
        Index const*                 faceVertices  = &m_faceVertices[faceStart];
        Bifrost::Math::float3 const& v0            = m_vertices[faceVertices[0]];
        Bifrost::Math::float3        cumulatedArea = {0.0F, 0.0F, 0.0F};

        // Note: The case faceSize == 0 is guarded against at the beginning of the function.
        for (size_t i = 1; i < faceSize - 1; ++i) {
            Bifrost::Math::float3 const& v1 = m_vertices[faceVertices[i]];
            Bifrost::Math::float3 const& v2 = m_vertices[faceVertices[i + 1]];
            cumulatedArea += cross(v1 - v0, v2 - v0);
        }
        return 0.5F * mag(cumulatedArea);
    };
    return computeAreaHarness(computePolygonAreaFunc, m_faceOffsets);
}

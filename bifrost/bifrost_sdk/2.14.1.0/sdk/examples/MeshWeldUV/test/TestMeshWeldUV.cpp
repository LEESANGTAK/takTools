//-
// ===========================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// ===========================================================================
//+

#include <gtest/gtest.h>

#include <Examples/GeoSDK/MeshWeldUV.h>

#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Geometry/Primitives.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/Ptr.h>

#include <cmath>

using Bifrost::Geometry::Index;
using Bifrost::Math::float2;
using Bifrost::Math::float3;
using ArrayFloat2 = Amino::Array<float2>;
using ArrayFloat3 = Amino::Array<float3>;
using ArrayIndex  = Amino::Array<Index>;

namespace {

/// \brief Construct a plane mesh with 2 quads:
/// v3-------v4-------v5
/// |fv3  fv2|fv7  fv6|
/// |   f0   |   f1   |
/// |fv0  fv1|fv4  fv5|
/// v0------v1--------v2
/// \return A mutable pointer to the mesh.
auto createTestMesh() {
    auto mesh        = Bifrost::createObject();
    auto pos         = Amino::newClassPtr<ArrayFloat3>(6);
    auto faceVertex  = Amino::newClassPtr<ArrayIndex, Index>({0, 1, 4, 3, 1, 2, 5, 4});
    auto faceOffsets = Amino::newClassPtr<ArrayIndex, Index>({0, 4, 8});

    Bifrost::Geometry::populateMesh(pos, faceVertex, faceOffsets, *mesh);
    return mesh;
}

/// \brief Convenience function to add a UV set to a mesh.
/// \param uvIndices The indices into the uvData array. There should be one element per face-vertex.
/// \param uvData The UV coordinate data array.
/// \param uvName The name of the UV set.
/// \param mesh The mesh to add the UV set to.
void addUvSet(Amino::Ptr<ArrayIndex>  uvIndices,
              Amino::Ptr<ArrayFloat2> uvData,
              Amino::String const&    uvName,
              Bifrost::Object&        mesh) {
    auto const uvIndexName = Bifrost::Geometry::getGeoPropRangeName(uvName);
    auto       uvIndexObj  = Bifrost::createObject();
    Bifrost::Geometry::populateRangeGeoProperty(std::move(uvIndices),
                                                Bifrost::Geometry::sFaceVertexComp, *uvIndexObj);
    mesh.setProperty(uvIndexName, uvIndexObj.toImmutable());

    auto uvDataObj = Bifrost::createObject();
    Bifrost::Geometry::populateDataGeoProperty(float2{}, std::move(uvData), uvIndexName,
                                               *uvDataObj);
    mesh.setProperty(uvName, uvDataObj.toImmutable());
}

/// \brief Convenience function to get a UV set from a mesh.
/// \param uvName The name of the UV set.
/// \param mesh The mesh to get the UV set from.
/// \return The indices and UV coordinates of the UV set, or nullptrs if the UV set was not found.
auto getUvSet(Amino::String const& uvName, Bifrost::Object const& mesh) {
    auto uvData    = Bifrost::Geometry::getDataGeoPropValues<float2>(mesh, uvName);
    auto uvIndices = Bifrost::Geometry::getRangeGeoPropIndices(
        mesh, Bifrost::Geometry::getGeoPropTargetName(mesh, uvName));
    return std::make_pair(uvIndices, uvData);
}

/// \brief Almost equals for floating point numbers.
/// From: https://en.cppreference.com/w/cpp/types/numeric_limits/epsilon
/// \return true if the difference between x and y is within n ULPs, false otherwise.
template <class T>
std::enable_if_t<!std::numeric_limits<T>::is_integer, bool> equal_within_ulps(T           x,
                                                                              T           y,
                                                                              std::size_t n = 4) {
    // Since `epsilon()` is the gap size (ULP, unit in the last place)
    // of floating-point numbers in interval [1, 2), we can scale it to
    // the gap size in interval [2^e, 2^{e+1}), where `e` is the exponent
    // of `x` and `y`.

    // If `x` and `y` have different gap sizes (which means they have
    // different exponents), we take the smaller one. Taking the bigger
    // one is also reasonable, I guess.
    const T m = std::min(std::fabs(x), std::fabs(y));

    // Subnormal numbers have fixed exponent, which is `min_exponent - 1`.
    const int exp = m < std::numeric_limits<T>::min() ? std::numeric_limits<T>::min_exponent - 1
                                                      : std::ilogb(m);

    // We consider `x` and `y` equal if the difference between them is
    // within `n` ULPs.
    return std::fabs(x - y) <= static_cast<float>(n) * std::ldexp(std::numeric_limits<T>::epsilon(), exp);
}
} // namespace

namespace Bifrost {
namespace Math {

/// \brief Equality operator for float2.
/// \return True if a and b are within 4 ULPs of each other, false otherwise.
bool operator==(float2 const& a, float2 const& b) {
    return equal_within_ulps(a.x, b.x) && equal_within_ulps(a.y, b.y);
}

/// \brief Inequality operator for float2.
/// \return True if a and b are not within 4 ULPs of each other, false otherwise.
bool          operator!=(float2 const& a, float2 const& b) { return !(a == b); }

/// \brief Stream output operator for float2.
/// gtest will use this to print the float2 when an assertion fails.
std::ostream& operator<<(std::ostream& os, float2 const& a) {
    return os << "{" << std::setprecision(5) << a.x << ", " << a.y << "}";
}
} // namespace Math
} // namespace Bifrost

namespace Amino {

/// \brief Dump operator for Array<T>.
/// gtest will use this to print the array when an assertion fails.
template <typename T>
std::ostream& operator<<(std::ostream& os, Amino::Array<T> const& a) {
    os << "{";
    for (size_t i = 0; i < a.size(); ++i) {
        if (i != 0) os << ", ";
        os << a[i];
    }
    os << "}";
    return os;
}

/// \brief Equality operator for Array<T>.
/// gtest will use this to compare the arrays in the EXPECT_EQ macro.
template <typename T>
bool operator==(Array<T> const& a, Array<T> const& b) {
    if (a.size() != b.size()) return false;
    for (size_t i = 0; i < a.size(); ++i) {
        if (a[i] != b[i]) return false;
    }
    return true;
}

} // namespace Amino

TEST(TestMeshWeldUV, NonExistentUvSet) {
    // Test that a non-existent UV set is handled gracefully.
    auto mesh = createTestMesh();

    const Amino::String            uvSetName = "non_existent";
    Examples::GeoSDK::MeshUVWelder welder(*mesh);
    welder.weld(1.0F, uvSetName);
    auto outUvInfo = getUvSet(uvSetName, *mesh);
    EXPECT_EQ(outUvInfo.first, nullptr);
    EXPECT_EQ(outUvInfo.second, nullptr);
}

TEST(TestMeshWeldUV, NoSeams) {
    /* Test mesh:
            v3-------v4-------v5
            |fv3  fv2|fv7  fv6|
            |   f0   |   f1   |
            |fv0  fv1|fv4  fv5|
            v0------v1--------v2
    */
    auto mesh = createTestMesh();

    /* UV set with no seams. Nothing should be welded, even with a huge threshold.
            uv3-------uv4-------uv5
            |uvi3  uvi2|uvi7  uvi6|
            |     f0   |     f1   |
            |uvi0  uvi1|uvi4  uvi5|
            uv0------uv1--------uv2
    */
    Amino::String uvName = "no_seams";
    auto          uvData = Amino::newClassPtr<ArrayFloat2, float2>(
        {{0.0F, 0.0F}, {1.0F, 0.0F}, {2.0F, 0.0F}, {0.0F, 1.0F}, {1.0F, 1.0F}, {2.0F, 1.0F}});
    auto uvIndices = Amino::newClassPtr<ArrayIndex, Index>({0, 1, 4, 3,   // f0
                                                            1, 2, 5, 4}); // f1
    addUvSet(uvIndices, uvData, uvName, *mesh);

    Examples::GeoSDK::MeshUVWelder welder(*mesh);
    welder.weld(1.0F, uvName);
    auto outUvInfo = getUvSet(uvName, *mesh);

    EXPECT_EQ(*(outUvInfo.first), *uvIndices);
    EXPECT_EQ(*(outUvInfo.second), *uvData);
}

TEST(TestMeshWeldUV, Threshold) {
    /* Test mesh:
            v3-------v4-------v5
            |fv3  fv2|fv7  fv6|
            |   f0   |   f1   |
            |fv0  fv1|fv4  fv5|
            v0------v1--------v2
    */
    auto mesh = createTestMesh();

    /* UV set with one seam.
            uv3-------uv4  uv6-------uv5
            |uvi3  uvi2|  / uvi7  uvi6|
            |     f0   | /      f1    |
            |uvi0  uvi1|/uvi4     uvi5|
            uv0------uv1------------uv2
    */
    Amino::String uvName    = "one_seam";
    auto          uvData    = Amino::newClassPtr<ArrayFloat2, float2>({{0.0F, 0.0F}, // uv0
                                                                       {1.0F, 0.0F},
                                                                       {2.0F, 0.0F},
                                                                       {0.0F, 1.0F}, // uv3
                                                                       {1.0F, 1.0F},
                                                                       {2.0F, 1.0F},
                                                                       {1.1F, 1.0F}}); // uv6
    auto          uvIndices = Amino::newClassPtr<ArrayIndex, Index>({0, 1, 4, 3,       // f0
                                                                     1, 2, 5, 6});     // f1
    addUvSet(uvIndices, uvData, uvName, *mesh);

    // Test case 1: Very tiny threshold, should be a no-op.
    Examples::GeoSDK::MeshUVWelder welder(*mesh);
    welder.weld(0.01F, uvName);
    auto outUvInfo = getUvSet(uvName, *mesh);
    EXPECT_EQ(*(outUvInfo.first), *uvIndices);
    EXPECT_EQ(*(outUvInfo.second), *uvData);

    /* Test case 2: Larger threshold, should weld uv6 to uv4:
            uv3-------uv4-------uv5
            |uvi3  uvi2|uvi7  uvi6|
            |     f0   |    f1    |
            |uvi0  uvi1|uvi4  uvi5|
            uv0------uv1---------uv2
    */
    welder.weld(1.0F, uvName);
    outUvInfo = getUvSet(uvName, *mesh);

    ArrayIndex expectedIndices({0, 1, 4, 3,   // f0
                                1, 2, 5, 4}); // f1 (6 should be welded to 4)
    EXPECT_EQ(*(outUvInfo.first), expectedIndices);

    ArrayFloat2 expectedData(
        {{0.0F, 0.0F}, {1.0F, 0.0F}, {2.0F, 0.0F}, {0.0F, 1.0F}, {1.05F, 1.0F}, {2.0F, 1.0F}});
    EXPECT_EQ(*(outUvInfo.second), expectedData);
}

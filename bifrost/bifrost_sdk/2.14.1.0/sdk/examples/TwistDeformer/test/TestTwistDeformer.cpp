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

#include <Examples/GeoSDK/Float3Utils.h>
#include <Examples/GeoSDK/Float4x4Utils.h>
#include <Examples/GeoSDK/TwistDeformer.h>

#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Geometry/Primitives.h>
#include <Bifrost/Math/Types.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/Ptr.h>

using Bifrost::Math::float3;
using Examples::GeoSDK::TwistDeformer;
using namespace Examples::Math;

namespace {
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
/// \brief Equality operator for float3.
/// \return True if a and b are within 4 ULPs of each other, false otherwise.
bool operator==(float3 const& a, float3 const& b) {
    return equal_within_ulps(a.x, b.x) && equal_within_ulps(a.y, b.y) &&
           equal_within_ulps(a.z, b.z);
}
} // namespace Math
} // namespace Bifrost

TEST(TwistDeformer, Amount) {
    // Create a simple points geometry with 2 points.
    //
    // y
    // ^      v2
    // |
    // |
    // +-->x  v1
    auto positions =
        Amino::newClassPtr<Amino::Array<float3>, float3>({{1.0F, 0.0F, 0.0F}, {1.0F, 1.0F, 0.0F}});
    auto pointsGeo = [&]() {
        auto obj = Bifrost::createObject();
        Bifrost::Geometry::populatePointCloud(positions, *obj);
        return obj.toImmutable();
    }();

    auto twistGeo = [pointsGeo](auto amount) mutable {
        // Create a separate copy of the geometry for each test case to be tested in isolation.
        auto          pointsGeoCopy = pointsGeo;
        auto          pointsGeoMut  = pointsGeoCopy.toMutable();
        TwistDeformer twister(*pointsGeoMut);
        twister.deform(amount);

        // Get an Amino::Ptr to the deformed positions.
        auto deformedPositions = Bifrost::Geometry::getDataGeoPropValues<float3>(
            *pointsGeoMut, Bifrost::Geometry::sPointPosition);
        return deformedPositions;
    };

    {
        // Test case 1: 0 twist amount.
        auto deformedPositions = twistGeo(0.0F);

        // Positions should not have changed.
        EXPECT_EQ(positions->at(0), deformedPositions->at(0));
        EXPECT_EQ(positions->at(1), deformedPositions->at(1));
    }

    float dist45{};
    {
        // Test case 2: 45 degree twist amount.
        auto deformedPositions = twistGeo(45.0F);

        // v2 should have moved.
        dist45 = mag(deformedPositions->at(1) - positions->at(1));
        EXPECT_GT(dist45, 0.0F);
    }

    {
        // Test case 3: 90 degree twist amount.
        auto deformedPositions = twistGeo(90.0F);

        // v2 should have moved more than at 45 degrees.
        auto const dist90 = mag(deformedPositions->at(1) - positions->at(1));
        EXPECT_GT(dist90, dist45);
    }
}

TEST(TwistDeformer, Axis) {
    // Create a simple points geometry with 2 points. Twist it along the x-axis.
    //
    // y
    // ^
    // v1     v2
    // |
    // +-->x
    auto positions =
        Amino::newClassPtr<Amino::Array<float3>, float3>({{0.0F, 1.0F, 0.0F}, {1.0F, 1.0F, 0.0F}});
    auto pointsGeo = Bifrost::createObject();
    Bifrost::Geometry::populatePointCloud(positions, *pointsGeo);

    TwistDeformer twister(*pointsGeo);
    twister.deform(90.0F, {0.0F, 0.0F, 0.0F}, {1.0F, 0.0F, 0.0F});

    auto deformedPositions = Bifrost::Geometry::getDataGeoPropValues<float3>(
        *pointsGeo, Bifrost::Geometry::sPointPosition);

    // Check that v2 moved along its original yz plane.
    auto const v2         = positions->at(1);
    auto const deformedV2 = deformedPositions->at(1);
    EXPECT_FLOAT_EQ(v2.x, deformedV2.x);
    EXPECT_NE(v2.z, deformedV2.z);
    EXPECT_NE(v2.y, deformedV2.y);
}

TEST(TwistDeformer, Position) {
    // Create a simple points geometry with 2 points. Twist it along the y-axis, around (-1,0,0)
    //
    // y
    // ^
    // |
    // v2
    // |
    // v1
    // +-->x
    auto positions =
        Amino::newClassPtr<Amino::Array<float3>, float3>({{0.0F, 1.0F, 0.0F}, {0.0F, 2.0F, 0.0F}});
    auto pointsGeo = Bifrost::createObject();
    Bifrost::Geometry::populatePointCloud(positions, *pointsGeo);

    TwistDeformer twister(*pointsGeo);
    twister.deform(90.0F, {-1.0F, 0.0F, 0.0F});

    auto deformedPositions = Bifrost::Geometry::getDataGeoPropValues<float3>(
        *pointsGeo, Bifrost::Geometry::sPointPosition);

    // Check that v2 moved along its original xz plane.
    auto const v2         = positions->at(1);
    auto const deformedV2 = deformedPositions->at(1);
    EXPECT_FLOAT_EQ(v2.y, deformedV2.y);
    EXPECT_NE(v2.x, deformedV2.x);
    EXPECT_NE(v2.z, deformedV2.z);
}

TEST(TwistDeformer, EmptyPoints) {
    // Create an empty points geometry.
    auto pointsGeo = Bifrost::createObject();
    Bifrost::Geometry::populatePointCloud(*pointsGeo);

    // Create a twist deformer.
    TwistDeformer twister(*pointsGeo);

    // Deform the empty points geometry.
    twister.deform(0.0F);

    auto deformedPositions = Bifrost::Geometry::getDataGeoPropValues<float3>(
        *pointsGeo, Bifrost::Geometry::sPointPosition);
    EXPECT_TRUE(deformedPositions->empty());
}

TEST(TwistDeformer, CopyOnWrite) {
    // Test that the deformation does not happen in-place when there are multiple Amino::Ptrs to the
    // array of positions.

    // Create a simple points geometry with 2 points.
    auto pos =
        Amino::newClassPtr<Amino::Array<float3>, float3>({{1.0F, 0.0F, 0.0F}, {1.0F, 1.0F, 0.0F}});
    auto pointsGeo = Bifrost::createObject();
    Bifrost::Geometry::populatePointCloud(pos, *pointsGeo);

    // Note there are two Amino::Ptrs to the positions array. One is held in the points geometry,
    // and the other is held in the pos variable.
    EXPECT_EQ(pos.use_count(), 2);

    // Perform the twist. The positions held in the mesh should be copied since the mesh does not
    // have exclusive ownership of the array (the pos variable also holds a reference to the
    // array)
    TwistDeformer twister(*pointsGeo);
    twister.deform(90.0F);

    auto outPositions = Bifrost::Geometry::getDataGeoPropValues<float3>(
        *pointsGeo, Bifrost::Geometry::sPointPosition);

    // Check that the outPositions array is unique.
    EXPECT_NE(outPositions.get(), pos.get());

    // The array pointed to by the pos variable should not have been modified.
    EXPECT_EQ(pos->at(0), (float3{1.0F, 0.0F, 0.0F}));
    EXPECT_EQ(pos->at(1), (float3{1.0F, 1.0F, 0.0F}));
}

TEST(TwistDeformer, InPlace) {
    // Test that the deformation happens in-place when there are no other Amino::Ptr pointing at the
    // positions array.

    // Create a simple points geometry with 2 points.
    auto pos =
        Amino::newClassPtr<Amino::Array<float3>, float3>({{1.0F, 0.0F, 0.0F}, {1.0F, 1.0F, 0.0F}});
    auto pointsGeo = Bifrost::createObject();
    Bifrost::Geometry::populatePointCloud(pos, *pointsGeo);

    // Remember the memory address of the positions array for the test. This is only for testing
    // the unique-ness of the array after the twist. The array must not be dereferenced through this
    // variable.
    auto const posAddress = reinterpret_cast<uintptr_t>(pos.get());

    // Clear the pos pointer. The mesh now holds exclusive ownership of the positions array.
    pos = nullptr;

    // Perform the twist. The positions held in the mesh should be modified in-place since the mesh
    // has exclusive ownership of the array.
    TwistDeformer twister(*pointsGeo);
    twister.deform(90.0F);

    // Get the deformed positions.
    auto outPositions = Bifrost::Geometry::getDataGeoPropValues<float3>(
        *pointsGeo, Bifrost::Geometry::sPointPosition);

    // Check that the address of the outPositions array is the same as the original positions array.
    // (i.e. it was modified in-place)
    auto const outPosAddress = reinterpret_cast<uintptr_t>(outPositions.get());
    EXPECT_EQ(outPosAddress, posAddress);
}
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

#include <Examples/GeoSDK/MeshArea.h>

#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Geometry/Primitives.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/Ptr.h>

#include <chrono>
#include <functional>

namespace {

using FuncComputeArea = std::function<float(Examples::GeoSDK::FaceMeshView const&)>;

template <bool EnableProfiling = true>
float computeArea(FuncComputeArea const&                areaFunction,
                  Examples::GeoSDK::FaceMeshView const& faceContainer,
                  std::string const&                    name) {
    using namespace std::chrono;
    time_point<high_resolution_clock> start_point;
    time_point<high_resolution_clock> end_point;
    long long                         time = 0;

    start_point = high_resolution_clock::now();
    float area  = areaFunction(faceContainer);
    end_point   = high_resolution_clock::now();
    time        = duration_cast<microseconds>(end_point - start_point).count();

    std::cout << name << ": Time: " << time << " microseconds" << std::endl;

    return area;
}

template <>
float computeArea<false>(FuncComputeArea const&                areaFunction,
                         Examples::GeoSDK::FaceMeshView const& faceContainer,
                         std::string const& /*name*/) {
    return areaFunction(faceContainer);
}

template <bool EnableProfiling=false>
void testArea(
    // Check each area computation method against the expected area.

    Examples::GeoSDK::FaceMeshView const& faceContainer,
    float                                 expectedArea) {
    auto compNewellArea = std::mem_fn(&Examples::GeoSDK::FaceMeshView::computeAreaNewell);
    float areaNewell = computeArea<EnableProfiling>(compNewellArea, faceContainer, "Newell method");
    EXPECT_FLOAT_EQ(areaNewell, expectedArea);

    auto compShoelaceArea = std::mem_fn(&Examples::GeoSDK::FaceMeshView::computeAreaShoelace);
    float areaShoelace =
        computeArea<EnableProfiling>(compShoelaceArea, faceContainer, "Shoelace method");
    EXPECT_FLOAT_EQ(areaShoelace, expectedArea);

    auto compClassicArea = std::mem_fn(&Examples::GeoSDK::FaceMeshView::computeAreaFanOut);
    float areaClassic =
        computeArea<EnableProfiling>(compClassicArea, faceContainer, "FanOut method");
    EXPECT_FLOAT_EQ(areaClassic, expectedArea);
}

} // namespace

TEST(TestFaceContainer, TestCubeArea) {
    // Simple cube test.

    constexpr float cubeFaceWidth = 2.0F;
    constexpr float cubeArea      = 24.0F;

    auto cubeMesh = Bifrost::createObject();
    Bifrost::Geometry::populateCubeMesh(cubeFaceWidth, *cubeMesh);
    Examples::GeoSDK::FaceMeshView faceContainer(*cubeMesh);

    testArea(faceContainer, cubeArea);
}

TEST(TestFaceContainer, TestWeirdArea) {
    // (1,3,0) *--------* (3,3,0)
    //         \       /
    //          \     /
    //           \   /
    //            \ /
    //     (2,2,0) * (2,2,0)
    //            / \
    //           /   \
    //          /     \
    //         /       \
    // (1,1,0) *--------* (3,1,0)

    constexpr float weirdArea = 2.0F;

    auto weirdMesh   = Bifrost::createObject();
    auto weirdPoints = Amino::newClassPtr<Amino::Array<Bifrost::Math::float3>>(
        std::initializer_list<Bifrost::Math::float3>{
            {1, 1, 0}, {3, 1, 0}, {2, 2, 0}, {3, 3, 0}, {1, 3, 0}, {2, 2, 0}});
    auto weirdFaceOffsets = Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>(
        std::initializer_list<Bifrost::Geometry::Index>{0, 6});

    auto weirdFaceVertices = Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>(
        std::initializer_list<Bifrost::Geometry::Index>{0, 1, 2, 3, 4, 5});

    ASSERT_TRUE(Bifrost::Geometry::populateMesh(std::move(weirdPoints),
                                                std::move(weirdFaceVertices),
                                                std::move(weirdFaceOffsets), *weirdMesh))
        << "Failed to populate weird mesh";

    Examples::GeoSDK::FaceMeshView faceContainer(*weirdMesh);

    testArea(faceContainer, weirdArea);
}

TEST(TestFaceContainer, TestConcaveArea) {
    // (1,3,0) *--------* (3,3,0)
    //         |       /
    //         |      /
    //         |     /
    //         |    /
    //         |   * (2,2,0)
    //         |    \
    //         |     \
    //         |      \
    //         |       \
    // (1,1,0) *--------* (3,1,0)

    constexpr float concaveArea = 3.0F;

    auto concaveMesh   = Bifrost::createObject();
    auto concavePoints = Amino::newClassPtr<Amino::Array<Bifrost::Math::float3>>(
        std::initializer_list<Bifrost::Math::float3>{
            {1, 1, 0}, {3, 1, 0}, {2, 2, 0}, {3, 3, 0}, {1, 3, 0}});
    auto concaveFaceOffsets = Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>(
        std::initializer_list<Bifrost::Geometry::Index>{0, 5});

    auto concaveFaceVertices = Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>(
        std::initializer_list<Bifrost::Geometry::Index>{0, 1, 2, 3, 4});

    ASSERT_TRUE(Bifrost::Geometry::populateMesh(std::move(concavePoints),
                                                std::move(concaveFaceVertices),
                                                std::move(concaveFaceOffsets), *concaveMesh))
        << "Failed to populate concave mesh";

    Examples::GeoSDK::FaceMeshView faceContainer(*concaveMesh);

    testArea(faceContainer, concaveArea);
}

TEST(TestFaceContainer, TestTwistedArea) {
    // (1,3,0) *--------* (3,3,0)
    //         \       /
    //          \     /
    //           \   /
    //            \ /
    //            / \
    //           /   \
    //          /     \
    //         /       \
    // (1,1,0) *--------* (3,1,0)

    constexpr float twistedArea = 0.0F;

    auto twistedQuad   = Bifrost::createObject();
    auto twistedPoints = Amino::newClassPtr<Amino::Array<Bifrost::Math::float3>>(
        std::initializer_list<Bifrost::Math::float3>{{1, 1, 0}, {3, 1, 0}, {1, 3, 0}, {3, 3, 0}});
    auto twistedFaceOffsets = Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>(
        std::initializer_list<Bifrost::Geometry::Index>{0, 4});

    auto twistedFaceVertices = Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>(
        std::initializer_list<Bifrost::Geometry::Index>{0, 1, 2, 3});

    ASSERT_TRUE(Bifrost::Geometry::populateMesh(std::move(twistedPoints),
                                                std::move(twistedFaceVertices),
                                                std::move(twistedFaceOffsets), *twistedQuad))
        << "Failed to populate twisted quad";

    Examples::GeoSDK::FaceMeshView faceContainer(*twistedQuad);

    testArea(faceContainer, twistedArea);
}

TEST(TestFaceContainer, TestNonPlanarArea) {
    // (1,3,1) *--------* (3,3,2)
    //         |        |
    //         |        |
    //         |        |
    //         |        |
    // (1,1,2) *--------* (3,1,1)

    constexpr float nonPlanarQuadArea = 4.0F;

    auto nonPlanarQuad   = Bifrost::createObject();
    auto nonPlanarPoints = Amino::newClassPtr<Amino::Array<Bifrost::Math::float3>>(
        std::initializer_list<Bifrost::Math::float3>{{1, 1, 2}, {3, 1, 1}, {3, 3, 2}, {1, 3, 1}});
    auto nonPlanarFaceOffsets = Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>(
        std::initializer_list<Bifrost::Geometry::Index>{0, 4});

    auto nonPlanarFaceVertices = Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>(
        std::initializer_list<Bifrost::Geometry::Index>{0, 1, 2, 3});

    ASSERT_TRUE(Bifrost::Geometry::populateMesh(std::move(nonPlanarPoints),
                                                std::move(nonPlanarFaceVertices),
                                                std::move(nonPlanarFaceOffsets), *nonPlanarQuad))
        << "Failed to populate non planar quad";

    Examples::GeoSDK::FaceMeshView faceContainer(*nonPlanarQuad);
    testArea(faceContainer, nonPlanarQuadArea);
}

TEST(TestFaceContainer, TestPlaneArea) {
    //
    // A big plane 1000x1000 squares
    //
    constexpr float    planeWidth        = 1000.0F;
    constexpr unsigned planeSubdivisions = 1000;
    constexpr float    bigPlaneArea      = planeWidth * planeWidth;

    auto bigPlaneMesh = Bifrost::createObject();
    Bifrost::Geometry::populatePlaneMesh(planeWidth, planeSubdivisions, *bigPlaneMesh);

    Examples::GeoSDK::FaceMeshView faceContainer(*bigPlaneMesh);
    testArea<true>(faceContainer, bigPlaneArea);
}

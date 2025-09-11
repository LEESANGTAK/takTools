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

#include <Examples/GeoSDK/ObjWriter.h>

#include <Amino/Core/Ptr.h>

#include <Bifrost/Geometry/DebugDump.h>
#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Geometry/Primitives.h>
#include <Bifrost/Geometry/Validator.h>
#include <Bifrost/Object/Object.h>


#include <chrono>
#include <functional>

namespace {
using Bifrost::Geometry::Index;
using Bifrost::Math::float2;
using Bifrost::Math::float3;
using ArrayFloat3 = Amino::Array<float3>;
using ArrayFloat2 = Amino::Array<float2>;
using ArrayIndex  = Amino::Array<Index>;

void addFaceVertexUVs(Bifrost::Object& mesh) {
    // Range geo properties represent index arrays that provide an additional level of indirection
    // between the topological components of the geometry and a corresponding data geo property data
    // array. They are useful when there are only a few unique data elements, or the *identity* of
    // the data elements is important, and not just the *value*. The index array in a range geo
    // property has at least the same number of elements as the component it is targeting. Its
    // values are indices into a corresponding data array. The target of the data geo property is
    // the range geo property and the target of the range geo property is the component.

    // In practice, mesh normals and UV coordinates typically use indexed geo properties. For UV
    // coordinates a float2 array is stored in a data geo property named `face_vertex_uv`. This geo
    // property targets a range geo property named `face_vertex_uv_index` that contains the index
    // array. The range geo property then targets the `face_vertex_component`. For UV coordinates in
    // particular the identity of the referenced UV coordinates is important. Face vertices that
    // reference the same vertex but different UV coordinates represent UV seams (also called UV
    // borders) within a mesh.

    //  Here we have a range of 4 elements indexed by 24 face vertex
    auto uv_data = Amino::newClassPtr<ArrayFloat2, float2>(
        {{0.0F, 0.0F}, {1.0F, 0.0F}, {0.0F, 1.0F}, {1.0F, 1.0F}});
    auto uv_indices = Amino::newClassPtr<ArrayIndex, Index>(
        {0, 1, 3, 2, 0, 1, 3, 2, 0, 1, 3, 2, 0, 1, 3, 2, 0, 1, 3, 2, 0, 1, 3, 2});
    ASSERT_EQ(uv_indices->size(),
              Bifrost::Geometry::getElementCount(mesh, Bifrost::Geometry::sFaceVertexComp));

    // Creating an Indexing Object, populate it and set it to the geometry.
    auto       uv_index_obj = Bifrost::createObject();
    auto const uv_index_name =
        Bifrost::Geometry::getGeoPropRangeName(Bifrost::Geometry::sFaceVertexUV);
    Bifrost::Geometry::populateRangeGeoProperty(std::move(uv_indices),
                                                Bifrost::Geometry::sFaceVertexComp, *uv_index_obj);
    mesh.setProperty(uv_index_name, uv_index_obj.toImmutable());

    // Creating the Indexed data Object, populate it and set it to the geometry.
    auto uv_dataObj = Bifrost::createObject();
    Bifrost::Geometry::populateDataGeoProperty(float2{}, std::move(uv_data), uv_index_name,
                                               *uv_dataObj);
    mesh.setProperty(Bifrost::Geometry::sFaceVertexUV, uv_dataObj.toImmutable());

    // A good way to make sure your properties are set correctly is to validate your geometry.
    Bifrost::Geometry::MeshValidator v;
    ASSERT_TRUE(v.validate(mesh));
}
} // namespace

TEST(TestOBJWriter, TestOutputCube) {
    // Simple cube test.
    constexpr float c    = 1.0F;
    auto            mesh = Bifrost::createObject();
    Bifrost::Geometry::populateCubeMesh(c, *mesh);

    Bifrost::Geometry::MeshValidator v;
    ASSERT_TRUE(v.validate(*mesh));

    ASSERT_TRUE(Examples::GeoSDK::writeOBJ(*mesh, "./mesh.obj"));

    auto fv_indices =
        Bifrost::Geometry::getDataGeoPropValues<Index>(*mesh, Bifrost::Geometry::sFaceVertex);
    ASSERT_TRUE(fv_indices);
    auto fvn_name = Bifrost::Geometry::getGeoPropRangeName(Bifrost::Geometry::sFaceVertexNormal);
    auto fvn_data = Bifrost::Geometry::getDataGeoPropValues<float3>(
        *mesh, Bifrost::Geometry::sFaceVertexNormal);
    ASSERT_TRUE(fvn_data);

    addFaceVertexUVs(*mesh);

    auto uv_data =
        Bifrost::Geometry::getDataGeoPropValues<float2>(*mesh, Bifrost::Geometry::sFaceVertexUV);
    auto uv_indices = Bifrost::Geometry::getRangeGeoPropIndices(
        *mesh, Bifrost::Geometry::getGeoPropTargetName(*mesh, Bifrost::Geometry::sFaceVertexUV));
    ASSERT_TRUE(uv_data);
    ASSERT_TRUE(uv_indices);

    ASSERT_TRUE(mesh->hasProperty(Bifrost::Geometry::sFaceVertexUV));
    ASSERT_TRUE(Examples::GeoSDK::writeOBJ(*mesh, "./mesh_with_uvs.obj"));
}

//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include <Examples/GeoSDK/ObjWriter.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Math/Types.h>

#include <fstream>
#include <iostream>

using Bifrost::Geometry::Index;
using ArrayFloat3 = Amino::Array<Bifrost::Math::float3>;
using ArrayFloat2 = Amino::Array<Bifrost::Math::float2>;
using ArrayIndex  = Amino::Array<Index>;

namespace {
//
void outputFloatArray(std::fstream& out, const ArrayFloat3& pts, const std::string& section) {
    // Vertex section
    for (const auto& pt : pts) {
        out << section << pt.x << " " << pt.y << " " << pt.z << std::endl;
    }
    out << std::endl;
}
void outputFloatArray(std::fstream& out, const ArrayFloat2& pts, const std::string& section) {
    // Vertex section
    for (const auto& pt : pts) {
        out << section << pt.x << " " << pt.y << std::endl;
    }
    out << std::endl;
}

void outputNormals(std::fstream& out, const Bifrost::Object& mesh) {
    Amino::Ptr<ArrayFloat3> normals(Bifrost::Geometry::getDataGeoPropValues<Bifrost::Math::float3>(
        mesh, Bifrost::Geometry::sFaceVertexNormal));
    if (!normals) {
        normals = Bifrost::Geometry::getDataGeoPropValues<Bifrost::Math::float3>(
            mesh, Bifrost::Geometry::sPointNormal);
    }
    outputFloatArray(out, *normals, "vn ");
}

void outputUVS(std::fstream& out, const Bifrost::Object& mesh) {
    Amino::Ptr<ArrayFloat2> uvs(Bifrost::Geometry::getDataGeoPropValues<Bifrost::Math::float2>(
        mesh, Bifrost::Geometry::sFaceVertexUV));
    if (uvs) {
        outputFloatArray(out, *uvs, "vt ");
    }
}
} // namespace
bool Examples::GeoSDK::writeOBJ(const Bifrost::Object& mesh, const std::string& filename) {
    std::fstream out_stream(filename, std::ios_base::out);
    if (!out_stream) {
        return false;
    }
    out_stream.precision(6);

    const auto num_pts   = Bifrost::Geometry::getElementCount(mesh, Bifrost::Geometry::sPointComp);
    const auto num_faces = Bifrost::Geometry::getElementCount(mesh, Bifrost::Geometry::sFaceComp);
    // Write a small header
    out_stream << "# Vertices : " << num_pts << std::endl;
    out_stream << "# Faces : " << num_faces << std::endl;
    if (num_pts < 1) {
        return false;
    }

    Amino::Ptr<ArrayFloat3> vertices(Bifrost::Geometry::getDataGeoPropValues<Bifrost::Math::float3>(
        mesh, Bifrost::Geometry::sPointPosition));
    outputFloatArray(out_stream, *vertices, "v ");

    // Write normals
    bool has_point_normal = mesh.hasProperty(Bifrost::Geometry::sPointNormal);
    bool has_fv_normal    = mesh.hasProperty(Bifrost::Geometry::sFaceVertexNormal);
    bool has_normal       = has_fv_normal || has_point_normal;
    if (has_normal) {
        outputNormals(out_stream, mesh);
    }

    bool has_uvs = mesh.hasProperty(Bifrost::Geometry::sFaceVertexUV);
    if (has_uvs) {
        outputUVS(out_stream, mesh);
    }

    if (num_faces > 0) {
        Amino::Ptr<ArrayIndex> face_vertices(
            Bifrost::Geometry::getDataGeoPropValues<Index>(mesh, Bifrost::Geometry::sFaceVertex));
        Amino::Ptr<ArrayIndex> face_offsets(
            Bifrost::Geometry::getDataGeoPropValues<Index>(mesh, Bifrost::Geometry::sFaceOffset));
        assert(face_offsets->size() == num_faces + 1);

        Amino::Ptr<ArrayIndex> fvni;
        if (has_fv_normal) {
            auto fv_index_name =
                Bifrost::Geometry::getGeoPropRangeName(Bifrost::Geometry::sFaceVertexNormal);
            fvni = Bifrost::Geometry::getRangeGeoPropIndices(mesh, fv_index_name);
        }
        Amino::Ptr<ArrayIndex> fvti;
        if (has_uvs) {
            auto fvuvs_index_name =
                Bifrost::Geometry::getGeoPropRangeName(Bifrost::Geometry::sFaceVertexUV);
            fvti = Bifrost::Geometry::getRangeGeoPropIndices(mesh, fvuvs_index_name);
        }

        // Face section
        for (size_t f = 0; f < num_faces; ++f) {
            auto first_vertex_index = (*face_offsets)[f];
            auto face_size          = (*face_offsets)[f + 1] - (*face_offsets)[f];
            out_stream << "f";

            for (size_t v = 0; v < face_size; ++v) {
                auto fv =
                    (*face_vertices)[first_vertex_index + v] + 1; // Obj format : Index are 1-based.
                auto fvn_index = fv;
                if (has_fv_normal) {
                    fvn_index = (*fvni)[first_vertex_index + v] + 1;
                }

                // See https://en.wikipedia.org/wiki/Wavefront_.obj_file
                // If No normals or texture coordinates : f v1 v2 v3 ....
                // if Vertex texture coordinate indices : f v1/vt1 v2/vt2 v3/vt3 ...
                // If Vertex normal indices  :            f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3 ...
                out_stream << " " << fv;

                if (has_uvs && has_normal) {
                    auto fvt_index = (*fvti)[first_vertex_index + v] + 1;
                    out_stream << "/" << fvt_index << "/" << fvn_index;
                } else if (has_normal) {
                    out_stream << "//" << fvn_index;
                } else if (has_uvs) {
                    auto fvt_index = (*fvti)[first_vertex_index + v] + 1;
                    out_stream << "/" << fvt_index;
                }
            }

            out_stream << std::endl;
        }
        out_stream << std::endl;
    }

    // Ouput
    return true;
}
//

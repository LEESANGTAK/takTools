//-
//*****************************************************************************
// Copyright (c) 2024 Autodesk, Inc.
// All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

//
/// \file GeometryTypes.h
///
/// \brief Geometry related types that flow in the graph that are defined in C++.
/// \note The Bifrost namespace is mandatory in C++ but does not exist in the graph.

#ifndef BIFROST_GEOMETRY_TYPES_H
#define BIFROST_GEOMETRY_TYPES_H

#include <Bifrost/Geometry/GeometryExport.h>

#include <Amino/Core/internal/ConfigMacros.h>
#include <Amino/Cpp/Annotate.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Bifrost/Math/Types.h>

#define BIFROST_IGNORE_NAMESPACE AMINO_ANNOTATE("Amino::Namespace ignore")
namespace Bifrost BIFROST_IGNORE_NAMESPACE {
#undef BIFROST_IGNORE_NAMESPACE

namespace Simulation {
/// Rate types available for scale_rate_to_time_step
enum  class AMINO_ANNOTATE("Amino::Enum")
    RateType : int {
        per_second, /**< rate per second */
        per_frame   /**< rate per frame */
    };

struct AMINO_ANNOTATE("Amino::Struct") Time {
    long long ticks; ///< Number of ticks, based on Maya's definition of ticks
    double    time;  ///< Time in seconds.
    double    frame; ///< Frame number - can be fractional.
    double    frameLength; ///< Length of a frame in seconds.
};

struct AMINO_ANNOTATE("Amino::Struct") TimelineInfo {
    double startFrame; ///< The first frame of the time slider from the host.
    double endFrame;   ///< The last frame of the time slider from the host.
    double minFrame;   ///< The first frame of the range slider from the host.
    double maxFrame;   ///< The last frame of the range slider from the host.
    double frameStep;  ///< The increment between steps viewed during the playing of the animation
                       ///< from the host.
};

} // namespace Simulation

namespace Geometry {

namespace Common {

// To add a new geometry type:
// - Add an element to this enum
// - Add populateXyz and getXyzPrototype methods to GeoProperty.h
// - Add the type to Bifrost::Geometry::getGeometryTypes()
// - Update get_geo_schema_type to add a case for the new type
// - Update switch_is_a to use this new case.
// - Update all compounds using switch_is_a to do the right thing for the new
// type.
//   (could be a simple passthrough by default.)

enum class
 AMINO_ANNOTATE("Amino::Enum")
GeometryType : int {
    not_a_geometry = 0,  /**< Not a geometry */
    volume,         /**< Volume geometry */
    instances,      /**< Instances geometry */
    mesh,           /**< Mesh geometry */
    strands,        /**< Strands geometry */
    points         /**< Points geometry */
};

/// \class GeoLocation
/// \brief Describes a location within, or on the surface of, a geometry.
///
/// The member variable names are intentionally generic, as this data type
/// can describe locations on the surface of a mesh, or within a volume, or
/// along a strand segment, or a particular point in a points geometry.
///
/// For meshes the interpretation of a GeoLocation is a weighted sum of the
/// corners of a face within the mesh. The type member will be set to
/// GeometryType::mesh. The index member is interpreted as a face index. The
/// sub_indices will contain corner indices relative to the face. There are
/// always at least three valid indices. The fourth may be set to
/// Bifrost::Geometry::kInvalidIndex. The sub_parameters will contain weights
/// for the corresponding sub_indices. If there are more than four sub_indices
/// the remaining indices and corresponding weights will be stored in
/// aux_indices and aux_weights respectively.
///
/// For strands the interpretation of a GeoLocation is a weighted sum of the
/// points of a strand segment. The type member will be set to
/// GeometryType::strand. The index member is interpreted as a strand index. The
/// sub_indices will contain point indices relative to the strand. There are
/// always two valid indices. The third and fourth may be set to kInvalidIndex.
/// The sub_parameters will contain weights for the corresponding sub_indices.
///
/// For points the interpretation of a GeoLocation is a single point within the
/// point cloud. The type member will be set to GeometryType::points. The index
/// is interpreted as a point index. The other members are not used.
///
/// For volumes the interpretation of a GeoLocation is a position in local
/// space. The type member will be set to GeometryType::volume. The
/// sub_parameter member is interpreted as a local position in 3d space within
/// the volume. The other
/// members are not used.
struct  AMINO_ANNOTATE(
    "Amino::Struct")  BIFROST_GEOMETRY_DECL GeoLocation {
    /// \brief The type of geometry location.
    GeometryType type{};

    /// \brief The index of the component this location relates to.
    unsigned int index{};

    /// \brief The sub-indices (up to four). For example, these may refer to the
    /// face vertices of a face.
    Bifrost::Math::uint4 sub_indices{};

    /// \brief The sub-parameters (up to four). For example, these may refer to
    /// weights corresponding to the sub_indices.
    Bifrost::Math::float4 sub_parameters{};

    /*@cond true*/
    AMINO_INTERNAL_WARNING_PUSH
    AMINO_INTERNAL_WARNING_DISABLE_MSC(4251)
    /*@endcond*/

    /// \brief Auxillary array for any indices beyond the first four.
    Amino::Ptr<Amino::Array<unsigned int>> aux_indices{Amino::PtrDefaultFlag{}};
    /// \brief Auxillary array for any parameters beyond the first four.
    Amino::Ptr<Amino::Array<float>> aux_parameters{Amino::PtrDefaultFlag{}};

    /*@cond true*/
    AMINO_INTERNAL_WARNING_POP
    /*@endcond*/

    bool operator==(const GeoLocation& other) const;
    bool operator!=(const GeoLocation& other) const {
        return !(*this == other);
    }
};

/// Specifies the detail size mode to use.
enum class
 AMINO_ANNOTATE("Amino::Enum")
Adaptivity : int
{
    Automatic, ///< How this works is context dependent.
    VariedFromProperty, ///< Use a detail size that varies according to the specified voxel property.
    Off ///< Use a uniform detail size.
};
/// The interpolation mode determines the type of interpolation used when interpolating new data
/// values
enum class AMINO_ANNOTATE("Amino::Enum") DataInterpolationMode : int {
    Nearest = 0, ///< Nearest neighbor interpolation
    Linear,      ///< Linear interpolation
    DefaultValue ///< No interpolation, use the default value specified in the geo property
};

} // Common

namespace Mesh {

///@{ \name FaceEdge
/// \class FaceEdge
/// \brief Describes a half-edge within a face of a mesh.
struct  AMINO_ANNOTATE(
    "Amino::Struct")  BIFROST_GEOMETRY_DECL FaceEdge {
    unsigned int face;      ///< The index of the face that is referenced by this FaceEdge
    unsigned int side;      ///< The side within the face that is referenced by this FaceEdge. Side 0 is defined as the edge between face vertex 0 and 1, side 1 is defined as the edge between face vertex 1 and 2, etc.

    bool operator==(const FaceEdge& other) const;
};
} // namespace Mesh

// BIFROST-4034 - Hide ports that are not yet needed in the graph_space node
// design
/*@cond true*/
#define BIFROST_WANT_FULL_GRAPH_TRANSFORM_FUNCTIONALITY 0
/*@endcond*/
namespace Transform {
struct
     AMINO_ANNOTATE("Amino::Struct")  BIFROST_GEOMETRY_DECL
    GraphTransforms {
    Bifrost::Math::float4x4 totalTransform; ///< The total transform of the graph node.
#if BIFROST_WANT_FULL_GRAPH_TRANSFORM_FUNCTIONALITY
    Bifrost::Math::float4x4 parentTransform;
    Bifrost::Math::float4x4 localTransform;
#endif
};
} // namespace Transform

namespace Query {
/// Defines an interpolation mode
enum  AMINO_ANNOTATE("Amino::Enum")
    SamplerType : int {
        kLinear,  ///< Linear interpolation
        kCubicC0, ///< Piecewise cubic interpolation with C0 continuity
        kCubicC1  ///< Piecewise cubic interpolation with C1 continuity
    };
} // namespace Query

} // Geometry
} // Bifrost

#endif // BIFROST_GEOMETRY_TYPES_H

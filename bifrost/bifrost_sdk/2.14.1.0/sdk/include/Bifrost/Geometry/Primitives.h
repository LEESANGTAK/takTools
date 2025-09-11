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
/// \file Primitives.h
///
/// \brief Utility functions to build basic primitives that conform to the geometry schema.
///

#ifndef BIFROST_GEOMETRY_PRIMITIVE_H
#define BIFROST_GEOMETRY_PRIMITIVE_H

#include <Bifrost/Geometry/GeometryExport.h>

#include <Bifrost/Geometry/GeoPropertyKey.h>
#include <Bifrost/Geometry/GeometryTypes.h>

#include <Bifrost/Object/Object.h>

#include <Bifrost/Math/Types.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>

namespace Bifrost
{
namespace Geometry
{
/// \defgroup GeoPrimitives Geometry Primitives
/// \brief Utility functions for manipulating Geometry Primitives that conform to the geometry schema.
///@{

/// \defgroup GeoPrimitiveTypes Identifying a Geometry Primitive
/// \brief Functions for querying the "type" of a geometry.
///@{
/// \brief Return a list of geometry prototypes, ordered from most to least specific.
/// Can be used to find the type of an object, for example using the helper
/// function \ref Bifrost::Geometry::resolveType.
///
/// The ordering of types is (from most to least specific)
/// - Volume
/// - Instances
/// - Mesh
/// - Strands
/// - Point cloud
///
/// \return A const array of geometry prototypes.
BIFROST_GEOMETRY_DECL Amino::Ptr<Amino::Array<Amino::Ptr<Bifrost::Object>>>
                      getGeometryTypes();

// -----------------------------------------------------------------------------
/// \brief Finds the first prototype in the given prototypes such that the given
/// object satisfies this prototype.
///
template<typename Prototypes>
decltype(auto) findPrototype(Bifrost::Object const& obj, Prototypes const& prototypes) {
    auto isA = [&obj](Amino::Ptr<Bifrost::Object> const& prototype) {
        return Bifrost::Object::isA(obj, *prototype);
    };
    return std::find_if(std::begin(prototypes), std::end(prototypes), isA);
}

// -----------------------------------------------------------------------------
/// \brief Determine the type of an object.
///
/// Simply traverses all the geometry prototypes and returns the first one that matches.
inline Common::GeometryType resolveType(Bifrost::Object const& obj) {
    auto prototypes = getGeometryTypes();

    auto it = findPrototype(obj, *prototypes);
    if (it == prototypes->end()) return Common::GeometryType::not_a_geometry;

    auto index = std::distance(prototypes->begin(), it);
    return static_cast<Common::GeometryType>(index + 1); // skip not_a_geometry
}
///@}

// -----------------------------------------------------------------------------
// Geometry object volume-specific methods

/// \defgroup GeoPrimitiveVolumes Volume functions
/// \brief Functions for creating empty volumes.
///@{
/*! \brief Returns the prototypical volume object.

    The returned pointer may be used in conjunction with  Bifrost::Object::isA to
    determine if an object conforms to the volume schema. The returned object
    may not be modified.

    \return The volume prototype
*/
 Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getVolumePrototype();

 /*! \brief Populate an object with the required properties to conform to the
     volume geometry schema.

     The volume is initially empty.
     \param [in,out] object Volume geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populateVolume(Bifrost::Object& object);

 // -----------------------------------------------------------------------------
 // Geometry object levelSet-specific methods

 /*! \brief Returns the prototypical level set object.

     The returned pointer may be used in conjunction with  Bifrost::Object::isA to
     determine if an object conforms to the volume schema. The returned object
     may not be modified.

     \return The levelSet prototype
 */
 Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getLevelSetPrototype();

 /*! \brief Returns the prototypical fog volume object.

     The returned pointer may be used in conjunction with  Bifrost::Object::isA to
     determine if an object conforms to the volume schema. The returned object
     may not be modified.

     \return The fogVolume prototype
 */
 Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getFogVolumePrototype();

 /*! \brief Returns the prototypical liquid set object.

     The returned pointer may be used in conjunction with  Bifrost::Object::isA to
     determine if an object conforms to the liquid schema. The returned object
     may not be modified.

     \return The liquid prototype
 */
 Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getFlipLiquidPrototype();

 /*! \brief Populate an object with the required properties to conform to the
     liquid geometry schema.

     The liquid is initially empty.
     \param [in,out] object Liquid geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populateFlipLiquid(Bifrost::Object& object);


 /*! \brief Populate an object with the required properties to conform to the
     level set geometry schema.

     The level set is initially empty.
     \param [in,out] object level set geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populateLevelSet(Bifrost::Object& object);

 /*! \brief Populate an object with the required properties to conform to the
     fog volume geometry schema.

     The fog volume is initially empty.
     \param [in,out] object level set geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populateFogVolume(Bifrost::Object& object);
 /// @}

 // -----------------------------------------------------------------------------
 // Geometry object point-specific methods

/// \defgroup GeoPrimitivePoints Point functions
/// \brief Functions for creating Point geometry objects.
///@{

 /*! \brief Returns the prototypical point cloud object.

     The returned pointer may be used in conjunction with  Bifrost::Object::isA to
     determine if an object conforms to the point cloud schema. The returned
    object may not be modified.

     \return The point cloud prototype
 */
 Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getPointCloudPrototype();

 /*! \brief Populate an object with the required properties to conform to the
     point cloud geometry schema.

     The point cloud is initially empty.
     \param [in,out] object Point cloud geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populatePointCloud(Bifrost::Object& object);

 /*! \brief Populate an object with the required properties to conform to the
     point cloud geometry schema.

     The point cloud is initialized with the specified data.
     \param [in] position The initial positions.
     \param [in,out] object Point cloud geometry object to be populated.
 */
 bool BIFROST_GEOMETRY_DECL populatePointCloud(
     Amino::Ptr<Amino::Array<Bifrost::Math::float3>> position, Bifrost::Object& object);
 /// @}

 // -----------------------------------------------------------------------------
 // Geometry object strand-specific methods

/// \defgroup GeoPrimitiveStrands Strand functions
/// \brief Functions for creating Strand geometry objects.
///@{
 /*! \brief Returns the prototypical strand object.

     The returned pointer may be used in conjunction with  Bifrost::Object::isA to
     determine if an object conforms to the strand schema. The returned
     object may not be modified.

     \return The strand prototype
 */
 Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getStrandPrototype();

 /*! \brief Populate an object with the required properties to conform to the
     strand geometry schema.

     The strand is initially empty.
     \param [in,out] object Strand geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populateStrand(Bifrost::Object& object);

 /*! \brief Populate an object with the required properties to conform to the
     strand geometry schema.

     The strand is initialized with the specified data.
     \param [in] positions The initial positions.
     \param [in] strandOffsets The initial offsets.
     \param [in,out] object Strand geometry object to be populated.
 */
 bool BIFROST_GEOMETRY_DECL
 populateStrand(Amino::Ptr<Amino::Array<Bifrost::Math::float3>>    positions,
                Amino::Ptr<Amino::Array<Bifrost::Geometry::Index>> strandOffsets,
                Bifrost::Object&                                   object);
 /// @}

 // -----------------------------------------------------------------------------
 // Geometry object mesh-specific methods

/// \defgroup GeoPrimitiveMeshes Mesh functions
/// \brief Functions for creating Mesh geometry objects.
///@{
 /*! \brief Returns the prototypical mesh object.

     The returned pointer may be used in conjunction with  Bifrost::Object::isA to
     determine if an object conforms to the mesh schema. The returned object may
     not be modified.

     \code {.cpp}
     Amino::Ptr< Bifrost::Object > obj = getSomeObject();
     Amino::Ptr< Bifrost::Object > mesh = Bifrost::Geometry::getMeshPrototype();
     if(  Bifrost::Object::isA(obj.get(), mesh.get()) ) {
         std::cout << "I have a mesh object";
     }
     Amino::Ptr<Bifrost::Object> emptyMesh = mesh.toMutable();
     // emptyMesh is new, empty mesh that is non-const, i.e. writeable
     \endcode
     \return The mesh prototype
 */
 Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getMeshPrototype();

 /*! \brief Populate an object with the required properties to conform to the
    Mesh geometry schema.

     The mesh is initially empty.
     \param [in,out] object Mesh geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populateMesh(Bifrost::Object& object);

 /*! \brief Populate an object with the required properties to conform to the
    Mesh geometry schema.

     The mesh is initialized with the specified data arrays.

     For example, to define a mesh that contains two triangles covering the
     unit square:
     \code{.cpp}
     Amino::Ptr<Amino::Array<Bifrost::Math::float3>> pos =
    Amino::newClassPtr<Amino::Array<Bifrost::Math::float>>();

     // Four vertices that correspond to the points of the unit square
     *pos = { {0f,0f,0f}, {1f,0f,0f}, {1f,1f,0f}, {0f,1f,0f} };

     Amino::Ptr<Amino::Array<Bifrost::Geometry::Index>> faceVert =
         Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>();

     // Six face vertices, three for each face. Face 0 uses vertices 0, 1, 2 and
     // face 1 uses vertices 0, 2, 3.
     *faceVert = { 0, 1, 2, 0, 2, 3 };

     Amino::Ptr<Amino::Array<Bifrost::Geometry::Index>> faceOffset =
         Amino::newClassPtr<Amino::Array<Bifrost::Geometry::Index>>();

     // There are two faces in the mesh so the faceOffset array contains 2
    elements plus
     // one extra pointing to one past the last element in the faceVert array.
     *faceOffset = { 0, 3, 6 };

     Amino::Ptr<Bifrost::Object> obj = Bifrost::createObject();
     populateMesh( pos, faceVert, faceOffset, obj.get() );
     \endcode

     \param [in] positions The vertex positions of the new mesh.
     \param [in] face_vertices The face vertices of the new mesh.
     \param [in] face_offsets The face offsets of the new mesh.
     \param [in,out] object Mesh geometry object to be populated.
     \return true if the object successfully initialized with the specified data arrays,
             false if errors were encountered. If false, object is left in an
             undefined state.
 */
 bool BIFROST_GEOMETRY_DECL
 populateMesh(Amino::Ptr<Amino::Array<Bifrost::Math::float3>>    positions,
              Amino::Ptr<Amino::Array<Bifrost::Geometry::Index>> face_vertices,
              Amino::Ptr<Amino::Array<Bifrost::Geometry::Index>> face_offsets,
              Bifrost::Object&                                   object);

 /*! \brief Populate an object with the properties and values required to define
     a six-sided cube mesh.
     \param [in] width Width of the cube.
     \param [in,out] object Mesh geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populateCubeMesh(float width, Bifrost::Object& object);

 /*! \brief Populate an object with the properties of a mesh sphere.
     \param [in] radius Radius of the sphere.
     \param [in,out] object Mesh geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populateSphereMesh(float radius, Bifrost::Object& object);

 /*! \brief Populate an object with the properties and values required to define
     a unit plane with the requested subdivisions on the X and Z axes.
     \param [in] width Width of the plane.
     \param [in] subdivisions Number of X and Z subdivisions. Minimum is one.
     \param [in,out] object Mesh geometry object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populatePlaneMesh(float            width,
                                              unsigned         subdivisions,
                                              Bifrost::Object& object);
 /// @}

// -----------------------------------------------------------------------------
// Geometry object Instances-specific methods

/// \defgroup GeoPrimitiveInstances Instance functions
/// \brief Functions for creating Instance geometry objects.
///@{
/*! \brief Returns the prototypical Instances object.

     The returned pointer may be used in conjunction with  Bifrost::Object::isA to
     determine if an object conforms to the Instances schema. The returned object may
     not be modified.

     \return The prototypical Instances object.
 */
 Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getInstancesPrototype();

 /*! \brief Populate an object with the required properties to conform to the
     Instances schema.

     The instances geo is initially empty.
     \param [in,out] object Instances object to be populated.
 */
 void BIFROST_GEOMETRY_DECL populateInstances(Bifrost::Object& object);
 /// @}

/// \defgroup GeoPrimitiveUtilities Utility functions
/// \brief Utility functions
///@{
/*! \brief clear internal geometry structures kept as prototypes

     Geometry prototype object are kept as "constants" internally.

     If one wants to clean them before terminating their program then one can call this function.

     If it is called before the end of your program, then the next access to geometry prototypes
     will rebuild them.
 */

 void BIFROST_GEOMETRY_DECL clearGeometryPrototypes();
 /// @}
} // namespace Geometry
} // namespace Bifrost

#endif // BIFROST_GEOMETRY_PRIMITIVE_H

//-
//*****************************************************************************
// Copyright (c) 2025 Autodesk, Inc.
// All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+
//
/// \file Validator.h
///
/// \brief utility functions for validating geometry objects.
///

#ifndef BIFROST_GEOMETRY_VALIDATOR_H
#define BIFROST_GEOMETRY_VALIDATOR_H

#include <Bifrost/Geometry/GeometryExport.h>

#include <Bifrost/Object/Object.h>

namespace Bifrost {
namespace Geometry {
// -----------------------------------------------------------------------------
/*! \class GeoValidator Validator.h
    \brief This is the base class for validating geometry.
*/
class BIFROST_GEOMETRY_DECL GeoValidator {
public:
    GeoValidator();
    virtual ~GeoValidator();

    /// Error codes that describe errors that may be found when validating
    /// objects.
    enum class ErrorCode {
        kNoError = 0,
        kInvalidObject,
        kInvalidProperty,
        kInvalidSet,
        kInvalidCount,
        kInvalidIndex,
        kMissingTarget,
        kInvalidTarget
    };

    /*! \class Status
        \brief This class contains an error code and an informative text
        description of an error.
    */
    struct BIFROST_GEOMETRY_DECL Status {
        /*! \brief Treat the status as a bool.
            \return True if no error, false otherwise.
        */
        operator bool() const; // NOLINT

        Status();
        Status(GeoValidator::ErrorCode code, Amino::String desc);

        GeoValidator::ErrorCode m_code;
        Amino::String           m_desc;
    };

    /*! \brief Validates the given object
        \param [in] object The object to validate.
        \return A status object that indicates the validity of the object.
    */
    virtual Status validate(const Bifrost::Object& object);
};

// -----------------------------------------------------------------------------
/*! \class PointCloudValidator GeoProperty.h
    \brief This class validates point cloud objects have the correct structure
    and valid indexing.
*/
class BIFROST_GEOMETRY_DECL PointCloudValidator : public GeoValidator {
public:
    /*! \brief Validates the given object is a point cloud geometry.
        \param [in] object The object to validate
        \return A status object that indicates the validity of the point cloud.
    */
    Status validate(const Bifrost::Object& object) override;
};

// -----------------------------------------------------------------------------
/*! \class InstancesValidator GeoProperty.h
    \brief This class validates instances objects have the correct structure
    and valid indexing.
*/
class BIFROST_GEOMETRY_DECL InstancesValidator : public GeoValidator {
public:
    /*! \brief Validates the given object is an instances geometry.
        \param [in] object The object to validate
        \return A status object that indicates the validity of the instances.
    */
    Status validate(const Bifrost::Object& object) override;
};

// -----------------------------------------------------------------------------
/*! \class StrandValidator GeoProperty.h
    \brief This class validates strand objects have the correct structure and
    valid indexing.
*/
class BIFROST_GEOMETRY_DECL StrandValidator : public GeoValidator {
public:
    /*! \brief Validates the given object is a strand geometry.
        \param [in] object The object to validate
        \return A status object that indicates the validity of the strand.
    */
    Status validate(const Bifrost::Object& object) override;
};

// -----------------------------------------------------------------------------
/*! \class Bifrost::Geometry::MeshValidator GeoProperty.h
    \brief This class validates mesh objects have the correct structure and
    valid indexing.
*/
class BIFROST_GEOMETRY_DECL MeshValidator : public GeoValidator {
public:
    /*! \brief Validates the given object is a mesh geometry.
        \param [in] object The object to validate
        \return A status object that indicates the validity of the mesh.
    */
    Status validate(const Bifrost::Object& object) override;
};

// -----------------------------------------------------------------------------
/*! \class VolumeValidator GeoProperty.h
    \brief This class validates volume objects have the correct structure
*/
class BIFROST_GEOMETRY_DECL VolumeValidator : public GeoValidator {
public:
    /*! \brief Validates the given object is a mesh geometry.
        \param [in] object The object to validate
        \return A status object that indicates the validity of the volume.
    */
    Status validate(const Bifrost::Object& object) override;
};

// -----------------------------------------------------------------------------
/*! \brief Convenience function to validate the specified object with a
    Bifrost::Geometry::MeshValidator.
    \param [in] in_object Mesh geometry object to be validated
    \return The status of the validation.
*/
GeoValidator::Status BIFROST_GEOMETRY_DECL
validateMesh(const Bifrost::Object& in_object);

} // namespace Geometry
} // namespace Bifrost

#endif

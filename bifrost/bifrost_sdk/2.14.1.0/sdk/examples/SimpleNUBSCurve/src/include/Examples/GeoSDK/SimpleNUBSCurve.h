//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file SimpleNUBSCurve.h
/// \brief Simple NUBS Curve operations.

#ifndef SIMPLE_NUBS_CURVE_H
#define SIMPLE_NUBS_CURVE_H

#include "SimpleNUBSCurveExport.h"

#include <Bifrost/Object/Object.h>

#include <Amino/Core/BuiltInTypes.h>
namespace Examples {
namespace GeoSDK {

/// \brief Check if the stand object is made of valid NUBS curves.
/// \param nubsCurve Object to test
/// \param statusMessage Optional output status message if the object is not valid.
/// \return True if all strands are valid NUBS curves.
SIMPLE_NUBS_CURVE_DECL
bool isNUBSCurveValid(const Bifrost::Object& nubsCurve, Amino::String* statusMessage = nullptr);

/// \brief Convert a strand object to a NUBS curve object.
///        This operation does not create a new object but modifies the input object.
/// \param ioStrand Strand object to convert.
/// \param degree Degree of the NUBS curves.
/// \return True if the conversion was successful.
///         False if the input strand object is invalid or
///         if the input degree is less than 1 or
///         a strand does not have enough CVs to create a NUBS curve.
///
/// \note The NUBS curve data structure could have different degrees for
///       different strands but in this example code,
///       all NUBS curves will that the same degree.
SIMPLE_NUBS_CURVE_DECL
bool strandToNUBSCurve(Bifrost::Object& ioStrand, Amino::uint_t degree);

/// \brief Sample a NUBS curve object to construct a strand object.
/// \param nubsCurve NUBS curve object to convert.
/// \param samplesPerSpan Number of samples per span.
/// \param ioStrand Strand object constructed from the input NUBS curve object.
/// \return True if the construction of the strand object was successful.
/// \note This function follows the pattern of populating an object found in the Bifrost Geometry
///       SDK. For example, Bifrost::Geometry::populateMesh().
/// \note No properties are transferred from the input NUBS curve object to the output strand
///       object.
SIMPLE_NUBS_CURVE_DECL
bool buildStrandFromNUBSCurve(Bifrost::Object const& nubsCurve,
                              Amino::uint_t          samplesPerSpan,
                              Bifrost::Object&       ioStrand);

} // namespace GeoSDK
} // namespace Examples
#endif // SIMPLE_NUBS_CURVE_H

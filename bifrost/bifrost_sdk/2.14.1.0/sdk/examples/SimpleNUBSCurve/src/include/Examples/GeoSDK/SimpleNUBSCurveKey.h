//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file SimpleNUBSCurveKey.h
/// \brief Simple NUBS Curve keys to use with Bifrost geometry objects.

#ifndef SIMPLE_NUBS_CURVE_KEY_H
#define SIMPLE_NUBS_CURVE_KEY_H

#include "SimpleNUBSCurveExport.h"

#include <Amino/Core/StringView.h>

namespace Examples {
namespace GeoSDK {

/// \brief  Additional keys to be used with the NUBS curve object.
/// \note   These keys are not part of the Bifrost canonical geometry keys.
///         They are used to access the data in the NUBS curve object.
///         They are used to create a NUBS curve knot Component Geo Property and
///         a NUBS curve knot values Data Geo Property.
///
/// \note   Bifrost Geometry data structure is described in the Bifrost Developer Help
///         section found at https://help.autodesk.com/view/BIFROST/ENU/
extern SIMPLE_NUBS_CURVE_DECL Amino::StringView const sStrandDegree;
extern SIMPLE_NUBS_CURVE_DECL Amino::StringView const sStrandKnotOffset;
extern SIMPLE_NUBS_CURVE_DECL Amino::StringView const sKnotComp;
extern SIMPLE_NUBS_CURVE_DECL Amino::StringView const sKnotValue;

} // namespace GeoSDK
} // namespace Examples

#endif // SIMPLE_NUBS_CURVE_KEY_H

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
/// \file GeoPropertyKey.h
///
/// \brief Geo Property key strings declaration.  Used as keys in Geometry Objects.
///

#ifndef BIFROST_GEOMETRY_GEO_PROPERTY_KEY_H
#define BIFROST_GEOMETRY_GEO_PROPERTY_KEY_H

#include <Bifrost/Geometry/GeometryExport.h>

#include <Amino/Core/BuiltInTypes.h>
#include <Amino/Core/String.h>
#include <Amino/Core/StringView.h>

namespace Bifrost
{
namespace Geometry
{

// General
extern BIFROST_GEOMETRY_DECL Amino::String const sNullString;
extern BIFROST_GEOMETRY_DECL Amino::String const sDccName;
extern BIFROST_GEOMETRY_DECL Amino::String const sComponentTagSuffix;
extern BIFROST_GEOMETRY_DECL Amino::String const sComponentSuffix;
extern BIFROST_GEOMETRY_DECL Amino::String const sComponentTagPrefix_point;
extern BIFROST_GEOMETRY_DECL Amino::String const sComponentTagPrefix_face;

// ComponentGeoProp
extern BIFROST_GEOMETRY_DECL Amino::String const sCount;

// DataGeoProp
extern BIFROST_GEOMETRY_DECL Amino::String const sTarget;
extern BIFROST_GEOMETRY_DECL Amino::String const sData;
extern BIFROST_GEOMETRY_DECL Amino::String const sDependsOn;
extern BIFROST_GEOMETRY_DECL Amino::String const sDefault;
extern BIFROST_GEOMETRY_DECL Amino::String const sInterp;
extern BIFROST_GEOMETRY_DECL Amino::String const sOffsetSuffix;

// RangeGeoProp
extern BIFROST_GEOMETRY_DECL Amino::String const sIndices;
extern BIFROST_GEOMETRY_DECL Amino::String const sIndexSuffix;

// ComponentGeoProperties
extern BIFROST_GEOMETRY_DECL Amino::String const sPointComp;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceComp;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceVertexComp;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelComp;
extern BIFROST_GEOMETRY_DECL Amino::String const sStrandComp;

// Volume DataGeoProperties
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelPosition;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFogDensity;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelMassDensity;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelSignedDistance;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelDepth;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelDetailSize;

extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelAcceleration;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelTemperature;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelIgnitionTemperature;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelPointRadius;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelDegreeOfFreedom;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelVorticity;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelExpansionRate;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFogDensitySignedDistance;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFlameLevelSet;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelCombustionRate;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFlameSpeed;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelRefinement;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelSignificance;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelSamplingError;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelSootEmission;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelCombustionMask;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelSootOxidationMask;

extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFuel;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFuelPropane;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFuelEthane;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFuelButane;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFuelMethane;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFuelPropylene;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFuelPropyne;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFuelPropadiene;

extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelGasCarbonDioxide;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelGasNitrogen;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelGasOxygen;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelGasVapor;

// Liquid properties
extern BIFROST_GEOMETRY_DECL Amino::String const sPointId;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointPassthroughId;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointSourceId;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointDroplet;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointSignedAirLiquidDistance;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointStickinessBandwidth;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointStickinessStrength;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointViscosity;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointVoxelTileTree;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointExpansionRate;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelFlipVelocity;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelPressure;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelRefinementNearColliders;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelSignedAirLiquidDistance;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelSignedCoarsenRefineDistance;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelSignedColliderDistance;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelStickinessBandwidth;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelStickinessStrength;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelChurn;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelPointCount;

// Point DataGeoProperties
extern BIFROST_GEOMETRY_DECL Amino::String const sPointColor;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointNormal;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointOrientation;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointPosition;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointSize;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointAge;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointSpin;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointMass;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointInstanceId;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointKinematic;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointFriction;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointUV;

// Velocity DataGeoProperties
extern BIFROST_GEOMETRY_DECL Amino::String const sPointVelocity;
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelVelocity;

// Strand DataGeoProperties
extern BIFROST_GEOMETRY_DECL Amino::String const sStrandOffset;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointStrandIndex;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointTangent;
extern BIFROST_GEOMETRY_DECL Amino::String const  sPointRatio;

extern BIFROST_GEOMETRY_DECL Amino::String const sPointLength;
extern BIFROST_GEOMETRY_DECL Amino::String const sStrandLength;

// Mesh DataGeoProperties
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceCenter;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceNormal;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceOffset;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceUV;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceVertex;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceVertexNormal;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceVertexUV;

// Volume RangeGeoProperties
extern BIFROST_GEOMETRY_DECL Amino::String const sVoxelTileTree;

// Instances properties
extern BIFROST_GEOMETRY_DECL Amino::String const sInstanceShape;
extern BIFROST_GEOMETRY_DECL Amino::String const sInstanceShapes;

// Material properties
extern BIFROST_GEOMETRY_DECL Amino::String const sRenderSettings;
extern BIFROST_GEOMETRY_DECL Amino::String const sMaterialSurface;
extern BIFROST_GEOMETRY_DECL Amino::String const sMaterialDisplacement;
extern BIFROST_GEOMETRY_DECL Amino::String const sMaterialVolume;
extern BIFROST_GEOMETRY_DECL Amino::String const sMaterialReferenceID;

// Operator properties
extern BIFROST_GEOMETRY_DECL Amino::String const sOperatorReferenceID;
extern BIFROST_GEOMETRY_DECL Amino::String const sOperators;

// Generic Data Geo property
extern BIFROST_GEOMETRY_DECL Amino::String const sGenericDataGeoProp;

// Accelerator properties
extern BIFROST_GEOMETRY_DECL Amino::String const sAcceleratorGeo;
extern BIFROST_GEOMETRY_DECL Amino::String const sAcceleratorGrid;
extern BIFROST_GEOMETRY_DECL Amino::String const sAcceleratorComponent;

// Image properties
extern BIFROST_GEOMETRY_DECL Amino::String const sImageDisplacement;
extern BIFROST_GEOMETRY_DECL Amino::String const sImageVelocity;

// Component mapping properties
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceSourceIndex;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointSourceIndex;
extern BIFROST_GEOMETRY_DECL Amino::String const sPointSourceWeight;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceVertexSourceIndex;
extern BIFROST_GEOMETRY_DECL Amino::String const sFaceVertexSourceWeight;

using Index = Amino::uint_t;

extern BIFROST_GEOMETRY_DECL const Geometry::Index kInvalidIndex;
extern BIFROST_GEOMETRY_DECL const Geometry::Index kDeletedElement;

// Helper functions
/// \todo BIFROST-10097 - To be deprecated
BIFROST_GEOMETRY_DECL Amino::StringView cstr_to_asv(const char* cstr);
} // namespace Geometry
} // namespace Bifrost

#endif // GEO_PROPERTY_KEY_H

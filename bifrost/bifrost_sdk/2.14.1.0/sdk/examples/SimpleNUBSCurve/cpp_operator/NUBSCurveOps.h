//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef NUBS_CURVE_OPS_H
#define NUBS_CURVE_OPS_H

#include "NUBSCurveOpsExport.h"

#include <Bifrost/Object/Object.h>

#include <Amino/Core/PtrFwd.h>
#include <Amino/Cpp/Annotate.h>

namespace Examples {
namespace GeoSDK {

/// \brief Convert a strand to a NUBS curve
///
/// NUBS properties will be added to each strand of the input strand object.
/// The number of points (CVs) per strand must be greater than the degree +1.
///
/// \param [in,out] strand The input strand to convert to NUBS curve
/// \param [in] degree The degree of the NUBS curve to create
/// \return True if the conversion was successful.
NUBS_CURVE_OPS_DECL
bool strand_to_nubs_curve(
    Bifrost::Object& strand AMINO_ANNOTATE("Amino::InOut outName=strand_nubs_curve"), int degree)
    AMINO_ANNOTATE("Amino::Node outName=success");

/// \brief Convert a NUBS curve to a strand. A new strand object will be created.
/// \param [in] strand_nubs_curve The input NUBS curve to convert to strand.
/// \param [in] nb_samples_per_span The number of samples per span.
/// \param [out] out_strand The new output strand object.
/// \return  True if the conversion was successful.
NUBS_CURVE_OPS_DECL
bool nubs_curve_to_strand(Bifrost::Object const&              strand_nubs_curve,
                          int                                 nb_samples_per_span,
                          Amino::MutablePtr<Bifrost::Object>& out_strand)
    AMINO_ANNOTATE("Amino::Node outName=success");

} // namespace GeoSDK
} // namespace Examples

#endif // NUBS_CURVE_OPS_H

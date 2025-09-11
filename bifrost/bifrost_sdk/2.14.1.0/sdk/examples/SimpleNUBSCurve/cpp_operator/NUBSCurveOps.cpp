//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They
// may not be disclosed to, copied  or used by any third party without the
// prior written consent of Autodesk, Inc.
// =============================================================================
//+

#include "NUBSCurveOps.h"

#include <Examples/GeoSDK/SimpleNUBSCurve.h>

bool Examples::GeoSDK::strand_to_nubs_curve(Bifrost::Object& strand, int degree) {
    Amino::uint_t validDegree = (degree < 1) ? 1 : static_cast<Amino::uint_t>(degree);
    return Examples::GeoSDK::strandToNUBSCurve(strand, validDegree);
}

bool Examples::GeoSDK::nubs_curve_to_strand(Bifrost::Object const&              strand_nubs_curve,
                                            int                                 nb_samples_per_span,
                                            Amino::MutablePtr<Bifrost::Object>& out_strand) {
    Amino::uint_t validNbSamplesPerSpan =
        (nb_samples_per_span < 0) ? 0 : static_cast<Amino::uint_t>(nb_samples_per_span);
    out_strand = Bifrost::createObject();
    return Examples::GeoSDK::buildStrandFromNUBSCurve(strand_nubs_curve, validNbSamplesPerSpan,
                                                      *out_strand);
}

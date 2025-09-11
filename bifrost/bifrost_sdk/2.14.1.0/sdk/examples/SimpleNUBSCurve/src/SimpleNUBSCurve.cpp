//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//

#include <Examples/GeoSDK/SimpleNUBSCurve.h>

#include <Examples/GeoSDK/SimpleNUBSCurveKey.h>
#include <Examples/GeoSDK/SimpleNUBSCurveView.h>

#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Geometry/GeometryTypes.h>
#include <Bifrost/Geometry/Primitives.h>
#include <Bifrost/Geometry/Validator.h>

#include <limits>

using Index = Bifrost::Geometry::Index;
static_assert(std::is_same<Index, Amino::uint_t>::value, "Index type mismatch");

// Functions
bool Examples::GeoSDK::isNUBSCurveValid(const Bifrost::Object& nubsCurve,
                                        Amino::String*         statusMessage) {
    //
    // The validation of a Bifrost strand is extended for NUBS curves since a NUBS curve is added
    // to an existing Bifrost strand object.
    //
    // Extend for NUBS curves by checking the
    // Bifrost geometry properties added for NUBS:
    // - strand_degree
    // - strand_knot_offset
    // - knot_component
    // - knot_value

    auto setStatusMessage = [&](Amino::String message) {
        if (statusMessage) {
            *statusMessage = std::move(message);
        }
    };

    // Check strand object using the SDK's strand validator.
    Bifrost::Geometry::StrandValidator strandValidator;
    if (!strandValidator.validate(nubsCurve)) {
        setStatusMessage("Invalid strand object");
        return false;
    }

    // Check the NUBS properties are present
    // Note: that the strand validator will catch missing geometry properties that are targeted by
    // other existing geometry properties. However, it will not catch a non-canonical missing data
    // geometry property. For example, if the knotValue data geometry property is missing, the
    // validator will not catch it.
    if (!nubsCurve.hasProperty(sStrandDegree) || !nubsCurve.hasProperty(sStrandKnotOffset) ||
        !nubsCurve.hasProperty(sKnotComp) || !nubsCurve.hasProperty(sKnotValue)) {
        setStatusMessage("Missing NUBS properties");
        return false;
    }

    // Check the NUBS data is present and of the correct type.
    auto const strandDegrees =
        Bifrost::Geometry::getDataGeoPropValues<Amino::uint_t>(nubsCurve, sStrandDegree);
    auto const strandKnotOffsets =
        Bifrost::Geometry::getDataGeoPropValues<Index>(nubsCurve, sStrandKnotOffset);
    auto const knotValues = Bifrost::Geometry::getDataGeoPropValues<float>(nubsCurve, sKnotValue);

    // Note: Some checks are already performed by the strand validator since all validators test all
    // data geometry properties for size consistency with the number of elements found in the
    // component geometry property they target. The test checks that the size of the data array of a
    // data geometry property is least the number of elements found in the component geometry
    // property it targets.
    //
    // However, the generic validator code does not check the type of the data arrays.
    // The above getDataGeoPropValues() functions will return a nullptr if the data is not of the
    // demanded type.
    //
    // Also, an offset array is always one more than the number of strands and cannot be empty.
    if (!strandDegrees || !strandKnotOffsets || !knotValues || strandKnotOffsets->empty()) {
        setStatusMessage("Invalid NUBS data");
        return false;
    }

    // Check the NUBS offsets
    // Number of offsets is always one more than the number of strands.
    auto const nbStrands =
        Bifrost::Geometry::getElementCount(nubsCurve, Bifrost::Geometry::sStrandComp);
    if (nbStrands != strandKnotOffsets->size() - 1) {
        setStatusMessage("Invalid number of strand knot offsets");
        return false;
    }

    // Number of knot components is the size of the knot values array.
    auto const nbKnotValues = Bifrost::Geometry::getElementCount(nubsCurve, sKnotComp);
    if (nbKnotValues != knotValues->size()) {
        setStatusMessage("Invalid number of knot values");
        return false;
    }

    // The last strand knot offset value is equal to the number of knot values.
    if (nbKnotValues != strandKnotOffsets->back()) {
        setStatusMessage("Invalid last strand offset that should be the number of knot values");
        return false;
    }

    // First knot offset is always 0
    if (strandKnotOffsets->front() != 0) {
        setStatusMessage("Invalid first strand offset that should be 0");
        return false;
    }

    // Knot offsets are monotonically increasing
    for (size_t i = 1; i < strandKnotOffsets->size(); ++i) {
        if (strandKnotOffsets->at(i - 1) > strandKnotOffsets->at(i)) {
            setStatusMessage("Invalid strand offset that should be monotonically increasing");
            return false;
        }
    }

    // Check the NUBS data for each strand (NUBS curve)
    // Note: The Bifrost strand object has already been checked at the beginning of this function.
    auto const strandOffsets =
        Bifrost::Geometry::getDataGeoPropValues<Index>(nubsCurve, Bifrost::Geometry::sStrandOffset);

    for (size_t i = 0; i < nbStrands; ++i) {
        auto const degree         = strandDegrees->at(i);
        auto const cvLowOffset    = strandOffsets->at(i);
        auto const cvHighOffset   = strandOffsets->at(i + 1);
        auto const knotLowOffset  = strandKnotOffsets->at(i);
        auto const knotHighOffset = strandKnotOffsets->at(i + 1);

        // Degree is always greater than 0
        if (degree < 1) {
            setStatusMessage("Invalid degree");
            return false;
        }

        // Number of control points plus order is always equal to the number of knots
        if ((cvHighOffset - cvLowOffset) + degree + 1 != (knotHighOffset - knotLowOffset)) {
            setStatusMessage(
                "Invalid relation between a curve's degree and the number of control points and "
                "knots");
            return false;
        }

        // Knots are monotonically increasing
        for (size_t j = knotLowOffset + 1; j < knotHighOffset; ++j) {
            if (knotValues->at(j - 1) > knotValues->at(j)) {
                setStatusMessage("Invalid knot values that should be monotonically increasing");
                return false;
            }
        }
    }

    setStatusMessage("Valid NUBS curve");
    return true;
}

bool Examples::GeoSDK::strandToNUBSCurve(Bifrost::Object& ioStrand, Amino::uint_t degree) {
    Bifrost::Geometry::StrandValidator strandValidator;
    if (!strandValidator.validate(ioStrand)) {
        return false;
    }

    if (degree < 1) {
        return false;
    }

    size_t const order = degree + 1;
    // Check that we have the necessary number of control points (point_position) to create
    // NUBS of the given degree.
    auto const nbStrands =
        Bifrost::Geometry::getElementCount(ioStrand, Bifrost::Geometry::sStrandComp);
    auto const strandOffsets =
        Bifrost::Geometry::getDataGeoPropValues<Index>(ioStrand, Bifrost::Geometry::sStrandOffset);

    for (size_t i = 0; i < nbStrands; ++i) {
        auto const cvLowOffset  = strandOffsets->at(i);
        auto const cvHighOffset = strandOffsets->at(i + 1);

        // Need at least order control points
        if (cvHighOffset - cvLowOffset < order) {
            return false;
        }
    }

    // Allocate the arrays for degrees and knots
    //
    // Note that we have an array of degrees so you can have
    // different per span degree values.  However, in this example code,
    // we use the same degree for all strands.

    auto strandDegrees     = Amino::newMutablePtr<Amino::Array<Amino::uint_t>>(nbStrands, degree);
    auto strandKnotOffsets = Amino::newMutablePtr<Amino::Array<Index>>(nbStrands + 1);

    // Offsets start at 0
    strandKnotOffsets->at(0) = 0;
    for (size_t i = 1; i < nbStrands + 1; ++i) {
        auto const cvLowOffset  = strandOffsets->at(i - 1);
        auto const cvHighOffset = strandOffsets->at(i);

        auto const nbKnots       = cvHighOffset - cvLowOffset + degree + 1;
        strandKnotOffsets->at(i) = strandKnotOffsets->at(i - 1) + nbKnots;
    }

    // Reminder offset arrays have nbStrands+1 elements.
    // Last element is the number of knots, in this case
    auto const nbKnotValues = strandKnotOffsets->at(nbStrands);
    auto       knotValues   = Amino::newMutablePtr<Amino::Array<float>>(nbKnotValues);
    for (size_t i = 0; i < nbStrands; ++i) {
        auto const knotLowOffset  = strandKnotOffsets->at(i);
        auto const knotHighOffset = strandKnotOffsets->at(i + 1);

        // The knots will be order 0.0 values
        // followed by (#Knots - order - order ) +1.0 values
        // finished with order values of (#knows - order - degree)
        // Ex.:  11 knots and degree 3 will be:
        //  order 0.0 values   11-4-4 values  order values of 11-4-3
        //  0.0,0.0,0.0,0.0     1.0,2.0,3.0    4.0,4.0,4.0,4.0

        assert(knotHighOffset - knotLowOffset >= order + order);

        // Set the knots...
        auto knotValue = 0.0F;
        for (auto j = knotLowOffset; j < knotLowOffset + order; ++j) {
            knotValues->at(j) = knotValue;
        }
        knotValue += 1.0F;
        for (auto j = knotLowOffset + order; j < knotHighOffset - order; ++j) {
            knotValues->at(j) = knotValue;
            knotValue += 1.0F;
        }
        for (auto j = knotHighOffset - order; j < knotHighOffset; ++j) {
            knotValues->at(j) = knotValue;
        }
    }

    // Add the NUBS curve properties to the strand object
    auto knotCompProp = Bifrost::createObject();
    Bifrost::Geometry::populateComponentGeoProperty(nbKnotValues, *knotCompProp);
    ioStrand.setProperty(sKnotComp, std::move(knotCompProp));

    auto knotValueDataProp = Bifrost::createObject();
    Bifrost::Geometry::populateDataGeoProperty(0.0F, std::move(knotValues),
                                               Examples::GeoSDK::sKnotComp, *knotValueDataProp);
    ioStrand.setProperty(sKnotValue, std::move(knotValueDataProp));

    auto degreeDataProp = Bifrost::createObject();
    Bifrost::Geometry::populateDataGeoProperty(degree, std::move(strandDegrees),
                                               Bifrost::Geometry::sStrandComp, *degreeDataProp);
    ioStrand.setProperty(sStrandDegree, std::move(degreeDataProp));

    auto knotOffsetDataProp = Bifrost::createObject();
    Bifrost::Geometry::populateDataGeoProperty(static_cast<Index>(0), std::move(strandKnotOffsets),
                                               Bifrost::Geometry::sStrandComp, *knotOffsetDataProp);
    ioStrand.setProperty(sStrandKnotOffset, std::move(knotOffsetDataProp));

    return true;
}

bool Examples::GeoSDK::buildStrandFromNUBSCurve(Bifrost::Object const& nubsCurve,
                                                Amino::uint_t          samplesPerSpan,
                                                Bifrost::Object&       ioStrand) {
    if (!Examples::GeoSDK::isNUBSCurveValid(nubsCurve)) {
        return false;
    }

    // For each NUBS curve (strand NUBS curve) sample and create a strand.
    Examples::GeoSDK::NUBSCurveView curveView(nubsCurve);

    auto const    nbCurves         = curveView.getCurveCount();
    auto          newStrandOffsets = Amino::newMutablePtr<Amino::Array<Index>>(nbCurves + 1);
    Amino::uint_t nbSamples        = 0;
    newStrandOffsets->at(0)        = 0;
    for (size_t iCurve = 0; iCurve < nbCurves; ++iCurve) {
        curveView.setCurveIndex(static_cast<Amino::uint_t>(iCurve));

        auto const nbSpans = curveView.getSpanCount();

        // Samples between knots: nbSpans * samplesPerSpan
        // +(nbSpans-1) for the number of knots between start knot and end knot (Not counting knot
        // multiplicities). +2 for the start and end knot values
        nbSamples += nbSpans * samplesPerSpan + (nbSpans + 1);
        newStrandOffsets->at(iCurve + 1) = nbSamples;
    }

    auto newStrandPoints = Amino::newMutablePtr<Amino::Array<Bifrost::Math::float3>>(nbSamples);
    for (size_t iCurve = 0; iCurve < nbCurves; ++iCurve) {
        curveView.setCurveIndex(static_cast<Amino::uint_t>(iCurve));
        auto samplesToEvaluate = curveView.getSamplesPerSpan(samplesPerSpan);

        assert(samplesToEvaluate.size() ==
               newStrandOffsets->at(iCurve + 1) - newStrandOffsets->at(iCurve));

        auto const startIndex = newStrandOffsets->at(iCurve);

        for (size_t iSample = 0; iSample < samplesToEvaluate.size(); ++iSample) {
            auto const res = curveView.evaluate(samplesToEvaluate[iSample]);
            newStrandPoints->at(startIndex + iSample) = res;
        }
    }

    return Bifrost::Geometry::populateStrand(std::move(newStrandPoints),
                                             std::move(newStrandOffsets), ioStrand);
}

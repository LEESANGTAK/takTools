//-
// ===========================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// ===========================================================================
//+

#include <gtest/gtest.h>

#include <Examples/GeoSDK/SimpleNUBSCurve.h>
#include <Examples/GeoSDK/SimpleNUBSCurveKey.h>
#include <Examples/GeoSDK/SimpleNUBSCurveView.h>

#include <Bifrost/Geometry/DebugDump.h>
#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Geometry/Primitives.h>
#include <Bifrost/Geometry/Validator.h>
#include <Bifrost/Math/Types.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Core/String.h>

#include <iostream>
#include <sstream>

using Index = Bifrost::Geometry::Index;
static_assert(std::is_same<Index, Amino::uint_t>::value, "Index type mismatch");

namespace {
/// \brief Create a basic strand object with 2 strands.
/// \return Strand object with two strands. One with 5 points and one with 6.
///         Can support NUBS curve of degree 4 and less for the first strand.
///         Can support NUBS curve of degree 5 and less for the second strand.
/// \note   Remember that you need at least order (degree+1) points to create a NUBS curve.
Amino::MutablePtr<Bifrost::Object> createTestStrand() {
    // Create empty object
    auto strand = Bifrost::createObject();
    // Create strand data - output is an immutable pointer to the immutable data.
    auto strandPoints = Amino::newClassPtr<Amino::Array<Bifrost::Math::float3>>(
        std::initializer_list<Bifrost::Math::float3>{{0, 0, 0},
                                                     {1, 1, 0},
                                                     {2, 1, 0},
                                                     {3, 2, 0},
                                                     {4, 0, 0},
                                                     {5, 0, 0},
                                                     {6, -1, 0},
                                                     {7, -1, 0},
                                                     {8, -2, 0},
                                                     {9, -1, 0},
                                                     {10, 0, 0}});
    // Create strand offsets - output is an immutable pointer to the immutable data.
    // We have two strands, one with 5 (5-0) points and one with 6 (11-5) points.
    auto strandOffsets =
        Amino::newClassPtr<Amino::Array<Index>>(std::initializer_list<Index>{0, 5, 11});
    // Populate the strand object with the strand data.
    Bifrost::Geometry::populateStrand(std::move(strandPoints), std::move(strandOffsets), *strand);

    return strand;
}

class TestNUBSCurve : public ::testing::Test {
protected:
    TestNUBSCurve() = default;

    ~TestNUBSCurve() override = default;

    void SetUp() override {
        if (nullptr == strandNUBSCurve) {
            auto newStrand = createTestStrand();
            ASSERT_TRUE(newStrand) << "Failed to create mutable strand";

            // Convert to NUBS curve.
            // Adds the NUBS curve properties to the strand object.
            // Each strand must have at least degree+1 points (control points for a NUBS curve)
            ASSERT_TRUE(Examples::GeoSDK::strandToNUBSCurve(*newStrand, 3 /*degree*/))
                << "Failed to convert strand to NUBS curve";

            strandNUBSCurve = newStrand.toImmutable(); // or std::move(newStrand);
        }
    }
    void TearDown() override {
        ASSERT_TRUE(strandNUBSCurve) << "strandNUBSCurve incorrect at end of test";
    }

    Amino::MutablePtr<Bifrost::Object> getMutableNUBSCurveCopy() {
        return Amino::Ptr<Bifrost::Object>(strandNUBSCurve).toMutable();
    }

protected:
    Amino::Ptr<Bifrost::Object> strandNUBSCurve;
};

} // namespace

TEST(SimpleNUBSCurveTest, TestCreateNUBSCurve) {
    // Test creation of a NUBS curve object.
    //
    // Create a set of copies that are just refcounted pointers to the same data.
    // Use Amino PtrGuard to do the modification.
    // PtrGuard usage is scoped and the object is immutable again when the PtrGuard goes out of
    // scope.

    // Create a strand object with 2 strands.
    auto sourceStrand = createTestStrand().toImmutable();
    ASSERT_TRUE(sourceStrand) << "Failed to create immutable strand";

    auto strandNUBSCurveDeg0 = sourceStrand;
    auto strandNUBSCurveDeg1 = sourceStrand;
    auto strandNUBSCurveDeg2 = sourceStrand;
    auto strandNUBSCurveDeg3 = sourceStrand;
    auto strandNUBSCurveDeg4 = sourceStrand;
    auto strandNUBSCurveDeg5 = sourceStrand;

    // Note that createPtrGuard does not use the Amino::PtrGuardUniqueFlag{} flag because
    // none of the strandNUBSCurveDeg* are unique owners.
    {
        auto mutableNUBSCurveDeg0 = Amino::createPtrGuard(strandNUBSCurveDeg0);
        ASSERT_FALSE(Examples::GeoSDK::strandToNUBSCurve(*mutableNUBSCurveDeg0, 0 /*degree*/))
            << "Should not be able to create NUBS curve of degree 0";

        auto mutableNUBSCurveDeg1 = Amino::createPtrGuard(strandNUBSCurveDeg1);
        ASSERT_TRUE(Examples::GeoSDK::strandToNUBSCurve(*mutableNUBSCurveDeg1, 1 /*degree*/))
            << "Failed to convert strand to NUBS curve of degree 1";

        auto mutableNUBSCurveDeg2 = Amino::createPtrGuard(strandNUBSCurveDeg2);
        ASSERT_TRUE(Examples::GeoSDK::strandToNUBSCurve(*mutableNUBSCurveDeg2, 2 /*degree*/))
            << "Failed to convert strand to NUBS curve of degree 2";

        auto mutableNUBSCurveDeg3 = Amino::createPtrGuard(strandNUBSCurveDeg3);
        ASSERT_TRUE(Examples::GeoSDK::strandToNUBSCurve(*mutableNUBSCurveDeg3, 3 /*degree*/))
            << "Failed to convert strand to NUBS curve of degree 3";

        auto mutableNUBSCurveDeg4 = Amino::createPtrGuard(strandNUBSCurveDeg4);
        ASSERT_TRUE(Examples::GeoSDK::strandToNUBSCurve(*mutableNUBSCurveDeg4, 4 /*degree*/))
            << "Failed to convert strand to NUBS curve of degree 4";

        auto mutableNUBSCurveDeg5 = Amino::createPtrGuard(strandNUBSCurveDeg5);
        ASSERT_FALSE(Examples::GeoSDK::strandToNUBSCurve(*mutableNUBSCurveDeg5, 5 /*degree*/))
            << "Should not be able to create NUBS curve of degree 5. Strands have less than 6 "
               "(degree+1) control points.";
    }

    ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*strandNUBSCurveDeg0))
        << "Should not be a NUBS curve of degree 0";
    ASSERT_TRUE(Examples::GeoSDK::isNUBSCurveValid(*strandNUBSCurveDeg1))
        << "Invalid NUBS curve of degree 1";
    ASSERT_TRUE(Examples::GeoSDK::isNUBSCurveValid(*strandNUBSCurveDeg2))
        << "Invalid NUBS curve of degree 2";
    ASSERT_TRUE(Examples::GeoSDK::isNUBSCurveValid(*strandNUBSCurveDeg3))
        << "Invalid NUBS curve of degree 3";
    ASSERT_TRUE(Examples::GeoSDK::isNUBSCurveValid(*strandNUBSCurveDeg4))
        << "Invalid NUBS curve of degree 4";
    ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*strandNUBSCurveDeg5))
        << "Should not be a NUBS curve of degree 5";
}

TEST_F(TestNUBSCurve, TestIsNUBSCurveValid) {
    // Test validation of a NUBS curve object.
    //
    // Starts from the strandNUBSCurve object created in the fixture.
    // Then mutate a refcounted copy of strandNUBSCurve to create invalid NUBS curves.
    //
    // REMINDER: toMutable(), whatever the refcount, will reset the Amino::Ptr.
    //
    // Amino PtrGuard is used to edit array of data.

    // After initialization the curve is valid
    ASSERT_TRUE(Examples::GeoSDK::isNUBSCurveValid(*strandNUBSCurve)) << "Invalid NUBS curve";

    // Remove part of strand data
    {
        auto badStrandForCurve = getMutableNUBSCurveCopy();
        badStrandForCurve->eraseProperty(Bifrost::Geometry::sPointPosition);
        Amino::String statusMessage;
        // Should not be a NUBS curve without strand points
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badStrandForCurve, &statusMessage));
        std::cout << "Status message 1: " << statusMessage.c_str() << std::endl;
    }

    // Missing NUBS property
    {
        auto missingNUBSProperty = getMutableNUBSCurveCopy();
        missingNUBSProperty->eraseProperty(Examples::GeoSDK::sKnotValue);
        Amino::String statusMessage;
        // Should not be a NUBS curve without the NUBS knot component
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*missingNUBSProperty, &statusMessage));
        std::cout << "Status message 2: " << statusMessage.c_str() << std::endl;
    }

    // Bad NUBS data
    {
        auto badNUBSData = getMutableNUBSCurveCopy();
        auto nbKnotValues =
            Bifrost::Geometry::getElementCount(*badNUBSData, Examples::GeoSDK::sKnotComp);
        // Knot values are floats we set them to int... Bad data
        auto knotValuesOfBadType = Amino::newClassPtr<Amino::Array<int>>(nbKnotValues);
        Bifrost::Geometry::setDataGeoPropValues(Examples::GeoSDK::sKnotValue,
                                                std::move(knotValuesOfBadType), *badNUBSData);

        Amino::String statusMessage;
        // Should not be a NUBS curve without correct NUBS data
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badNUBSData, &statusMessage));
        std::cout << "Status message 3: " << statusMessage.c_str() << std::endl;
    }

    // Bad number of knot offsets
    {
        auto badKnotOffsets = getMutableNUBSCurveCopy();
        auto offsetArray    = Bifrost::Geometry::getDataGeoPropValues<Index>(
            *badKnotOffsets, Examples::GeoSDK::sStrandKnotOffset);
        {
            auto editOffsetArray = Amino::createPtrGuard(offsetArray);
            editOffsetArray->pop_back();
        }
        Bifrost::Geometry::setDataGeoPropValues(Examples::GeoSDK::sStrandKnotOffset,
                                                std::move(offsetArray), *badKnotOffsets);
        Amino::String statusMessage;
        // Should not be a NUBS curve without correct strand knot offsets
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badKnotOffsets, &statusMessage));
        std::cout << "Status message 4: " << statusMessage.c_str() << std::endl;
    }

    // Bad number of knot values - less knot values is caught by the validator and
    // more knot values are accepted by the validator because we have enough data.
    // However, isNUBSCurveValid code checks for exact number of knot values.
    {
        auto badKnotValues = getMutableNUBSCurveCopy();
        auto knotValues    = Bifrost::Geometry::getDataGeoPropValues<float>(
            *badKnotValues, Examples::GeoSDK::sKnotValue);
        {
            auto editKnotValues = Amino::createPtrGuard(knotValues);
            editKnotValues->push_back(1.0F);
        }
        Bifrost::Geometry::setDataGeoPropValues(Examples::GeoSDK::sKnotValue, std::move(knotValues),
                                                *badKnotValues);
        Amino::String statusMessage;
        // Should not be a NUBS curve without correct strand knot values
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badKnotValues, &statusMessage));
        std::cout << "Status message 5: " << statusMessage.c_str() << std::endl;
    }

    // Bad last offset value - geometry offset arrays have one more element than the number of
    // elements of the component they target.  That value is the number of elements of the
    // component the offset array is used to index.
    //
    // In our case, the strandKnotOffset array has one more element than the number of curves
    // (strands). Its last element is the number of knots for all the curves (strands).
    {
        auto badLastOffset = getMutableNUBSCurveCopy();
        auto offsetArray   = Bifrost::Geometry::getDataGeoPropValues<Index>(
            *badLastOffset, Examples::GeoSDK::sStrandKnotOffset);
        {
            auto editOffsetArray    = Amino::createPtrGuard(offsetArray);
            editOffsetArray->back() = 10000; // Way more than the number of knots
        }

        Bifrost::Geometry::setDataGeoPropValues(Examples::GeoSDK::sStrandKnotOffset,
                                                std::move(offsetArray), *badLastOffset);
        Amino::String statusMessage;
        // Should not be a NUBS curve without correct last strand offsets
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badLastOffset, &statusMessage));
        std::cout << "Status message 6: " << statusMessage.c_str() << std::endl;
    }

    // Bad first offset value - geometry offset arrays always start with 0.
    {
        auto badFirstOffset = getMutableNUBSCurveCopy();
        auto offsetArray    = Bifrost::Geometry::getDataGeoPropValues<Index>(
            *badFirstOffset, Examples::GeoSDK::sStrandKnotOffset);
        {
            auto editOffsetArray     = Amino::createPtrGuard(offsetArray);
            editOffsetArray->front() = 1000; // Should be 0
        }

        Bifrost::Geometry::setDataGeoPropValues(Examples::GeoSDK::sStrandKnotOffset,
                                                std::move(offsetArray), *badFirstOffset);
        Amino::String statusMessage;
        // Should not be a NUBS curve without correct first strand offsets
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badFirstOffset, &statusMessage));
        std::cout << "Status message 7: " << statusMessage.c_str() << std::endl;
    }

    // Non monotonic offset array - geometry offset arrays are monotonic.
    // In the case of knotStrandOffsets, the entries are the cumulative sums
    // of the number of knots per curve.
    {
        auto badOffsetArray = getMutableNUBSCurveCopy();
        auto offsetArray    = Bifrost::Geometry::getDataGeoPropValues<Index>(
            *badOffsetArray, Examples::GeoSDK::sStrandKnotOffset);
        {
            auto editOffsetArray   = Amino::createPtrGuard(offsetArray);
            editOffsetArray->at(1) = 50000; // Should be greater than the previous value and
                                            // smaller than the next value.
        }

        Bifrost::Geometry::setDataGeoPropValues(Examples::GeoSDK::sStrandKnotOffset,
                                                std::move(offsetArray), *badOffsetArray);
        Amino::String statusMessage;
        // Should not be a NUBS curve without monotonic strand offsets
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badOffsetArray, &statusMessage));
        std::cout << "Status message 8: " << statusMessage.c_str() << std::endl;
    }

    // Invalid degree
    {
        auto badDegree = getMutableNUBSCurveCopy();
        auto degrees   = Bifrost::Geometry::getDataGeoPropValues<Amino::uint_t>(
            *badDegree, Examples::GeoSDK::sStrandDegree);
        {
            auto editDegrees   = Amino::createPtrGuard(degrees);
            editDegrees->at(0) = 0; // Should be >= 1
        }

        Bifrost::Geometry::setDataGeoPropValues(Examples::GeoSDK::sStrandDegree, std::move(degrees),
                                                *badDegree);
        Amino::String statusMessage;
        // Should not be a NUBS curve with invalid degree
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badDegree, &statusMessage));
        std::cout << "Status message 9: " << statusMessage.c_str() << std::endl;
    }

    // Invalid #CVs + degree + 1 == #knots for a curve
    {
        auto badNbCVs = getMutableNUBSCurveCopy();
        auto degrees  = Bifrost::Geometry::getDataGeoPropValues<Amino::uint_t>(
            *badNbCVs, Examples::GeoSDK::sStrandDegree);
        {
            auto editDegrees   = Amino::createPtrGuard(degrees);
            editDegrees->at(0) = 50000; // Should be 3
        }

        Bifrost::Geometry::setDataGeoPropValues(Examples::GeoSDK::sStrandDegree, std::move(degrees),
                                                *badNbCVs);
        Amino::String statusMessage;
        // Should not be a NUBS curve with invalid relationship between #CVs, degree and #knots
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badNbCVs, &statusMessage));
        std::cout << "Status message 10: " << statusMessage.c_str() << std::endl;
    }

    // Non monotonic knot values
    {
        auto badKnotValues = getMutableNUBSCurveCopy();
        auto knotValues    = Bifrost::Geometry::getDataGeoPropValues<float>(
            *badKnotValues, Examples::GeoSDK::sKnotValue);
        {
            auto editKnotValues = Amino::createPtrGuard(knotValues);
            // Should be greater than the previous value and smaller than the next value.
            editKnotValues->at(1) = 1000.0F;
        }

        Bifrost::Geometry::setDataGeoPropValues(Examples::GeoSDK::sKnotValue, std::move(knotValues),
                                                *badKnotValues);
        Amino::String statusMessage;
        // Should not be a NUBS curve with non monotonic knot values
        ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*badKnotValues, &statusMessage));
        std::cout << "Status message 11: " << statusMessage.c_str() << std::endl;
    }
}

TEST_F(TestNUBSCurve, TestStrandToNUBSCurve) {
    // Test conversion of a strand object to a NUBS curve object.
    //
    // Starts from the strandNUBSCurve object created in the fixture.
    // Check validity and use the NUBSCurveView to check the data.

    constexpr Amino::uint_t   expectedNbSpansCurve1 = 3;
    const Amino::Array<float> expectedSpanKnotsCurve1{0.0F, 1.0F, 2.0F, 3.0F};
    constexpr Amino::uint_t   expectedNbCurves        = 2;
    const float               expectedStartKnotCurve0 = 0.0F;
    const float               expectedEndKnotCurve0   = 2.0F;

    // Dump the NUBS curve object
    std::stringstream ssOut;
    Bifrost::Geometry::debugDump(ssOut, *strandNUBSCurve);
    std::cout << ssOut.str() << std::endl;

    ASSERT_TRUE(Examples::GeoSDK::isNUBSCurveValid(*strandNUBSCurve)) << "Invalid NUBS curve";

    // Check we have data
    // It was checked by isNUBSCurveValid that we have the correct number of strands.
    // This shows that you can get to NUBS curve properties as any other strand properties.
    auto knotValues    = Bifrost::Geometry::getDataGeoPropValues<float>(*strandNUBSCurve,
                                                                     Examples::GeoSDK::sKnotValue);
    auto controlPoints = Bifrost::Geometry::getDataGeoPropValues<Bifrost::Math::float3>(
        *strandNUBSCurve, Bifrost::Geometry::sPointPosition);
    auto degrees = Bifrost::Geometry::getDataGeoPropValues<Amino::uint_t>(
        *strandNUBSCurve, Examples::GeoSDK::sStrandDegree);
    auto knotOffsets = Bifrost::Geometry::getDataGeoPropValues<Index>(
        *strandNUBSCurve, Examples::GeoSDK::sStrandKnotOffset);
    auto curveOffsets = Bifrost::Geometry::getDataGeoPropValues<Index>(
        *strandNUBSCurve, Bifrost::Geometry::sStrandOffset);

    ASSERT_TRUE(knotValues) << "Failed to get knot values";
    ASSERT_TRUE(controlPoints) << "Failed to get control points";
    ASSERT_TRUE(degrees) << "Failed to get degrees";
    ASSERT_TRUE(knotOffsets) << "Failed to get knot offsets";
    ASSERT_TRUE(curveOffsets) << "Failed to get curve offsets";

    // Create a view on the NUBS curve object
    // It is read-only and it is valid as long as the strand object is alive...
    // It will crash if the NUBS curve view is used after the strand object is destroyed.
    Examples::GeoSDK::NUBSCurveView curveView(*strandNUBSCurve);

    // Get number of curves (nb of strands)
    auto nbCurves = curveView.getCurveCount();
    ASSERT_EQ(nbCurves, expectedNbCurves);

    // Test some calls with the first curve (startKnot, endKnot values...)
    curveView.setCurveIndex(0 /*curveIndex*/);

    // Get start and end knots of the curve's parametric domain.
    auto startKnot = curveView.getStartKnotValue();
    auto endKnot   = curveView.getEndKnotValue();
    ASSERT_LE(startKnot, endKnot);
    ASSERT_FLOAT_EQ(startKnot, expectedStartKnotCurve0);
    ASSERT_FLOAT_EQ(endKnot, expectedEndKnotCurve0);

    // Trace: Evaluate the curve at start and end knots
    std::cout << "Trace: Evaluate the curve at start and end knots" << std::endl;
    auto res = curveView.evaluate(startKnot);
    std::cout << "Evaluated curve at " << startKnot << " : " << res.x << ", " << res.y << ", "
              << res.z << std::endl;

    res = curveView.evaluate(endKnot);
    std::cout << "Evaluated curve at " << endKnot << " : " << res.x << ", " << res.y << ", "
              << res.z << std::endl;

    // Check clamping...
    auto badStartKnot  = startKnot - 1.0F;
    auto badEndKnot    = endKnot + 1.0F;
    auto goodStartKnot = curveView.clamp(badStartKnot);
    auto goodEndKnot   = curveView.clamp(badEndKnot);

    ASSERT_FLOAT_EQ(goodStartKnot, startKnot);
    ASSERT_FLOAT_EQ(goodEndKnot, endKnot);

    // Test calls with second curve.
    // The span-related calls.
    curveView.setCurveIndex(1 /*curveIndex*/);

    // Number of spans in the curve (number of distinct knots for the parametric domain.
    auto nbSpans = curveView.getSpanCount();
    ASSERT_EQ(nbSpans, expectedNbSpansCurve1);

    auto spanKnots = curveView.getSpanKnots();
    ASSERT_EQ(spanKnots.size(), expectedSpanKnotsCurve1.size());

    for (size_t i = 0; i < nbSpans; ++i) {
        ASSERT_FLOAT_EQ(spanKnots[i], expectedSpanKnotsCurve1[i]);
    }

    // Trace: Evaluate the curve at each span knot value
    std::cout << "Trace: Evaluate the curve at each span knot value" << std::endl;
    for (auto span : spanKnots) {
        res = curveView.evaluate(span);
        std::cout << "Evaluated curve at " << span << " : " << res.x << ", " << res.y << ", "
                  << res.z << std::endl;
    }
}

TEST_F(TestNUBSCurve, TestNUBSCurveToStrand) {
    // Test conversion of a NUBS curve object to a strand object.
    //
    // Starts from the strandNUBSCurve object created in the fixture.
    // Get a Bifrost strand object from the NUBS curve object.
    // Check validity of strand object.
    // Check that the strand object is not a NUBS curve anymore.

    // Sample the NUBS curve to create a new strand object
    auto evaluatedStrand = Bifrost::createObject();

    ASSERT_TRUE(Examples::GeoSDK::buildStrandFromNUBSCurve(*strandNUBSCurve, 3, *evaluatedStrand))
        << "Invalid NUBS Curve. Failed to sample NUBS curve";

    // Validate the strand...
    Bifrost::Geometry::StrandValidator strandValidator;
    ASSERT_TRUE(strandValidator.validate(*evaluatedStrand)) << "Invalid strand structure";

    // It is not a NUBS curve anymore
    ASSERT_FALSE(Examples::GeoSDK::isNUBSCurveValid(*evaluatedStrand))
        << "Cannot be a NUBS curve anymore...";

    auto nbStrands =
        Bifrost::Geometry::getElementCount(*evaluatedStrand, Bifrost::Geometry::sStrandComp);
    auto newStrandPoints = Bifrost::Geometry::getDataGeoPropValues<Bifrost::Math::float3>(
        *evaluatedStrand, Bifrost::Geometry::sPointPosition);
    auto newStrandOffsets = Bifrost::Geometry::getDataGeoPropValues<Index>(
        *evaluatedStrand, Bifrost::Geometry::sStrandOffset);

    ASSERT_TRUE(newStrandPoints) << "Failed to get strand points from sampled NUBS curve";
    ASSERT_TRUE(newStrandOffsets) << "Failed to get strand offsets from sampled NUBS curve";
    ASSERT_FALSE(newStrandOffsets->empty()) << "Strand offset cannot be empty";
    ASSERT_EQ(nbStrands, newStrandOffsets->size() - 1);
    ASSERT_EQ(newStrandOffsets->at(nbStrands), newStrandPoints->size());
}

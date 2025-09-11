//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file SimpleNUBSCurveView.h
/// \brief Simple NUBS Curve View.

#ifndef SIMPLE_NUBS_CURVE_VIEW_H
#define SIMPLE_NUBS_CURVE_VIEW_H

#include "SimpleNUBSCurveExport.h"

#include <Bifrost/Geometry/GeoPropertyKey.h>
#include <Bifrost/Math/Types.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/Array.h>

namespace Examples {
namespace GeoSDK {

class SIMPLE_NUBS_CURVE_DECL NUBSCurveView {
    /// \brief  Class to access the NUBS Bifrost strand object underlying data.
    /// \note   This class is for read-only access only.
    /// \note   It is assumed that there is at least one curve in the object.
public:
    NUBSCurveView()                             = delete;
    NUBSCurveView(NUBSCurveView const&)         = delete;
    NUBSCurveView(NUBSCurveView&&)              = delete;
    NUBSCurveView(Bifrost::Object&& nubsCurves) = delete;
    explicit NUBSCurveView(Bifrost::Object const& nubsCurves);

public:
    /// \brief Get the number of curves in the object.
    /// \return Number of curves.
    Amino::uint_t getCurveCount() const;

    /// \brief Set the current curve to be evaluated
    /// \param curveIndex Index of the curve to evaluate.
    /// \return True if the curve index is for an existing curve.
    bool setCurveIndex(Amino::uint_t curveIndex);

    /// \brief Clamp t with respect to the current curve's parametric domain.
    /// \param t Parameter to clamp.
    /// \return Clamped parameter
    float clamp(float t) const;

    /// \brief Get the current curve's degree.
    /// \return Degree of the current curve.
    Amino::uint_t getDegree() const;

    /// \brief Get the number of spans in the current curve.
    /// \return Number of spans.
    Amino::uint_t getSpanCount() const;

    /// \brief Get start knot value of current curve's parametric domain.
    /// \return Start knot value.
    float getStartKnotValue() const;

    /// \brief Get end knot value of current curve's parametric domain.
    /// \return End knot value.
    float getEndKnotValue() const;

    /// \brief Get the distinct knots values of the current curve.
    /// \return Return array of distinct knots values.
    Amino::Array<float> getSpanKnots() const;

    /// \brief  Get samples per span. Span knots are always included.
    /// \param nbSamplesPerSpan Number of samples per span. 0 implies only span knots.
    /// \return Array of samples per span.
    ///         Ex.: for span knots [0.0, 1.0, 2.0] and nbSamplesPerSpan = 2 you get
    ///         [0.0, 1/3, 2/3, 1.0, 4/3, 5/3, 2.0]
    Amino::Array<float> getSamplesPerSpan(Amino::uint_t nbSamplesPerSpan) const;

    /// \brief Evaluate at a given value - assumed to be clamped correctly
    /// \param t Parameter to evaluate at.
    /// \return Point on curve at parameter t.
    Bifrost::Math::float3 evaluate(float t) const;

private:
    using BasisValues = Amino::Array<float>;

    Amino::uint_t getLowKnotIndex() const;
    Amino::uint_t getHighKnotIndex() const;

    BasisValues   basisValues(Amino::uint_t i, float t) const;
    Amino::uint_t findSpan(float t) const;

private:
    /// \brief Data structure to hold information about a curve.
    ///
    /// The CVs are defined on the interval [startCVIndex, endCVIndex).
    /// The knots are defined on the interval [startKnotIndex, endKnotIndex).
    ///
    /// \note This is a mutable data structure that is updated when the curve index is changed.
    struct NUBSCurveData {
        Amino::uint_t currentCurveIndex; ///< Index of the current curve.
        Amino::uint_t degree;            ///< Degree of the current curve.
        Amino::uint_t startCVIndex;      ///< Index of the first CV of the current curve.
        Amino::uint_t endCVIndex;        ///< Index of the last CV of the current curve.
        Amino::uint_t startKnotIndex;    ///< Index of the first knot of the current curve.
        Amino::uint_t endKnotIndex;      ///< Index of the last knot of the current curve.
    };

    /// \brief Number of curves in the object.
    Amino::uint_t m_nbCurves;
    /// \brief Access to the CVs (strand point positions).
    Amino::Array<Bifrost::Math::float3> const& m_strandPoints;
    /// \brief Access to the CVs offsets (strand offsets).
    Amino::Array<Bifrost::Geometry::Index> const& m_strandOffsets;
    /// \brief Access to the degrees (one per curve=strand).
    Amino::Array<Amino::uint_t> const& m_degrees;
    /// \brief Access to the knot values for all curves=strands.
    Amino::Array<float> const& m_knots;
    /// \brief Access to the knot offsets (one per curve=strand).
    Amino::Array<Bifrost::Geometry::Index> const& m_knotOffsets;

    /// \brief Data structure that holds information about the current curve.
    NUBSCurveData m_curveData;
};

} // namespace GeoSDK
} // namespace Examples

//
// Inline implementations
//

inline Amino::uint_t Examples::GeoSDK::NUBSCurveView::getCurveCount() const { return m_nbCurves; }

inline Amino::uint_t Examples::GeoSDK::NUBSCurveView::getDegree() const {
    return m_curveData.degree;
}

inline float Examples::GeoSDK::NUBSCurveView::getStartKnotValue() const {
    return m_knots[getLowKnotIndex()];
}

inline float Examples::GeoSDK::NUBSCurveView::getEndKnotValue() const {
    return m_knots[getHighKnotIndex()];
}

#endif // SIMPLE_NUBS_CURVE_VIEW_H

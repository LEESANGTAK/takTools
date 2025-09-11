//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//

#include <Examples/GeoSDK/SimpleNUBSCurveView.h>

#include <Examples/GeoSDK/SimpleNUBSCurveKey.h>

#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Geometry/GeometryTypes.h>

using Index = Bifrost::Geometry::Index;
static_assert(std::is_same<Index, Amino::uint_t>::value, "Index type mismatch");

// NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init)
Examples::GeoSDK::NUBSCurveView::NUBSCurveView(Bifrost::Object const& nubsCurves)
    : m_nbCurves(Bifrost::Geometry::getElementCount(nubsCurves, Bifrost::Geometry::sStrandComp)),
      m_strandPoints(*Bifrost::Geometry::getDataGeoPropValues<Bifrost::Math::float3>(
          nubsCurves, Bifrost::Geometry::sPointPosition)),
      m_strandOffsets(*Bifrost::Geometry::getDataGeoPropValues<Index>(
          nubsCurves, Bifrost::Geometry::sStrandOffset)),
      m_degrees(*Bifrost::Geometry::getDataGeoPropValues<Amino::uint_t>(nubsCurves, sStrandDegree)),
      m_knots(*Bifrost::Geometry::getDataGeoPropValues<float>(nubsCurves, sKnotValue)),
      m_knotOffsets(
          *Bifrost::Geometry::getDataGeoPropValues<Index>(nubsCurves, sStrandKnotOffset)) {
    // Initialize the curve data to the first curve.
    // Note: it is assumed that there is at least one curve.
    assert(m_nbCurves > 0);
    m_curveData.currentCurveIndex = 0;
    m_curveData.degree            = m_degrees[0];
    m_curveData.startCVIndex      = m_strandOffsets[0];
    m_curveData.endCVIndex        = m_strandOffsets[1];
    m_curveData.startKnotIndex    = m_knotOffsets[0];
    m_curveData.endKnotIndex      = m_knotOffsets[1];
}

bool Examples::GeoSDK::NUBSCurveView::setCurveIndex(Amino::uint_t curveIndex) {
    // Check that the curve index is valid
    if (m_nbCurves == 0 || curveIndex > m_nbCurves - 1) {
        return false;
    }

    // Is the curve index changed?  Keep existing curve data if not.
    if (curveIndex != m_curveData.currentCurveIndex) {
        m_curveData.currentCurveIndex = curveIndex;
        m_curveData.degree            = m_degrees[curveIndex];
        m_curveData.startCVIndex      = m_strandOffsets[curveIndex];
        m_curveData.endCVIndex        = m_strandOffsets[curveIndex + 1];
        m_curveData.startKnotIndex    = m_knotOffsets[curveIndex];
        m_curveData.endKnotIndex      = m_knotOffsets[curveIndex + 1];
    }

    return true;
}

Amino::uint_t Examples::GeoSDK::NUBSCurveView::getSpanCount() const {
    Amino::uint_t nbSpans = 0;

    for (size_t i = getLowKnotIndex(); i < getHighKnotIndex(); ++i) {
        if (m_knots[i] > m_knots[i + 1] || m_knots[i] < m_knots[i + 1]) {
            ++nbSpans;
        }
    }
    return nbSpans;
}

float Examples::GeoSDK::NUBSCurveView::clamp(float t) const {
    float firstKnot = getStartKnotValue();
    float lastKnot  = getEndKnotValue();
    if (t < firstKnot) {
        return firstKnot;
    } else if (t > lastKnot) {
        return lastKnot;
    } else {
        return t;
    }
}

Amino::Array<float> Examples::GeoSDK::NUBSCurveView::getSpanKnots() const {
    Amino::Array<float> spanKnots;
    auto const          startIndex = getLowKnotIndex();
    spanKnots.push_back(m_knots[startIndex]);

    for (auto i = startIndex; i < getHighKnotIndex(); ++i) {
        if (m_knots[i] > m_knots[i + 1] || m_knots[i] < m_knots[i + 1]) {
            spanKnots.push_back(m_knots[i + 1]);
        }
    }
    return spanKnots;
}

Amino::Array<float> Examples::GeoSDK::NUBSCurveView::getSamplesPerSpan(
    Amino::uint_t nbSamplesPerSpan) const {
    Amino::Array<float> samples;
    auto const          spanKnots = getSpanKnots();
    auto const          lastIndex = spanKnots.size() - 1;
    for (size_t i = 0; i < lastIndex; ++i) {
        auto t0 = spanKnots[i];
        samples.push_back(t0);
        if (nbSamplesPerSpan > 0) {
            auto const t1 = spanKnots[i + 1];
            auto const dt = (t1 - t0) / static_cast<float>(nbSamplesPerSpan + 1);
            for (size_t j = 1; j <= nbSamplesPerSpan; ++j) {
                samples.push_back(t0 + static_cast<float>(j) * dt);
            }
        }
    }
    samples.push_back(spanKnots[lastIndex]);

    return samples;
}

Bifrost::Math::float3 Examples::GeoSDK::NUBSCurveView::evaluate(float t) const {
    Amino::uint_t span = findSpan(t); // We could cache span in mutable data structure.
    BasisValues   N    = basisValues(span, t);

    Bifrost::Math::float3 result{0.0F, 0.0F, 0.0F};
    for (size_t i = 0; i <= m_curveData.degree; ++i) {
        float const& basis = N[i];
        auto const   cvIndex =
            m_curveData.startCVIndex + (span - m_curveData.startKnotIndex) - m_curveData.degree + i;
        Bifrost::Math::float3 const& controlPoint = m_strandPoints[cvIndex];
        result.x += basis * controlPoint.x;
        result.y += basis * controlPoint.y;
        result.z += basis * controlPoint.z;
    }

    return result;
}

//
// Private - NUBS evaluation
//

Amino::uint_t Examples::GeoSDK::NUBSCurveView::getLowKnotIndex() const {
    return m_curveData.startKnotIndex + m_curveData.degree;
}

Amino::uint_t Examples::GeoSDK::NUBSCurveView::getHighKnotIndex() const {
    return m_curveData.endKnotIndex - m_curveData.degree - 1;
}

// The following NUBS evaluation functions: findSpan, basisValues, and evaluate are adaptations
// from the pseudo-code found in  Piegl & Tiller, The NURBS Book, Springer, 1995, p. 68 - 78.
Amino::uint_t Examples::GeoSDK::NUBSCurveView::findSpan(float t) const {
    Amino::uint_t high = getHighKnotIndex();
    assert(high > 0);
    Amino::uint_t low = getLowKnotIndex();
    assert(low <= high);

    if (t >= m_knots[high]) {
        return high - 1;
    }

    if (t <= m_knots[low]) {
        return low;
    }

    Amino::uint_t mid = (low + high) / 2;

    while (t < m_knots[mid] || t >= m_knots[mid + 1]) {
        if (t < m_knots[mid]) {
            high = mid;
        } else {
            low = mid;
        }

        mid = (low + high) / 2;
    }

    return mid;
}

Examples::GeoSDK::NUBSCurveView::BasisValues Examples::GeoSDK::NUBSCurveView::basisValues(
    Amino::uint_t i, float t) const {
    BasisValues N(m_curveData.degree + 1, 0.0F);
    N[0] = 1.0F;

    // Note that left[0] and right[0] are not used.
    // This is to accommodate the indexing below
    Amino::Array<float> left(m_curveData.degree + 1, 0.0F);
    Amino::Array<float> right(m_curveData.degree + 1, 0.0F);

    for (Amino::uint_t j = 1; j <= m_curveData.degree; ++j) {
        left[j]  = t - m_knots[i + 1 - j];
        right[j] = m_knots[i + j] - t;

        float saved = 0.0F;
        for (Amino::uint_t r = 0; r < j; ++r) {
            float tmp = N[r] / (right[r + 1] + left[j - r]);
            N[r]      = saved + right[r + 1] * tmp;
            saved     = left[j - r] * tmp;
        }
        N[j] = saved;
    }

    return N;
}

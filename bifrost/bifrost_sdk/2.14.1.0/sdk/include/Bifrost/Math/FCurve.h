//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file  FCurve.h
///
/// \brief Bifrost standard FCurve

#ifndef BIFROST_MATH_FCURVE_H
#define BIFROST_MATH_FCURVE_H

#include <Bifrost/Math/MathExport.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Core/internal/ConfigMacros.h>

#include <Amino/Cpp/Annotate.h>
#include <Amino/Cpp/ClassDeclare.h>

namespace Amino {
class FCurveSerializer;
}

/// \brief Use a define, otherwise clang-format gets confused.
/// \warning : Ignoring namespace is an internal feature, should not be used by
/// external code.
#define BIFROST_IGNORE_NAMESPACE AMINO_ANNOTATE("Amino::Namespace ignore")
namespace Bifrost BIFROST_IGNORE_NAMESPACE {
#undef BIFROST_IGNORE_NAMESPACE

namespace Math {

//==============================================================================
// CLASS FCurve
//==============================================================================

/// \brief FCurve User Class
class AMINO_ANNOTATE("Amino::Class") BIFROST_MATH_SHARED_DECL FCurve {
    /// \brief FCurve Serializer friend
    friend class Amino::FCurveSerializer;

public:
    /// \brief Constructor
    ///
    /// param [in] createDefaultValue True will create a default curve
    ///            y=x; numPoints() > 0.
    ///            False will evaluate as y=x; numPoints() == 0.
    explicit FCurve(bool createDefaultValue = true);

    /// \brief Destructor
    ~FCurve();

    /// \brief Copy constructor
    ///
    /// \param other The FCurve to copy

    FCurve(FCurve const& other);

    /// \brief Reset to a default FCurve
    ///
    /// The default FCurve is y=x.
    ///
    /// \return True if reset is successful, else false.
    bool defaultValue();

    /// \brief Support function to evaluate a cubic Bezier curve segment.
    ///
    /// \param x0 The x coordinate of 0th Bezier control point
    /// \param y0 The y coordinate of 0th Bezier control point
    /// \param x1 The x coordinate of 1st Bezier control point
    /// \param y1 The y coordinate of 1st Bezier control point
    /// \param x2 The x coordinate of 2nd Bezier control point
    /// \param y2 The y coordinate of 2nd Bezier control point
    /// \param x3 The x coordinate of 3rd Bezier control point
    /// \param y3 The y coordinate of 3rd Bezier control point
    /// \param x  The x coordinate at which to evaluate the curve segment
    ///
    /// \return The value of the Bezier curve at x, given the 4 Bezier control
    /// points
    static double evalBezier(
        double x0,
        double y0,
        double x1,
        double y1,
        double x2,
        double y2,
        double x3,
        double y3,
        double x);

    /// \brief Number of points in the FCurve
    ///
    /// \return The number of points in this FCurve
    int numPoints() const;

    /// \brief Evaluate the FCurve at the given x value.
    ///
    /// \param [in] x The x value at which the FCurve will be evaluated
    ///
    /// \return The value of the FCurve at x.
    double evalFCurve(double x) const;

private:
    /// \brief Struct for previous, current, and next point for a Bezier curve
    ///
    /// In general, a Bezier segment Bi is defined by the control points
    /// Pi0, Pi1, Pi2, and Pi3, such that the the segment Bi passes through
    /// Pi0 and Pi3, and has a tangent of Pi1-Pi0 at Pi0, and Pi2-Pi3 at Pi3.
    ///
    /// For the ith control point, the incoming tangent is defined by the
    /// vector from (xp,yp) to (x,y), that is:
    ///    (xp,yp) = P(i-1)2
    ///    (x,y) = P(i-1)3 = Pi0
    ///
    /// Similarly, the outgoing tangent is defined by the vector from
    /// (xn,pn) to (x,y), that is:
    ///
    ///    (xn,yn) = Pi1
    ///
    struct BezierControlPoints {
        double xp;
        double yp;
        double x;
        double y;
        double xn;
        double yn;
    };

    /// Struct for one point
    struct BezierSegmentPoint {
        bool                locked;
        int                 interpolation;
        BezierControlPoints coords;
    };
    using FCurvePoints = Amino::Array<Math::FCurve::BezierSegmentPoint>;

    /// Curve extrapolation mode supported for pre/post extrapolation
    /// Note: this enum values are use to do serialization/deserialization
    enum class ExtrapolationMode {
        Constant = 0, ///< Flat line.
        Linear   = 1, ///< continue the linear trend in linear interpolation
        Cycle    = 2, ///< cycle the curve. (abc -> abc abc abc...)
        RelativeRepeat = 3, ///< offsets the value of the first point to the
                            ///< value of the last point each cycle.
        Oscillate = 4 ///< mirror the curve on X, and then cycle the mirrored
                      ///< the result. (abc -> abc cba abc cba...)
    };

    AMINO_INTERNAL_WARNING_PUSH
    AMINO_INTERNAL_WARNING_DISABLE_MSC(4251)
    FCurvePoints      m_points;
    ExtrapolationMode m_preExtrapolation  = ExtrapolationMode::Constant;
    ExtrapolationMode m_postExtrapolation = ExtrapolationMode::Constant;
    AMINO_INTERNAL_WARNING_POP
};

} // namespace Math
} // namespace BIFROST_IGNORE_NAMESPACE

/// \brief Macro for generating the getDefault entry point declaration related
/// to a given opaque type, defined in ClassDeclare.h
AMINO_DECLARE_DEFAULT_CLASS(BIFROST_MATH_SHARED_DECL, Bifrost::Math::FCurve);

#endif

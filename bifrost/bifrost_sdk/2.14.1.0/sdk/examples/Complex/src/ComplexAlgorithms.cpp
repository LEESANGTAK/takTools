//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "ComplexAlgorithms.h"

#include <complex>

namespace Algorithms {

std::complex<float> polar(float magnitude, float phase /* rads */) {
    auto real = magnitude * std::cos(phase);
    auto imag = magnitude * std::sin(phase);
    return std::complex<float>(real, imag);
}

} // namespace Algorithms

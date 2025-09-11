//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "Complex.h"

#include <complex>

#include "ComplexAlgorithms.h"

namespace Examples {
namespace SDK {
void polar(float magnitude, float phase /* rads */, Examples::SDK::Complex& polar) {
    auto c = Algorithms::polar(magnitude, phase);
    polar.imaginary = c.imag();
    polar.real = c.real();
}
}
}

namespace Core {
namespace Math {

void log_base_e(const Examples::SDK::Complex& value,
                Examples::SDK::Complex&       logarithm) {
    auto log  = std::log(std::complex<float>(value.real, value.imaginary));
    logarithm = {log.real(), log.imag()};
}

} // namespace Math
} // namespace Core

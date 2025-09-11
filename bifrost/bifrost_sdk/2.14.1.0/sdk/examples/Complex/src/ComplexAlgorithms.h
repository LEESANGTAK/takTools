//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file This example adds a method to the Complex struct
/// node operator. It is built as a separate standalone library to
/// have a separate support shared lib to link with ..."

#pragma once

#include <complex>
#include "ComplexAlgorithmsExport.h"

namespace Algorithms {

COMPLEX_ALGORITHMS_DECL std::complex<float> polar(float magnitude,
                                                  float phase /* rads */);

} // namespace Algorithms

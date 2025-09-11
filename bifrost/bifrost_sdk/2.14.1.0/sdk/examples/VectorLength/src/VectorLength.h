//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef VECTOR_LENGTH_H
#define VECTOR_LENGTH_H

#include "VectorLengthExport.h"

#include <Bifrost/Math/Types.h>

namespace Examples {
namespace SDK {

//==============================================================================
// ENUM VectorLengthMode
//==============================================================================

enum class AMINO_ANNOTATE("Amino::Enum") VectorLengthMode {
    Euclidean,
    EuclideanSquared,
    Max,
    Manhattan
};

//==============================================================================
// FREE FUNCTIONS
//==============================================================================

VECTOR_LENGTH_DECL float vector_length(Bifrost::Math::float3 const& in,
                                       VectorLengthMode             mode)
    AMINO_ANNOTATE("Amino::Node");

} // namespace SDK
} // namespace Examples

#endif // VECTOR_LENGTH_H

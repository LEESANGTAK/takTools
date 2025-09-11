//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+
#include "VectorLength.h"

#include <algorithm>
#include <cassert>
#include <cmath>

namespace {
float euclidean2_length(Bifrost::Math::float3 const& in) {
    return in.x * in.x + in.y * in.y + in.z * in.z;
}
float euclidean_length(Bifrost::Math::float3 const& in) {
    return std::sqrt(euclidean2_length(in));
}
float max_length(Bifrost::Math::float3 const& in) {
    return std::max(std::abs(in.x), std::max(std::abs(in.y), std::abs(in.z)));
}
float manhattan_length(Bifrost::Math::float3 const& in) {
    return std::abs(in.x) + std::abs(in.y) + std::abs(in.z);
}
} // namespace

namespace Examples {
namespace SDK {

float vector_length(Bifrost::Math::float3 const& in, VectorLengthMode mode) {
    switch (mode) {
        case VectorLengthMode::Euclidean: return euclidean_length(in);
        case VectorLengthMode::EuclideanSquared: return euclidean2_length(in);
        case VectorLengthMode::Max: return max_length(in);
        case VectorLengthMode::Manhattan: return manhattan_length(in);
    }
    assert((false) && "All cases are covered");
    return euclidean_length(in);
}

} // namespace SDK
} // namespace Examples

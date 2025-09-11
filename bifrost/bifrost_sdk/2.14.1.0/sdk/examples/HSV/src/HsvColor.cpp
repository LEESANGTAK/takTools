//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "HsvColor.h"

#include <algorithm>

namespace {

// RGBType is assumed to be in the range [0-1]
// Hue : [0...360]
// Saturation [0..1]
// Value : [0..1]

// https://en.wikipedia.org/wiki/HSL_and_HSV#Hue_and_chroma
// Hue : The "attribute of a visual sensation according to which an area
// appears to be similar to one of the perceived colors: red, yellow, green,
// and blue, or to a combination of two of them".

// Value (brightness): The "attribute of a visual sensation according to which
// an area appears to emit more or less light".

// Saturation : The "colorfulness
// of a stimulus relative to its own brightness".

template <typename Vec3Type>
Vec3Type rgb_to_hsv(const Vec3Type& rgb) {
    using MemberType = decltype(rgb.x);

    // Extract the Red, Green, Blue members
    const auto r = rgb.x;
    const auto g = rgb.y;
    const auto b = rgb.z;

    const auto rgb_max = std::max(r, std::max(g, b));
    const auto rgb_min = std::min(r, std::min(g, b));
    if (rgb_min < 0) {
        return {0, 0, 0};
    }

    const auto delta = rgb_max - rgb_min;
    auto       value = rgb_max;

    MemberType hue = 0, saturation = 0;

    if (rgb_max > 0) {
        saturation = (delta / rgb_max);
    }

    if (delta > 0) {
        if (r >= rgb_max) {
            hue = (g - b) / delta;
        } else if (g >= rgb_max) {
            hue = MemberType{2} + (b - r) / delta;
        } else {
            hue = MemberType{4} + (r - g) / delta;
        }
    }
    hue *= static_cast<MemberType>(60.0F);
    if (hue < static_cast<MemberType>(0.0F)) {
        hue += static_cast<MemberType>(360.0F);
    }

    return {hue, saturation, value};
}

} // namespace

namespace Examples {
namespace SDK {

void RGB_to_HSV(Bifrost::Math::float3 const& rgb, Bifrost::Math::float3& hsv) {
    hsv = rgb_to_hsv(rgb);
}
void RGB_to_HSV(Bifrost::Math::float4 const& rgb, Bifrost::Math::float3& hsv) {
    hsv = rgb_to_hsv(Bifrost::Math::float3{rgb.x, rgb.y, rgb.z}); // drop alpha
}
void RGB_to_HSV(Bifrost::Math::double3 const& rgb,
                Bifrost::Math::double3&       hsv) {
    hsv = rgb_to_hsv(rgb);
}
void RGB_to_HSV(Bifrost::Math::double4 const& rgb,
                Bifrost::Math::double3&       hsv) {
    hsv = rgb_to_hsv(Bifrost::Math::double3{rgb.x, rgb.y, rgb.z}); // drop alpha
}

} // namespace SDK
} // namespace Examples

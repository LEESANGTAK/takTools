//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+
#ifndef EXECUTOR_CUSTOM_OBJECT_H
#define EXECUTOR_CUSTOM_OBJECT_H

// For the macros used to expose types/functions to Amino
#include <Amino/Cpp/Annotate.h>
#include <Bifrost/Math/Types.h>

namespace Examples {
namespace SDK {

/// \brief Define a structure representing a BoundingBox.
///
/// The structure has the name "BoundingBox" and is defined in the "Examples::SDK"
/// namespace. Its fully qualified name is therefore "Examples::SDK::BoundingBox".
/// This fully qualified name is therefore a unique identifier for our "BoundingBox"
/// struct.
struct AMINO_ANNOTATE("Amino::Struct") BoundingBox {
    Bifrost::Math::float3 min;
    Bifrost::Math::float3 max;
};

} // namespace SDK
} // namespace Examples

#endif // EXECUTOR_CUSTOM_OBJECT_H

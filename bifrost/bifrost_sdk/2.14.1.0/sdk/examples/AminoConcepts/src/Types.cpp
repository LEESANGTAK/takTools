//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "Types.h"

#include <Amino/Cpp/ClassDefine.h>

/// \brief Defines the entry point that will create the default value of type
/// `Examples::SDK::MyClass` and return it to Amino. By default, the default
/// value of a custom class will be the default constructed value (calling the
/// default constructor).
AMINO_DEFINE_DEFAULT_CLASS(Examples::SDK::MyClass);

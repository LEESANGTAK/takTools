//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They
// may not be disclosed to, copied  or used by any third party without the
// prior written consent of Autodesk, Inc.
// =============================================================================
//+

#include "ObjWriterOps.h"
#include <Examples/GeoSDK/ObjWriter.h>

bool Examples::GeoSDK::WriteObj(Bifrost::Object const &mesh, Amino::String const &filename) {
    return writeOBJ(mesh, filename.c_str());
}

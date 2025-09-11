//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file ObjWriter .h
/// \brief Simple functions to read and write Simple Obj files.

#ifndef OBJ_WRITER_H
#define OBJ_WRITER_H

#include <Bifrost/Object/ObjectFwd.h>
#include <string>
#include "ObjWriterExport.h"

namespace Examples {
namespace GeoSDK {
OBJ_WRITER_DECL bool writeOBJ(const Bifrost::Object& mesh, const std::string& filename);
} // namespace GeoSDK
} // namespace Examples

#endif // OBJ_WRITER_H

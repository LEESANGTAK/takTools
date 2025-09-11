//-
//*****************************************************************************
// Copyright (c) 2024 Autodesk, Inc.
// All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

//
/// \file DebugDump.h
///
/// \brief bifrost object serialization util functions.
///

#ifndef BIFROST_GEOMETRY_DEBUG_DUMP_H
#define BIFROST_GEOMETRY_DEBUG_DUMP_H

#include <Bifrost/Geometry/GeometryExport.h>

#include <Bifrost/Object/Object.h>

namespace Bifrost {
namespace Geometry {
namespace Internal {
struct BIFROST_GEOMETRY_DECL DebugDumpInterface {
    virtual ~DebugDumpInterface();
    virtual void write(const char* data, size_t size) = 0;
};
BIFROST_GEOMETRY_DECL void debugDumpToStream(DebugDumpInterface& io, const Bifrost::Object& object, size_t sampleSize);
} // namespace Internal


/// \defgroup GeoPrimitiveUtilities Utility functions
/// @{
/// @brief Dump this object as a string to the given stream. Useful for debugging.
/// @tparam OStream Generic output stream type. Supports write(const char*, size_t).
/// @param os Output stream to which the object is dumped.
/// @param object The object to dump.
/// @param sampleSize Maximum number of elements in array data to dump out. Default is 10.
template <typename OStream>
inline void debugDump(OStream& os, Bifrost::Object const& object, size_t sampleSize = 10) {
    struct DebugDumpStream : public Internal::DebugDumpInterface {
        explicit DebugDumpStream(OStream& os_) : m_os(os_) {}
        void     write(const char* data, size_t size) override { m_os.write(data, size); }
        OStream& m_os;
    };
    DebugDumpStream vos{os};
    Internal::debugDumpToStream(vos, object, sampleSize);
}
/// @}

} // namespace Geometry
} // namespace Bifrost

#endif // BIFROST_DEBUG_DUMP_H

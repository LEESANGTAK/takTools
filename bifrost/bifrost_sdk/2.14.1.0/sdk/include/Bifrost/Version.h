//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef BIFROST_VERSION_H_
#define BIFROST_VERSION_H_

#include <cstdint>
#include <string>

/// String representation of the complete bifrost version.
#define _bifrost_version_ "2.14.1.0"

/// Arch number part of Bifrost version.
#define _bifrost_arch_ 2

/// Major number part of Bifrost version.
#define _bifrost_major_ 14

/// Minor number part of Bifrost version.
#define _bifrost_minor_ 1

/// Patch number part of Bifrost version.
#define _bifrost_patch_ 0

static_assert((_bifrost_arch_ > 0 && _bifrost_arch_ < 100),
              "_bifrost_arch_ out of range");
static_assert((_bifrost_major_ >= 0 && _bifrost_major_ < 100),
              "_bifrost_major_ out of range");
static_assert((_bifrost_minor_ >= 0 && _bifrost_minor_ < 100),
              "_bifrost_minor_ out of range");
static_assert((_bifrost_patch_ >= 0 && _bifrost_patch_ < 1000),
              "_bifrost_patch_ out of range");

namespace Bifrost {
//----------------------------------------------------------------------------
//
namespace Version {

//----------------------------------------------------------------------------
//
/// \brief Returns the Arch number part of Bifrost version.
static inline constexpr unsigned getArchNumber() {
    return static_cast<unsigned>(_bifrost_arch_);
}

//----------------------------------------------------------------------------
//
/// \brief Returns the Major number part of Bifrost version.
static inline constexpr unsigned getMajorNumber() {
    return static_cast<unsigned>(_bifrost_major_);
}

//----------------------------------------------------------------------------
//
/// \brief Returns the Minor number part of Bifrost version.
static inline constexpr unsigned getMinorNumber() {
    return static_cast<unsigned>(_bifrost_minor_);
}

//----------------------------------------------------------------------------
//
/// \brief Returns the Patch number part of Bifrost version.
static inline constexpr unsigned getPatchNumber() {
    return static_cast<unsigned>(_bifrost_patch_);
}

//----------------------------------------------------------------------------
//
/// \brief Returns the complete Bifrost version as a std::string.
static inline std::string getAsString() {
    return std::string(_bifrost_version_);
}

//-----------------------------------------------------------------------------
//
/// \brief Returns the complete Bifrost version as a single 64-bit unsigned.
///
/// \details This is useful for comparing two Bifrost version numbers.
static inline constexpr uint64_t getAsNumber() {
    return (getArchNumber() * 100 * 100 * 1000 + getMajorNumber() * 100 * 1000
            + getMinorNumber() * 1000 + getPatchNumber());
}

} // namespace Version
} // namespace Bifrost

#endif // BIFROST_VERSION_H_

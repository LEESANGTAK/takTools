//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include <Amino/Core/RuntimeMessageCategory.h>
#include <Amino/Core/String.h>

#include <Amino/Core/internal/ConfigMacros.h>

namespace Amino {

//==============================================================================
// DEPRECATED
//==============================================================================

class RuntimeMessage {
public:
    AMINO_INTERNAL_DEPRECATED(
        "RuntimeMessage is deprecated, use logging in RuntimeServices instead.")
    RuntimeMessage() = default;

    AMINO_INTERNAL_DEPRECATED(
        "RuntimeMessage is deprecated, use logging in RuntimeServices instead.")
    RuntimeMessage(RuntimeMessageCategory category, String message)
        : m_message{std::move(message)}, m_category{category} {}

    AMINO_INTERNAL_DEPRECATED(
        "RuntimeMessage is deprecated, use logging in RuntimeServices instead.")
    RuntimeMessage(const RuntimeMessage&) = default;

    AMINO_INTERNAL_DEPRECATED(
        "RuntimeMessage is deprecated, use logging in RuntimeServices instead.")
    RuntimeMessage(RuntimeMessage&&) noexcept = default;

    AMINO_INTERNAL_DEPRECATED(
        "RuntimeMessage is deprecated, use logging in RuntimeServices instead.")
    ~RuntimeMessage() = default;

    AMINO_INTERNAL_DEPRECATED(
        "RuntimeMessage is deprecated, use logging in RuntimeServices instead.")
    RuntimeMessage& operator=(const RuntimeMessage&) = default;

    AMINO_INTERNAL_DEPRECATED(
        "RuntimeMessage is deprecated, use logging in RuntimeServices instead.")
    RuntimeMessage& operator=(RuntimeMessage&&) noexcept = default;

    AMINO_INTERNAL_DEPRECATED(
        "RuntimeMessage is deprecated, use logging in RuntimeServices instead.")
    bool isNull() const { return m_message.empty(); }

    AMINO_INTERNAL_DEPRECATED(
        "RuntimeMessage is deprecated, use logging in RuntimeServices instead.")
    explicit operator bool() const { return !isNull(); }

    String                 m_message;
    RuntimeMessageCategory m_category;
};

} // namespace Amino

//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef EXECUTOR_BASICS_TRANSLATION_H
#define EXECUTOR_BASICS_TRANSLATION_H

#include <BifrostGraph/Executor/TypeTranslation.h>

/// \brief ExecutorBasics TypeTranslation table.
///
/// This class manages the translation of port values between the ExecutorBasics application and
/// Amino.
///
class ExecutorBasicsTranslation : public BifrostGraph::Executor::TypeTranslation {
public:
    ExecutorBasicsTranslation();
    ~ExecutorBasicsTranslation() override = default;

    void deleteThis() noexcept override;

    void getSupportedTypeNames(StringArray& out_names) const noexcept override;

    bool convertValueFromHost(Amino::Type const& type,
                              Amino::Any&        outValue,
                              ValueData const*   valueData) const noexcept override;

    bool convertValueToHost(Amino::Any const& inValue,
                            ValueData*        valueData) const noexcept override;
};

#endif

//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef EXECUTOR_CUSTOM_OBJECT_VALUE_DATA_H
#define EXECUTOR_CUSTOM_OBJECT_VALUE_DATA_H

#include "ExecutorCustomObject.h"
#include <Bifrost/Math/Types.h>
#include <BifrostGraph/Executor/TypeTranslation.h>
#include <string>

/// \brief Specialization of Bifrost TypeTranslation::ValueData.
///
/// This class holds the data that will be passed to the Job's setInputValue and getOutputValue
/// methods, and the Job will pass it to the TypeTranslation table.
/// You can put any data you want to access inside the TypeTranslation table for a given port.
///
/// \note This example uses one TypeTranslation::ValueData to hold 2 different kinds of data
///       (Examples::SDK::BoundingBox and Bifrost::Math::float3). You can also have multiple
///       TypeTranslation::ValueData. It is your responsability to handle your
///       TypeTranslation::ValueData correctly inside your translation table.
///
/// \see See BifrostGraph::Executor::Job::setInputValue
/// \see See BifrostGraph::Executor::Job::getOutputValue
/// \see ExecutorCustomObjectTranslation::convertValueFromHost()
/// \see ExecutorCustomObjectTranslation::convertValueToHost()
class ExecutorCustomObjectValueData : public BifrostGraph::Executor::TypeTranslation::ValueData {
public:
    /// \brief Default Constructor.
    ExecutorCustomObjectValueData() noexcept = default;

    // disable copy/move constructor/operator
    ExecutorCustomObjectValueData(const ExecutorCustomObjectValueData&)            = delete;
    ExecutorCustomObjectValueData& operator=(const ExecutorCustomObjectValueData&) = delete;
    ExecutorCustomObjectValueData(ExecutorCustomObjectValueData&&)                 = delete;
    ExecutorCustomObjectValueData& operator=(ExecutorCustomObjectValueData&&)      = delete;

    ~ExecutorCustomObjectValueData() override = default;

    const Examples::SDK::BoundingBox& getBoundingBox() const noexcept { return m_boundingBox; }
    const Bifrost::Math::float3&      getFloat3() const noexcept { return m_float3; }

    void setBoundingBox(Examples::SDK::BoundingBox bb) noexcept { m_boundingBox = bb; }
    void setFloat3(Bifrost::Math::float3 f3) noexcept { m_float3 = f3; }

private:
    Examples::SDK::BoundingBox m_boundingBox{};
    Bifrost::Math::float3      m_float3{};
};

#endif // EXECUTOR_CUSTOM_OBJECT_VALUE_DATA_H

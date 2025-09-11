//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef EXECUTOR_BASICS_VALUE_DATA_H
#define EXECUTOR_BASICS_VALUE_DATA_H

#include <BifrostGraph/Executor/TypeTranslation.h>
#include <string>

/// \brief Specialization of Bifrost TypeTranslation::ValueData.
///
/// This class holds the data that will be passed to the Job's setInputValue and getOutputValue
/// methods, and the Job will pass it to the TypeTranslation table.
/// You can put any data you want to access inside the TypeTranslation table for a given port.
///
/// See BifrostGraph::Executor::Job::setInputValue
/// See BifrostGraph::Executor::Job::getOutputValue
/// \see ExecutorBasicsTranslation::convertValueFromHost()
/// \see ExecutorBasicsTranslation::convertValueToHost()
class ExecutorBasicsValueData : public BifrostGraph::Executor::TypeTranslation::ValueData {
public:
    /// \brief Default Constructor.
    ExecutorBasicsValueData() noexcept = default;

    // disable copy/move constructor/operator
    ExecutorBasicsValueData(const ExecutorBasicsValueData&)            = delete;
    ExecutorBasicsValueData& operator=(const ExecutorBasicsValueData&) = delete;
    ExecutorBasicsValueData(ExecutorBasicsValueData&&)                 = delete;
    ExecutorBasicsValueData& operator=(ExecutorBasicsValueData&&)      = delete;

    ~ExecutorBasicsValueData() override = default;

    /// \brief Retrieve the value to set for an input port, or the resulting output port value.
    /// \return The input or output port value.
    const std::string& getPortValue() const noexcept { return m_portValue; }

    /// \brief Set the desired value for an input port, or the resulting value for an output port.
    /// \param portValue The desired input port value, or the resulting output port value.
    void setPortValue(std::string portValue) noexcept { m_portValue = std::move(portValue); }

private:
    // See ExecutorBasicsTranslation::convertValueFromHost()
    // See ExecutorBasicsTranslation::convertValueToHost()
    std::string m_portValue; // The input or output port value.
};

#endif // EXECUTOR_BASICS_VALUE_DATA_H

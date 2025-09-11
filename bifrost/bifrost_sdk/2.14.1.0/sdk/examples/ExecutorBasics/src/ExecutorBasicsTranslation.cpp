//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "ExecutorBasicsExport.h"

#include "ExecutorBasicsTranslation.h"
#include "ExecutorBasicsValueData.h"

#include <Amino/Core/Any.h>
#include <BifrostGraph/Executor/Utility.h>

#include <iostream>

ExecutorBasicsTranslation::ExecutorBasicsTranslation()
    : BifrostGraph::Executor::TypeTranslation("ExecutorBasics TypeTranslation Table") {}

void ExecutorBasicsTranslation::deleteThis() noexcept { delete this; }

void ExecutorBasicsTranslation::getSupportedTypeNames(StringArray& out_names) const noexcept {
    // Define the types this TypeTranslation table supports.
    out_names.push_back("float");
    out_names.push_back("int");
}

bool ExecutorBasicsTranslation::convertValueFromHost(Amino::Type const& type,
                                                     Amino::Any&        outValue,
                                                     ValueData const*   valueData) const noexcept {
    assert(dynamic_cast<const ExecutorBasicsValueData*>(valueData));
    if (const auto* data = dynamic_cast<const ExecutorBasicsValueData*>(valueData)) {
        Amino::String typeName = BifrostGraph::Executor::Utility::getTypeName(type);
        try {
            if (typeName == "float") {
                outValue = std::stof(data->getPortValue());
            } else if (typeName == "int") {
                outValue = std::stoi(data->getPortValue());
            } else {
                // Should never go there because in getSupportedTypeNames()
                // we declare that we only support float and int.
                assert(false);
            }
            return true;
        } catch (std::exception& ex) {
            std::cerr << "Failed to convert input port value '" << data->getPortValue()
                      << "' to type " << typeName.asChar() << ": " << ex.what() << std::endl;
        } catch (...) {
            std::cerr << "Unknown error while converting input port value '" << data->getPortValue()
                      << "' to type " << typeName.asChar() << std::endl;
        }
    }
    return false;
}

bool ExecutorBasicsTranslation::convertValueToHost(Amino::Any const& inValue,
                                                   ValueData*        valueData) const noexcept {
    assert(dynamic_cast<ExecutorBasicsValueData*>(valueData));
    if (auto* data = dynamic_cast<ExecutorBasicsValueData*>(valueData)) {
        try {
            std::string strVal;
            if (inValue.type() == Amino::getTypeId<float>()) {
                auto const val = Amino::any_cast<float>(inValue);
                strVal         = std::to_string(val);
            } else if (inValue.type() == Amino::getTypeId<int>()) {
                const int val = Amino::any_cast<int>(inValue);
                strVal        = std::to_string(val);
            } else {
                // Should never go there because in getSupportedTypeNames()
                // we declare that we only support float and int.
                assert(false);
            }
            data->setPortValue(strVal);
            return true;
        } catch (...) {
            std::cerr << "Failed to convert output port value." << std::endl;
        }
    }

    return false;
}

extern "C" {
EXECUTOR_BASICS_TRANSLATION_SHARED_DECL BifrostGraph::Executor::TypeTranslation*
                                        createBifrostTypeTranslation(void);
EXECUTOR_BASICS_TRANSLATION_SHARED_DECL BifrostGraph::Executor::TypeTranslation*
                                        createBifrostTypeTranslation(void) {
                                            return new ExecutorBasicsTranslation();
}
}

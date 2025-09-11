//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "ExecutorCustomObjectExport.h"

#include "ExecutorCustomObject.h"
#include "ExecutorCustomObjectTranslation.h"
#include "ExecutorCustomObjectValueData.h"

#include <Amino/Core/Any.h>
#include <BifrostGraph/Executor/Utility.h>

ExecutorCustomObjectTranslation::ExecutorCustomObjectTranslation()
    : BifrostGraph::Executor::TypeTranslation("ExecutorCustomObject TypeTranslation Table") {}

void ExecutorCustomObjectTranslation::deleteThis() noexcept { delete this; }

void ExecutorCustomObjectTranslation::getSupportedTypeNames(StringArray& out_names) const noexcept {
    // Define the types this TypeTranslation table supports.
    out_names.push_back("Examples::SDK::BoundingBox");
    out_names.push_back("Math::float3");
}

bool ExecutorCustomObjectTranslation::convertValueFromHost(
    Amino::Type const& type, Amino::Any& outValue, ValueData const* valueData) const noexcept {
    assert(dynamic_cast<const ExecutorCustomObjectValueData*>(valueData));
    if (const auto* data = dynamic_cast<const ExecutorCustomObjectValueData*>(valueData)) {
        Amino::String typeName = BifrostGraph::Executor::Utility::getTypeName(type);
        try {
            if (typeName == "Examples::SDK::BoundingBox") {
                outValue = data->getBoundingBox();
            } else if (typeName == "Math::float3") {
                outValue = data->getFloat3();
            } else {
                // Should never go there because in getSupportedTypeNames()
                // we declare that we only support Math::float3 and Examples::SDK::BoundingBox.
                assert(false);
            }
            return true;
        } catch (...) {}
    }
    return false;
}

bool ExecutorCustomObjectTranslation::convertValueToHost(Amino::Any const& inValue,
                                                         ValueData* valueData) const noexcept {
    assert(dynamic_cast<ExecutorCustomObjectValueData*>(valueData));
    if (auto* data = dynamic_cast<ExecutorCustomObjectValueData*>(valueData)) {
        try {
            std::string strVal;
            if (inValue.type() == Amino::getTypeId<Examples::SDK::BoundingBox>()) {
                auto const bb = Amino::any_cast<Examples::SDK::BoundingBox>(inValue);
                data->setBoundingBox(bb);
            } else {
                // Should never go there because in getSupportedTypeNames()
                // we declare that we only support Math::float3 and Examples::SDK::BoundingBox.
                // The graph example only output a boundingbox so we don't need to handle
                // Math::float3 here.
                assert(false);
            }
            return true;
        } catch (...) {}
    }
    return false;
}

extern "C" {
EXECUTOR_CUSTOM_OBJECT_TRANSLATION_SHARED_DECL BifrostGraph::Executor::TypeTranslation*
                                               createBifrostTypeTranslation(void);
EXECUTOR_CUSTOM_OBJECT_TRANSLATION_SHARED_DECL BifrostGraph::Executor::TypeTranslation*
                                               createBifrostTypeTranslation(void) {
    return new ExecutorCustomObjectTranslation();
}
}

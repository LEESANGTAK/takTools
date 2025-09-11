//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+
#include "IndexSet.h"

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Cpp/ClassDefine.h>

namespace Examples {
namespace SDK {

//------------------------------------------------------------------------------
//
void add_to_index_set(IndexSet& set, Amino::long_t value) {
    set->insert(value);
}

//------------------------------------------------------------------------------
//
bool find_in_index_set(IndexSet const& set, Amino::long_t value) {
    return set->find(value) != set->end();
}

//------------------------------------------------------------------------------
//
void get_index_set_elements(IndexSet const& set, MutableArrayLong& elements) {
    elements = Amino::newMutablePtr<ArrayLong>();
    elements->reserve(set->size());
    std::copy(set->begin(), set->end(), std::back_inserter(*elements));
    // Ptr/MutablePtr managed outputs must never be null.
    assert(elements != nullptr);
}

//------------------------------------------------------------------------------
//
void union_index_set(IndexSet& first, const IndexSet& second) {
    first->insert(second->begin(), second->end());
}

void associative_union_index_set(IndexSet& first, const IndexSet& second) {
    first->insert(second->begin(), second->end());
}

//------------------------------------------------------------------------------
//
void difference_index_set(IndexSet& first, const IndexSet& second) {
    // Iterate over second indexset, removing elements from first.
    for (auto value : *second) {
        first->erase(value);
    }
}
} // namespace SDK
} // namespace Examples

/// Macro for generating the getDefault entry point definition
/// This is necessary to allow Amino graphs to create default values for
/// opaque, class types.
AMINO_DEFINE_DEFAULT_CLASS(Examples::SDK::IndexSet);

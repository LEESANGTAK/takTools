//-
// ================================================================================================
// Copyright 2023 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file Utility.h
/// \brief BifrostGraph Executor Internal Utilities.
///
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_INTERNAL_UTILITY_H
#define BIFROSTGRAPH_EXECUTOR_INTERNAL_UTILITY_H

#include <utility>

namespace BifrostGraph {
namespace Executor {
namespace Internal {

/// \brief Helper for swapping the content of two values.
/// \tparam X the type of the values to swap.
/// \param [inout] x1 The first value to be swapped with the second one.
/// \param [inout] x2 The second value to be swapped with the first one.
/// \post \p x1 contains the old value of \p x2
/// \post \p x2 contains the old value of \p x1
template<typename X>
void _swap(X& x1, X& x2) noexcept {
    X temp{std::move(x1)};
    x1 = std::move(x2);
    x2 = std::move(temp);
}

} // namespace Internal
} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_INTERNAL_UTILITY_H

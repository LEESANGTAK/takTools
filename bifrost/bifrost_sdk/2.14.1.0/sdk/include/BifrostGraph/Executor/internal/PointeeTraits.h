//-
// ================================================================================================
// Copyright 2023 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file PointeeTraits.h
/// \brief BifrostGraph Executor Internal Pointee Traits.
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_INTERNAL_POINTEE_TRAITS_H
#define BIFROSTGRAPH_EXECUTOR_INTERNAL_POINTEE_TRAITS_H

#include <type_traits>

namespace BifrostGraph {
namespace Executor {
namespace Internal {

/// \brief Common Traits about the to-be-pointee for some pointee wrapper classes.
/// If not, an error will be emitted at compile time.
struct PointeeTraits {
    /// \brief The trait is_compliant<T> checks whether a pointee wrapper object, like the
    /// \ref Owner template class, can be instantiated.
    /// \tparam T the pointee's exposed type used by indirection operators and by accessors.
    template <typename T>
    struct is_compliant
        : public std::integral_constant<
              bool,
              // The pointee must not be a pointer itself.
              (!std::is_pointer<T>::value &&

               // The pointee must not be a reference.
               !std::is_reference<T>::value &&

               // The type must not include "const" qualifier.
               // By definition, Owner<T> points to a non-const T.
               !std::is_const<T>::value &&

               // The type must not include "volatile" qualifier.
               !std::is_volatile<T>::value &&

               // The type must not be an array (e.g. int[]).
               !std::is_array<T>::value)> {};

    /// \brief This trait checks if the type T has a complete class type.
    /// \tparam P the storage type used for the owned object.
    template <typename, typename = void>
    struct is_type_complete : public std::false_type {
    };

    template <typename... Ps>
    struct make_void {
        using type = void;
    };

    template <typename... Ps>
    using void_p = typename make_void<Ps...>::type;

    template <typename P>
    struct is_type_complete<P, void_p<decltype(sizeof(P))>> : public std::true_type {
    };
};

} // namespace Internal
} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_INTERNAL_POINTEE_TRAITS_H

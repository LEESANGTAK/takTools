//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_DEFAULT_CLASS_DEFINE_H
#define AMINO_CORE_INTERNAL_DEFAULT_CLASS_DEFINE_H

#include "DefaultClassDeclare.h"

#include <Amino/Core/Ptr.h>

#include <Amino/Core/internal/ConfigMacros.h>

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  DefaultClassDefine.h
/// \brief Functions used to define the default class getter function of an
///        opaque user type.

//==============================================================================
// NAMESPACE Amino
//==============================================================================

namespace Amino {

template <typename T>
Ptr<T> createDefaultClass() = delete;

//==============================================================================
// NAMESPACE Internal
//==============================================================================

namespace Internal {
class CreateDefault final {
private:
    /*----- friend declarations -----*/

    template <typename T>
    friend Ptr<T> const& Amino::Internal::getDefaultClass();

    /*----- static member functions -----*/

    template <typename T>
    static constexpr std::true_type has_create_fcn(
        decltype(createDefaultClass<T>()));
    template <typename T>
    static constexpr std::false_type has_create_fcn(...);

    /*----- types -----*/

    template <typename T>
    using HasCreate = decltype(has_create_fcn<T>(nullptr));

    /*----- static member functions -----*/

    template <typename T>
    static Ptr<T> create(Ptr<T> ptr) {
        return std::move(ptr);
    }
    template <typename T>
    static std::enable_if_t<!HasCreate<T>::value, Ptr<T>> create() {
        return newClassPtr<T>();
    }
    template <typename T>
    AMINO_INTERNAL_DEPRECATED(
        "Use AMINO_DEFINE_DEFAULT_CLASS(TYPE, args...) instead.")
    static std::enable_if_t<HasCreate<T>::value, Ptr<T>> create() {
        return Amino::createDefaultClass<T>();
    }
};
} // namespace Internal

//==============================================================================
// MACROS
//==============================================================================

//------------------------------------------------------------------------------
//
/// \brief MSVC requires this expansion macro to resolve __VA_ARGS__ correctly.
#define AMINO_INTERNAL_DEFINE_DEFAULT_CLASS_EXPAND(X) X

//------------------------------------------------------------------------------
//
#define AMINO_INTERNAL_DEFINE_DEFAULT_CLASS_1(TYPE, ARG)               \
    template <>                                                        \
    Amino::Ptr<TYPE> const& Amino::Internal::getDefaultClass<TYPE>() { \
        static Amino::Ptr<TYPE> const s_default =                      \
            Amino::Internal::CreateDefault::create<TYPE>(ARG);         \
        return s_default;                                              \
    }                                                                  \
    static_assert(true, "")

//------------------------------------------------------------------------------
//
#define AMINO_INTERNAL_DEFINE_DEFAULT_CLASS_0(TYPE) \
    AMINO_INTERNAL_DEFINE_DEFAULT_CLASS_1(TYPE, )

//------------------------------------------------------------------------------
//
#define AMINO_INTERNAL_DEFINE_DEFAULT_CLASS_SELECT(_0, _1, NAME, ...) NAME

//------------------------------------------------------------------------------
//
// clang-format off
#define AMINO_INTERNAL_DEFINE_DEFAULT_CLASS(...)    \
    AMINO_INTERNAL_DEFINE_DEFAULT_CLASS_EXPAND(     \
        AMINO_INTERNAL_DEFINE_DEFAULT_CLASS_SELECT( \
            __VA_ARGS__,                            \
            AMINO_INTERNAL_DEFINE_DEFAULT_CLASS_1,  \
            AMINO_INTERNAL_DEFINE_DEFAULT_CLASS_0,  \
        )(__VA_ARGS__))
// clang-format on

} // namespace Amino

/// \endcond
#endif

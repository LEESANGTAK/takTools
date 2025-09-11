//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_INTERNAL_PIMPL_H
#define AMINO_INTERNAL_PIMPL_H

#include <Amino/Core/internal/Storage.h>

/// \cond AMINO_INTERNAL_DOCS
///
/// \file PImpl.h

namespace Amino {
namespace Internal {

/// \brief Helper to check if the private implementation is nothrow
/// constructible with the given arguments.
///
/// Moved outside of PImpl because MSVC seems to struggles with out-of-line
/// definitions of template classes nested within another template class.
template <typename T, typename... Args>
struct PImpl_is_nothrow_constructible;

/// \brief Helper implementation class for SDK classes.
template <typename T, decltype(sizeof(int)) NumPtr>
class PImpl {
private:
    friend T;

    template <typename... Args>
    constexpr static inline bool is_nothrow_constructible_v =
        PImpl_is_nothrow_constructible<T, Args...>::value;

    template <typename... Args>
    inline PImpl(Args&&... args) noexcept(is_nothrow_constructible_v<Args...>);
    inline PImpl() noexcept(is_nothrow_constructible_v<>);
    inline PImpl(PImpl&&) noexcept;
    inline PImpl(PImpl const&);
    inline ~PImpl();

    inline PImpl& operator=(PImpl&&) noexcept;
    inline PImpl& operator=(PImpl const&);

    inline decltype(auto) operator*() const noexcept;
    inline decltype(auto) operator*() noexcept;
    inline decltype(auto) operator->() const noexcept;
    inline decltype(auto) operator->() noexcept;

    inline decltype(auto) cget() const noexcept;
    inline decltype(auto) get() const noexcept;
    inline decltype(auto) get() noexcept;

    Storage_t<NumPtr> m_storage;
};

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_PROPAGATE_CONST_H
#define AMINO_CORE_INTERNAL_PROPAGATE_CONST_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file PropagateConst.h
///
/// \brief Wrapper class that propagates the constness to a pointer-like object.

#include <utility>

namespace Amino {
namespace Internal {

/// \brief Wrapper class that propagates the constness to a pointer-like object.
///
/// Conceptually very similar to
/// \a https://en.cppreference.com/w/cpp/experimental/propagate_const
///
/// This can be particularly useful when creating classes with the PImpl idiom,
/// as it will allow the class to access it's private implementation class
/// with the same constness than the class itself.
// LCOV_EXCL_BR_START
template <typename Wrapped>
class PropagateConst {
private:
    /*----- types -----*/

    using element_type       = typename Wrapped::element_type;
    using const_element_type = std::add_const_t<element_type>;
    using pointer            = std::add_pointer_t<element_type>;
    using const_pointer      = std::add_pointer_t<const_element_type>;
    using reference          = std::add_lvalue_reference_t<element_type>;
    using const_reference    = std::add_lvalue_reference_t<const_element_type>;

public:
    /*----- types -----*/

    using wrapped_type = Wrapped;

    /*----- member functions -----*/

    /// \brief Constructor.
    template <typename... Args>
    explicit constexpr PropagateConst(Args&&... args)
        : m_w(std::forward<Args>(args)...) {}

    /// \brief Same as the wrapped object's operator bool() function.
    explicit constexpr operator bool() const { return m_w.operator bool(); }

    /// \brief Same as the wrapped object's get() function.
    constexpr pointer get() { return m_w.get(); }

    /// \brief Same as the wrapped object's get() function, but const.
    constexpr const_pointer get() const { return m_w.get(); }

    /// \brief Same as the wrapped object's operator->() function.
    constexpr pointer operator->() { return m_w.operator->(); }

    /// \brief Same as the wrapped object's operator->() function, but const.
    constexpr const_pointer operator->() const { return m_w.operator->(); }

    /// \brief Same as the wrapped object's operator*() function.
    constexpr reference operator*() { return m_w.operator*(); }

    /// \brief Same as the wrapped object's operator*() function, but const.
    constexpr const_reference operator*() const { return m_w.operator*(); }

    /// \brief Get the wrapped object.
    /// \{
    constexpr Wrapped const& getWrapped() const noexcept { return m_w; }
    constexpr Wrapped&       getWrapped() noexcept { return m_w; }
    /// \}

private:
    /// \brief The wrapped "pointer-like" object.
    Wrapped m_w;
};
// LCOV_EXCL_BR_STOP

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

//-
// =============================================================================
// Copyright 2025 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_INTERNAL_CHARS_H
#define AMINO_INTERNAL_CHARS_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file Chars.h

#include <Amino/Core/StringView.h>
#include <Amino/Core/internal/ConfigMacros.h>

#define AMINO_INTERNAL_DEPRECATED_CHARS \
    AMINO_INTERNAL_DEPRECATED("Use StringView version instead.")

#define AMINO_INTERNAL_DEPRECATED_CHARS_FORCEINLINE              \
    AMINO_INTERNAL_DEPRECATED("Use StringView version instead.") \
    AMINO_INTERNAL_FORCEINLINE

namespace Amino {
namespace Internal {

/// \brief Helper "backcomp" to keep allowing functions that use to take a
/// \ref String to keep taking a `char const*` (from which \ref String is
/// implicitly constructible). The new version takes a \ref StringView which
/// is not implicitly constructible from a `char const*` (unless the size
/// is known at compile-time (i.e. `char const[N]` rather than `char
/// const*`)).
class Chars {
private:
    template <
        typename T,
        typename C = std::remove_const_t<std::remove_reference_t<T>>>
    static constexpr bool is_exactly_chars_v =
        std::is_same_v<C, char const*> || std::is_same_v<C, char*>;

public:
    template <typename T, typename = std::enable_if_t<is_exactly_chars_v<T>>>
    // NOLINTNEXTLINE(google-explicit-constructor)
    /*implicit*/ Chars(T&& c) : m_sv{c} {} // explicit constructor

    /// \brief \ref Chars is meant to be transient, just to be used as a
    /// temporary argument to a function that expects a \ref StringView.
    /// \{
    Chars()                        = delete;
    Chars(Chars&&)                 = delete;
    Chars(Chars const&)            = delete;
    Chars& operator=(Chars&&)      = delete;
    Chars& operator=(Chars const&) = delete;
    /// \}

    /// \brief Get the \ref StringView.
    StringView str() const& noexcept { return m_sv; }

private:
    /// \brief The explicitly constructed \ref StringView from the `char
    /// const*`.
    StringView m_sv;
};

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

/// \file StringView.h
///
/// \brief String view class (similar to std::string_view)
///
/// \see Amino::StringView

#ifndef AMINO_CORE_STRING_VIEW_H
#define AMINO_CORE_STRING_VIEW_H

#include "internal/ConfigMacros.h"

#include <cassert>
#include <cstddef>
#include <string_view>
#include <utility>
#ifndef AMINO_REMOVE_TRANSITIVE_HEADERS
#include <string>
#endif

//==============================================================================
// NAMESPACE Amino
//==============================================================================

namespace Amino {

//==============================================================================
// CLASS StringView
//==============================================================================

/// \brief String view class (similar to std::string_view).
class StringView {
private:
    template <typename R>
    static inline constexpr bool is_raw_cstring =
        (std::is_same_v<std::decay_t<R>, char const*> ||
         std::is_same_v<std::decay_t<R>, char*>)&& //
        !std::is_array_v<std::remove_reference_t<R>>;

    template <typename R>
    static inline constexpr bool is_sview_convertible_v =
        !is_raw_cstring<R> && std::is_convertible_v<R, std::string_view>;

    template <typename R>
    static inline constexpr bool is_sview_constructible_v =
        !is_sview_convertible_v<R> &&
        std::is_constructible_v<std::string_view, R>;

    // Allow StringView to be implicitly constructed from any type that is
    // implicitly convertible to std::string_view (except char const* is made
    // explicit).
    template <typename R>
    using enable_if_implicitly_constructible =
        std::enable_if_t<is_sview_convertible_v<R>>;

    template <typename R>
    using enable_if_explicitly_constructible =
        std::enable_if_t<is_sview_constructible_v<R>>;

public:
    /*----- member functions -----*/

    /// \brief Default constructor (empty string view)
    constexpr StringView() noexcept = default;

    /// \brief Constructing a \ref StringView from a nullptr_t is not allowed.
    // NOLINTNEXTLINE(google-explicit-constructor)
    StringView(std::nullptr_t) = delete;

    /// \brief Constructs a string view with the given data and size.
    constexpr StringView(char const* data, size_t size) noexcept
        : m_data(data), m_size(size) {}

    /// \brief \ref StringView can be explicitly constructed from types from
    /// which `std::string_view` can explicitly be constructed.
    template <typename R, enable_if_explicitly_constructible<R>* = nullptr>
    AMINO_INTERNAL_FORCEINLINE constexpr explicit StringView(R&& r)
        : StringView(Private{}, std::string_view{std::forward<R>(r)}) {}

    /// \brief \ref StringView can be implicitly constructed from types from
    /// which `std::string_view` can implicitly be constructed.
    ///
    /// \note The only exception is for raw c-strings from which the size must
    /// be obtained at runtime. In this case, the explicit constructor must be
    /// used.
    template <typename R, enable_if_implicitly_constructible<R>* = nullptr>
    // NOLINTNEXTLINE(google-explicit-constructor)
    AMINO_INTERNAL_FORCEINLINE constexpr /*implicit*/ StringView(R&& r)
        : StringView(Private{}, std::forward<R>(r)) {}

    /// \brief std::string_view conversions
    // NOLINTNEXTLINE(google-explicit-constructor)
    AMINO_INTERNAL_FORCEINLINE constexpr operator std::string_view()
        const noexcept {
        return {data(), size()}; // LCOV_EXCL_BR_LINE
    }

    /// \brief Get the string view data
    constexpr char const* data() const noexcept { return m_data; }

    /// \brief Get the size of the string view
    ///
    /// \warning Remember that a string view may not be null-terminated.
    constexpr size_t size() const noexcept { return m_size; }

    /// \copydoc size
    constexpr size_t length() const noexcept { return size(); }

    /// \brief Returns whether the string view is empty or not.
    constexpr bool empty() const noexcept { return m_size == 0; }

    /// \brief Get an iterator to the beginning of the string view.
    /// \{
    constexpr char const* cbegin() const noexcept { return m_data; }
    constexpr char const* begin() const noexcept { return cbegin(); }
    /// \}

    /// \brief Get an iterator to the end of the string view.
    /// \{
    constexpr char const* cend() const noexcept { return m_data + m_size; }
    constexpr char const* end() const noexcept { return cend(); }
    /// \}

    /// \brief Get the first character in the string view.
    /// \pre The string view must not be empty.
    constexpr char front() const noexcept { return deref(0); }

    /// \brief Get the last character in the string view.
    /// \pre The string view must not be empty.
    constexpr char back() const noexcept { return deref(m_size - 1); }

    /// \brief Get the character at the given index in the string view.
    /// \pre   idx < size()
    constexpr char operator[](size_t idx) const noexcept { return deref(idx); }

    /// \brief Comparison operators.
    /// \{
    constexpr bool operator==(StringView o) const noexcept {
        return size() == o.size() && compare(o) == 0;
    }
    constexpr bool operator<(StringView o) const noexcept {
        return compare(o) < 0;
    }
    constexpr bool operator>(StringView o) const noexcept {
        return compare(o) > 0;
    }
    constexpr bool operator!=(StringView o) const noexcept {
        return !(*this == o);
    }
    constexpr bool operator<=(StringView o) const noexcept {
        return !(*this > o);
    }
    constexpr bool operator>=(StringView o) const noexcept {
        return !(*this < o);
    }
    /// \}

private:
    struct Private {};

    /*----- member functions -----*/

    /// \brief Implementation of constructors piggy backing on std::string_view.
    AMINO_INTERNAL_FORCEINLINE constexpr StringView(
        Private, std::string_view s) noexcept
        : StringView(s.data(), s.size()) {}

    /// \brief Dereferences a character in the string view at the given index.
    constexpr char deref(size_t idx) const noexcept {
        assert(m_data);
        assert(!empty());
        assert(idx < m_size);
        return m_data[idx];
    }

    /// \brief Private implementation of comparison operators.
    ///
    /// \cond AMINO_INTERNAL_DOCS
    /// \note Not public because returned integer sign matched the sign of
    /// std::string_view::compare, but the value may not. Ideally, we should
    /// just dispatch everything to std::string_view's implementation, but
    /// that will only be possible when we officially drop support of C++14.
    /// \endcond
    constexpr int compare(StringView o) const noexcept {
        size_t size = m_size < o.m_size ? m_size : o.m_size;
        for (size_t i = 0; i < size; ++i) {
            if (m_data[i] < o.m_data[i]) return -1;
            if (m_data[i] > o.m_data[i]) return +1;
        }
        if (m_size < o.m_size) return -1;
        if (m_size > o.m_size) return +1;
        return 0;
    }

    /*----- data members -----*/

    /// \brief The string view data.
    char const* m_data = nullptr;

    /// \brief The size of the string view.
    size_t m_size = 0;
};

//==============================================================================
// NAMESPACE StringViewLiteral
//==============================================================================

namespace StringViewLiteral {

/// \brief User defined literal for Amino::StringView.
///
/// Example:
/// \code{.cpp}
/// using namespace Amino::StringViewLiteral;
/// constexpr auto my_amino_string_view = "some string"_asv;
/// \endcode
constexpr StringView operator""_asv(char const* data, size_t size) {
    return StringView{data, size};
}

} // namespace StringViewLiteral

} // namespace Amino

#endif

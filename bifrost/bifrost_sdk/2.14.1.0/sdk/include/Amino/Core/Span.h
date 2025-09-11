//-
//*****************************************************************************
// Copyright (c) 2025 Autodesk, Inc. All rights reserved.
//
// These coded instructions, statements, and computer programs contain
// unpublished proprietary information written by Autodesk, Inc. and are
// protected by Federal copyright law. They may not be disclosed to third
// parties or copied or duplicated in any form, in whole or in part, without
// the prior written consent of Autodesk, Inc.
//*****************************************************************************
//+

/// \file Span.h

#ifndef AMINO_CORE_SPAN_H
#define AMINO_CORE_SPAN_H

#include <cassert>
#include <cstddef>
#include <type_traits>

namespace Amino {

//==============================================================================
// CLASS Span
//==============================================================================

/// \brief The class template span describes an object that can refer to a
/// contiguous sequence of objects with the first element of the sequence at
/// position zero.
///
/// \note This is essentially a simplified version of `std::span` from C++20.
// LCOV_EXCL_BR_START
template <typename T>
class Span {
private:
    template <typename R>
    static inline constexpr bool is_span =
        std::is_same_v<std::remove_cv_t<std::remove_reference_t<R>>, Span<T>>;

public:
    /*----- types -----*/

    using element_type    = T;
    using value_type      = std::remove_cv_t<T>;
    using iterator        = T*;
    using const_iterator  = T const*;
    using size_type       = size_t;
    using difference_type = ptrdiff_t;

    /*----- member functions -----*/

    /// \brief Default constructor (empty \ref Span).
    constexpr Span() noexcept = default;

    /// \brief Construct a \ref Span from a pointer and a size.
    constexpr Span(T* data, size_type size)
        : m_begin{data}, m_end{internal_get_end(data, size)} {
        assert(data || size == 0);
    }

    /// \brief Construct a \ref Span from a pointer to the beginning and a
    /// pointer to the end.
    constexpr Span(T* begin, T* end) : m_begin{begin}, m_end{end} {
        assert(begin <= end);
    }

    template <typename R, typename = std::enable_if_t<!is_span<R>>>
    constexpr explicit Span(R&& r)
        : m_begin{r.data()}, m_end{m_begin + r.size()} {}

    /// \brief \ref Span is not constructible from a nullptr.
    /// \{
    constexpr Span(std::nullptr_t, size_type) = delete;
    constexpr Span(T*, std::nullptr_t)        = delete;
    constexpr Span(std::nullptr_t, T*)        = delete;
    /// \}

    /// \brief Check if the \ref Span is empty.
    constexpr bool empty() const { return m_begin == m_end; }

    /// \brief Access the ith element.
    ///
    /// \pre i < size()
    /// \{
    constexpr T const& operator[](size_type i) const {
        assert(i < size());
        return m_begin[i];
    }
    constexpr T& operator[](size_type i) {
        assert(i < size());
        return m_begin[i];
    }
    /// \}

    /// \brief Access the first element.
    ///
    /// \pre The span is not empty.
    /// \{
    constexpr T const& front() const {
        assert(!empty());
        return *m_begin;
    }
    constexpr T& front() {
        assert(!empty());
        return *m_begin;
    }
    /// \}

    /// \brief Access the last element.
    ///
    /// \pre The span is not empty.
    /// \{
    constexpr T const& back() const {
        assert(!empty());
        return *(m_end - 1);
    }
    constexpr T& back() {
        assert(!empty());
        return *(m_end - 1);
    }
    /// \}

    /// \brief Returns an iterator to the beginning of the \ref Span.
    /// \{
    constexpr const_iterator cbegin() const { return m_begin; }
    constexpr const_iterator begin() const { return m_begin; }
    constexpr iterator       begin() { return m_begin; }
    /// \}

    /// \brief Returns an iterator to the end of the \ref Span.
    /// \{
    constexpr const_iterator cend() const { return m_end; }
    constexpr const_iterator end() const { return m_end; }
    constexpr iterator       end() { return m_end; }
    /// \}

    /// \brief Direct access to the underlying contiguous storage of the \ref
    /// Span.
    constexpr T* data() const { return m_begin; }

    /// \brief Returns the number of elements in the \ref Span.
    constexpr size_type size() const {
        return static_cast<size_type>(m_end - m_begin);
    }

private:
    constexpr static T* internal_get_end(T* data, size_type size) {
        if (data) // separate line for coverage
            return data + size;
        return nullptr;
    }

    /*----- data members -----*/

    T* m_begin{nullptr};
    T* m_end{nullptr};
};
// LCOV_EXCL_BR_STOP

/// \brief Deduction guides for \ref Span.
/// \{
template <typename T>
Span(T*, size_t) -> Span<T>;
template <typename T>
Span(T*, T*) -> Span<T>;
template <typename R>
Span(R&&) -> Span<std::remove_pointer_t<decltype(std::declval<R>().data())>>;
/// \}

//==============================================================================
// CLASS SpanParam
//==============================================================================

/// \brief Same as \ref Span but the constructor from a range is implicit,
/// making it more convenient and safe to use as a function input parameter.
template <typename T>
class SpanParam : public Span<T> {
private:
    template <typename R>
    static inline constexpr bool is_span_param =
        std::is_same_v<std::remove_cv_t<std::remove_reference_t<R>>, Span<T>>;

public:
    using Span<T>::Span;

    template <typename R, typename = std::enable_if_t<!is_span_param<R>>>
    // NOLINTNEXTLINE(google-explicit-constructor)
    /*implicit*/ constexpr SpanParam(R&& r) : Span<T>{r} {}
};

/// \brief Deduction guides for \ref SpanParam.
/// \{
template <typename T>
SpanParam(T*, size_t) -> SpanParam<T>;
template <typename T>
SpanParam(T*, T*) -> SpanParam<T>;
template <typename R>
SpanParam(R&&)
    -> SpanParam<std::remove_pointer_t<decltype(std::declval<R>().data())>>;
/// \}

} // namespace Amino

#endif

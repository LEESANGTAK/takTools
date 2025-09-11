//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \cond AMINO_INTERNAL_DOCS
///
/// \file WrappedIterator.h
///
/// \brief \ref Amino::Internal::WrappedIterator : Wrapped iterator adaptor.

#ifndef AMINO_WRAPPPEDITERATOR_H
#define AMINO_WRAPPPEDITERATOR_H

#include <iterator>
#include <type_traits>

namespace Amino {
namespace Internal {

//==============================================================================
// CLASS WrappedIterator
//==============================================================================

/// \brief Wrapped iterator adaptor.
///
/// This class wraps a base iterator. The wrapped iterator forward all of its
/// operations to the underlying base operator and thus behaves the same way as
/// the underlying base iterator. But, the wrapped iterator is a different type
/// than the base iterator and a wrapped iterator can't be constructed out of a
/// base iterator. Only the associated \p Factory class is allowed to construct
/// the wrapped iterator. This prevents accidental conversions between the base
/// and the wrapped iterator types.
///
/// The interface of this class follows the same pattern as the other C++ std
/// iterator adaptor such as std::reverse_iterator and std::move_iterator.
///
/// \tparam Iter The base iterator type. The base iterator type must be at least
/// a bidirectional_iterator.
///
/// \tparam Factory A class which will be allowed to invoke the \ref
///  WrappedIterator constructor.
template <typename Iter, typename Factory>
class WrappedIterator {
public:
    /// \brief Base iterator type
    using iterator_type = Iter;

    using value_type = typename std::iterator_traits<iterator_type>::value_type;
    using difference_type =
        typename std::iterator_traits<iterator_type>::difference_type;
    using pointer   = typename std::iterator_traits<iterator_type>::pointer;
    using reference = typename std::iterator_traits<iterator_type>::reference;
    using iterator_category =
        typename std::iterator_traits<iterator_type>::iterator_category;

    // For upcoming, C++20 concepts:
    // using iterator_concept =
    //     typename std::iterator_traits<iterator_type>::iterator_concept;

private:
    iterator_type m_i{};

public:
    /// \brief Default constructor.
    ///
    /// The underlying iterator is value initialized. Operations on the
    /// resulting iterator have defined behavior if and only if the
    /// corresponding operations on a value initialized Iter also have defined
    /// behavior.
    constexpr WrappedIterator() noexcept = default;

    /// \brief The underlying iterator is initialized with that of other.
    ///
    /// This overload participates in overload resolution only if U is not the
    /// same type as Iter and std::convertible_to<const U&, Iter> is modeled
    template <
        typename U,
        typename =
            std::enable_if_t<std::is_convertible<U, iterator_type>::value>>
    // NOLINTNEXTLINE(google-explicit-constructor)
    constexpr WrappedIterator(const WrappedIterator<U, Factory>& other) noexcept
        : m_i(other.base()) {}

    /// \brief Accesses the pointed-to element.
    ///
    /// \{
    constexpr reference operator*() const noexcept { return *m_i; }

    constexpr pointer operator->() const noexcept {
        return m_i;
        // In C++20, one could use std::to_address() and WrapIter would become
        // even more flexible!
        //
        // return std::to_address(m_i);
    }
    /// \}

    /// \brief Advances or decrements the iterator.
    ///
    /// \{
    constexpr WrappedIterator& operator++() noexcept {
        ++m_i;
        return *this;
    }

    constexpr WrappedIterator operator++(int) noexcept {
        WrappedIterator tmp(*this);
        ++(*this);
        return tmp;
    }

    constexpr WrappedIterator& operator--() noexcept {
        --m_i;
        return *this;
    }

    constexpr WrappedIterator operator--(int) noexcept {
        WrappedIterator tmp(*this);
        --(*this);
        return tmp;
    }

    constexpr WrappedIterator operator+(difference_type n) const noexcept {
        WrappedIterator w(*this);
        w += n;
        return w;
    }

    constexpr WrappedIterator& operator+=(difference_type n) noexcept {
        m_i += n;
        return *this;
    }

    constexpr WrappedIterator operator-(difference_type n) const noexcept {
        return *this + (-n);
    }

    constexpr WrappedIterator& operator-=(difference_type n) noexcept {
        *this += -n;
        return *this;
    }
    /// \}

    /// \brief Accesses an element by index.
    constexpr reference operator[](difference_type n) const noexcept {
        return m_i[n];
    }

    /// \brief Accesses the underlying iterator.
    constexpr iterator_type base() const noexcept { return m_i; }

private:
    /// \brief The underlying iterator is initialized with x.
    ///
    /// Only the factory class is allowed to invoke it.
    constexpr explicit WrappedIterator(iterator_type x) noexcept : m_i(x) {}

    friend Factory;
};

/// \brief Compares the underlying iterators
///
/// \{
template <class Iter1, typename Factory>
constexpr bool operator==(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter1, Factory>& y) noexcept {
    return x.base() == y.base();
}

template <class Iter1, class Iter2, typename Factory>
constexpr bool operator==(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter2, Factory>& y) noexcept {
    return x.base() == y.base();
}

template <class Iter1, typename Factory>
constexpr bool operator<(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter1, Factory>& y) noexcept {
    return x.base() < y.base();
}

template <class Iter1, class Iter2, typename Factory>
constexpr bool operator<(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter2, Factory>& y) noexcept {
    return x.base() < y.base();
}

template <class Iter1, typename Factory>
constexpr bool operator!=(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter1, Factory>& y) noexcept {
    return !(x == y);
}

template <class Iter1, class Iter2, typename Factory>
constexpr bool operator!=(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter2, Factory>& y) noexcept {
    return !(x == y);
}

template <class Iter1, typename Factory>
constexpr bool operator>(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter1, Factory>& y) noexcept {
    return y < x;
}

template <class Iter1, class Iter2, typename Factory>
constexpr bool operator>(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter2, Factory>& y) noexcept {
    return y < x;
}

template <class Iter1, typename Factory>
constexpr bool operator>=(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter1, Factory>& y) noexcept {
    return !(x < y);
}

template <class Iter1, class Iter2, typename Factory>
constexpr bool operator>=(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter2, Factory>& y) noexcept {
    return !(x < y);
}

template <class Iter1, typename Factory>
constexpr bool operator<=(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter1, Factory>& y) noexcept {
    return !(y < x);
}

template <class Iter1, class Iter2, typename Factory>
constexpr bool operator<=(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter2, Factory>& y) noexcept {
    return !(y < x);
}
/// \}

/// \brief Advances the iterator.
template <class Iter1, class Iter2, typename Factory>
constexpr auto operator-(
    const WrappedIterator<Iter1, Factory>& x,
    const WrappedIterator<Iter2, Factory>& y) noexcept
    -> decltype(x.base() - y.base()) {
    return x.base() - y.base();
}

/// \brief Computes the distance between two iterator adaptors.
template <class Iter1, typename Factory>
constexpr WrappedIterator<Iter1, Factory> operator+(
    typename WrappedIterator<Iter1, Factory>::difference_type n,
    WrappedIterator<Iter1, Factory>                           x) noexcept {
    x += n;
    return x;
}

} // namespace Internal
} // namespace Amino

#endif // AMINO_WRAPPPEDITERATOR_H

/// \endcond

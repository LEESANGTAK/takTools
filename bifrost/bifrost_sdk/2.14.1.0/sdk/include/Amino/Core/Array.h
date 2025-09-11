//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_ARRAY_H
#define AMINO_ARRAY_H

/// \file Array.h
///
/// \brief A resizable container of contiguous elements.
///
/// \see Amino::Array

//==============================================================================
// EXTERNAL DECLARATIONS
//==============================================================================

#include "ArrayFwd.h"

#include "internal/ArrayImpl.h"
#include "internal/ConfigMacros.h"

#include <type_traits>

namespace Amino {

//==============================================================================
// FORWARD DECLARATIONS
//==============================================================================

template <typename T>
class Array;

//==============================================================================
// ALIAS ArrayD (Array with given dimension)
//==============================================================================

/// \brief Helper alias for multidimensional array types.
///
/// Declaring multidimenstional array can yield very long type names and make
/// the code hard to read. Using this alias can therefore greatly help with
/// code readability and code maintainability.
///
/// For example:
/// \code{.cpp}
/// // The two type aliases resolve to the same type.
/// // But the version using Amino::ArrayD_t is much more concise, easier to
/// // understand and read.
/// using ArrayInt3D_1 =
///     Amino::Array<Amino::Ptr<Amino::Array<Amino::Ptr<Amino::Array<int>>>>>;
///
/// using ArrayInt3D_2 = Amino::ArrayD_t<3, int>;
/// static_assert(std::is_same<ArrayInt3D_1,ArrayInt3D_2>::value, "");
/// \endcode
///
/// Note that \ref Ptr are used to manage individual array element types.
/// This is always necessary in order to use those arrays in Amino graphs, since
/// array types must always be managed by \ref Ptr when used in Amino graphs.
template <unsigned Dimension, typename T>
using ArrayD_t = Internal::MultiDimensionalArray_t<Dimension, T>;

//==============================================================================
// FUNCTION warn_if_unsupported_element
//==============================================================================

/// \brief Helpers to produce a warning on unsupported element types when
///        constructing Amino::Array of such types.
/// \{
template <typename T>
inline constexpr void warn_if_unsupported_element();
/// \}

//==============================================================================
// CLASS Array
//==============================================================================

/// \brief Define a Amino array of elements of type \p T.
///
/// Amino Arrays are resizable containers of contiguous elements.
///
/// \warning \ref Amino::Array is NOT a replacement for other contiguous
/// containers (like std::vector). \ref Amino::Array is only meant to be used
/// within an Amino graph. Therefore, if a value never needs to flow directly
/// into the graph, a standard container (like std::vector) should be used
/// instead.
///
/// Amino Arrays of any Amino-known types can be used in Amino graphs, but they
/// must always be memory managed by \ref Amino::Ptr. If the element type is
/// itself an Array or a custom user class, it must also be managed by an
/// \ref Amino::Ptr.
///
/// \warning \ref Amino::Array is not a replacement for std::vector or any
/// other random access container. It is a type primarily meant to be used in
/// Amino graphs (since its internal layout and details are known to the
/// compiler).
///
/// \tparam T The type of the elements.
template <typename T>
class Array : private Internal::ArrayImpl<T> {
private:
    static_assert(
        std::is_same<std::remove_cv_t<T>, T>::value,
        "Amino::Array must have a non-const, non-volatile value_type");

    /// \brief The internal array implementation class.
    using BaseClass = Internal::ArrayImpl<T>;

public:
    /*----- types -----*/

    /// \brief The type of the value being stored in the array.
    /// Equivalent to `T`.
    using value_type = typename BaseClass::value_type;

    /// \brief Type to represent a mutable pointer to an array element value.
    /// Equivalent to `value_type*`.
    using pointer = typename BaseClass::pointer;

    /// \brief Type to represent a constant pointer to an array element value.
    /// Equivalent to `value_type const*`.
    using const_pointer = typename BaseClass::const_pointer;

    /// \brief Type to represent a mutable reference to an array element value.
    /// Equivalent to `value_type&`.
    using reference = typename BaseClass::reference;

    /// \brief Type to represent a constant reference to an array element value.
    /// Equivalent to `value_type const&`.
    using const_reference = typename BaseClass::const_reference;

    /// \brief A signed integral type. Usually the same as \p ptrdiff_t.
    using difference_type = typename BaseClass::difference_type;

    /// \brief An unsigned integral that can represent any non-negative value of
    /// \p difference_type. Usually the same as \p size_t.
    using size_type = typename BaseClass::size_type;

    /// \brief Type representing a random-access iterator to a \p value_type.
    using iterator = typename BaseClass::iterator;

    /// \brief Type representing a random-access iterator to a const \p
    /// value_type.
    using const_iterator = typename BaseClass::const_iterator;

private:
    /// \brief Traits to enable functions which can take input iterators only.
    template <typename InputIterator>
    using enable_if_input_iterator_t = std::enable_if_t<std::is_convertible<
        typename std::iterator_traits<InputIterator>::iterator_category,
        std::input_iterator_tag>::value>;

    /// \brief Traits to enable functions only if T is constructible from the
    /// given arguments.
    template <typename... Args>
    using enable_if_constructible_t =
        std::enable_if_t<std::is_constructible<T, Args...>::value>;

public:
    /*----- constructors and assignment functions -----*/

    /// \brief Construct an empty array.
    explicit Array() : BaseClass() { warn_if_unsupported_element<T>(); }

    /// \brief Construct an array with \p n default initialized elements.
    ///
    /// \param n The array size.
    explicit Array(size_type n) : BaseClass(n) {
        warn_if_unsupported_element<T>();
    }

    /// \brief Construct an array with \p n elements of value \p value.
    ///
    /// \param n     The array size.
    /// \param value The value to fill the array.
    Array(size_type n, const value_type& value) : BaseClass(n, value) {
        warn_if_unsupported_element<T>();
    }

    /// \brief Construct an array with the values in the range
    /// <tt>[first,last)</tt>, in the same order.
    ///
    /// The range used is <tt>[first,last)</tt>, which includes all the elements
    /// between \a first and \a last, including the element pointed by \a first,
    /// but not the element pointed by \a last.
    ///
    /// \tparam InputIterator Input iterator type.
    ///
    /// \param first Input iterator to the first position in the range.
    /// \param last  Input iterator to the last position in the range.
    template <
        class InputIterator,
        typename = enable_if_input_iterator_t<InputIterator>>
    Array(InputIterator first, InputIterator last) : BaseClass(first, last) {
        warn_if_unsupported_element<T>();
    }

    /// \brief Construct an array with the contents of the initializer_list.
    ///
    /// \param init The initializer list.
    Array(std::initializer_list<value_type> init) : BaseClass(init) {
        warn_if_unsupported_element<T>();
    }

    /// \brief Copy constructor.
    ///
    /// Construct a new array containing a copy of the elements in \p other, in
    /// the same order.
    ///
    /// \param other An array of the same type whose elements are to be copied.
    Array(const Array<T>& other) = default;

    /// \brief Move constructor.
    ///
    /// Construct a new array taking ownership of the elements in \p other.
    ///
    /// \param other An array of the same type whose elements are to be copied.
    Array(Array<T>&& other) noexcept = default;

    /// \brief Destroys the array. This calls the destructor for each element,
    /// and releases all the storage allocated by the array.
    ~Array() = default;

    /// \brief Copy assignment operator.
    ///
    /// Copy all the elements from \p other into the current array.
    /// Any elements held in the current array before this call are destroyed.
    ///
    /// \param other An array of the same type.
    Array<T>& operator=(const Array<T>& other) = default;

    /// \brief Move assignment operator.
    ///
    /// Take ownership of all the elements of \p other into the current array.
    /// Any elements held in the current array before this call are destroyed.
    ///
    /// \param other An array of the same type.
    Array<T>& operator=(Array<T>&& other) noexcept = default;

    /// \brief Copy all the elements from \p init into the current array.
    ///
    /// Any elements held in the current array before this call are destroyed.
    ///
    /// \param init An initializer list.
    Array<T>& operator=(std::initializer_list<value_type> init) {
        BaseClass::assign(init.begin(), init.end());
        return *this;
    }

    /// \brief Replaces the contents of the container with \p count copies of \p
    /// value value.
    ///
    /// \note This is almost equivalent to `*this = Array<T>(count, value)`
    /// except that the already allocated memory by `*this` may be reused if its
    /// capacity is large enough to hold \p count elements.
    ///
    /// \param count the new size of the container.
    /// \param value the value to initialize elements of the container with.
    ///
    /// \note Any elements held in the array before this call are destroyed.
    void assign(size_type count, const value_type& value) {
        BaseClass::assign(count, value);
    }

    /// \brief Replaces the contents of the container with copies of those in
    /// the range <tt>[first,last)</tt>.
    ///
    /// \note This is almost equivalent to `*this = Array<T>(first, last)`
    /// except that the already allocated memory by `*this` may be reused if
    /// its capacity is large enough to hold `std::distance(first, last)`
    /// elements.
    ///
    /// \param first iterator to first element to copy
    /// \param last  end iterator of range to copy
    ///
    /// \note Any elements held in the array before this call are destroyed.
    /// \note Container size will the same as the range after the call.
    template <
        class InputIterator,
        typename = enable_if_input_iterator_t<InputIterator>>
    void assign(InputIterator first, InputIterator last) {
        BaseClass::assign(first, last);
    }

    /// \brief Replaces the contents of the container with the elements from the
    /// initializer list \p init.
    ///
    /// \note This is almost equivalent to `*this = Array<T>(init)`
    /// except that the already allocated memory by `*this` may be reused if
    /// its capacity is large enough to hold `std::distance(first, last)`
    /// elements.
    ///
    /// \param init initializer list to copy the values from
    ///
    /// \note Any elements held in the current array before this call are
    /// destroyed.
    ///
    /// \note Container size will the same as the initializer list after the
    /// call.
    void assign(std::initializer_list<T> init) {
        BaseClass::assign(init.begin(), init.end());
    }

    /*----- element accessor functions -----*/

    /// \brief Get a reference to the element at position \p n in the array.
    ///
    /// \warning Unlike std::vector::at(), Amino::Array::at() asserts if
    /// `n >= size()`. That's because \ref Amino::Array does not throw any
    /// exceptions, so it asserts instead.
    ///
    /// \pre `n < size()`
    ///
    /// \param n The index of the element in the array.
    ///
    /// \return A reference to the element at position \p n in the array.
    /// \{
    reference       at(size_type n) { return BaseClass::at(n); }
    const_reference at(size_type n) const { return BaseClass::at(n); }
    /// \}

    /// \brief Get a reference to the element at position \p n in the  array.
    ///
    /// \pre `n < size()`
    ///
    /// \param n The index of the element in the array.
    ///
    /// \return A reference to the element at position \p n in the array.
    /// \{
    reference       operator[](size_type n) { return BaseClass::operator[](n); }
    const_reference operator[](size_type n) const {
        return BaseClass::operator[](n);
    }
    /// \}

    /// \brief Get a reference to the first element in the array.
    ///
    /// Unlike begin(), which returns an iterator to the first element in the
    /// array, this function returns a direct reference to the first element.
    ///
    /// \pre `!empty()`
    ///
    /// \return A reference to the first element in the array.
    /// \{
    reference       front() { return BaseClass::front(); }
    const_reference front() const { return BaseClass::front(); }
    /// \}

    /// \brief Get a reference to the last element in the array.
    ///
    /// Unlike end(), which returns an iterator just past the last element in
    /// the array, this function returns a direct reference to the last element.
    ///
    /// \pre `!empty()`
    ///
    /// \return A reference to the last element in the array.
    /// \{
    reference       back() { return BaseClass::back(); }
    const_reference back() const { return BaseClass::back(); }
    /// \}

    /// \brief Get a pointer to the underlying storage of the array.
    ///
    /// \return A pointer to the underlying storage of the array.
    /// \{
    pointer       data() noexcept { return BaseClass::data(); }
    const_pointer data() const noexcept { return BaseClass::data(); }
    /// \}

    /*----- iterators functions -----*/

    /// \brief Get a iterator pointing to the first element in the array.
    ///
    /// Unlike `front()`, which returns a direct reference to the first element
    /// in the array, this function returns a random-access iterator pointing to
    /// the first element. If the array is empty, the returned iterator is the
    /// same as `end()`.
    ///
    /// \return An iterator to the first element in the array.
    /// \{
    iterator       begin() noexcept { return BaseClass::begin(); }
    const_iterator begin() const noexcept { return BaseClass::begin(); }
    const_iterator cbegin() const noexcept { return BaseClass::cbegin(); }
    /// \}

    /// \brief Get a iterator pointing to the element just past the last
    /// element in the array (<em>past-the-end element</em>).
    ///
    /// Unlike `back()`, which returns a reference to the last element in the
    /// array, this function returns a random-access iterator pointing past the
    /// last element. This iterator does not point to any valid element, and
    /// therefore should not be dereferenced. If the array is empty, the
    /// returned iterator is the same as `begin()`.
    ///
    /// \return An iterator pointing past the last element in the array.
    /// \{
    iterator       end() noexcept { return BaseClass::end(); }
    const_iterator end() const noexcept { return BaseClass::end(); }
    const_iterator cend() const noexcept { return BaseClass::cend(); }
    /// \}

    /*----- capacity related functions -----*/

    /// \brief Check whether the array is empty (`size() == 0`).
    ///
    /// \return true if the array is empty, false otherwise.
    bool empty() const noexcept { return BaseClass::empty(); }

    /// \brief Get the number of elements in the array.
    ///
    /// \return The number of elements in the array.
    size_type size() const noexcept { return BaseClass::size(); }

    /// \brief Return the maximum number of elements the array is able to hold
    /// due to system or library implementation limitations, i.e.
    /// std::distance(begin(), end()) for the largest possible container.
    ///
    /// \note This value typically reflects the theoretical limit on the size of
    /// the container, at most std::numeric_limits<difference_type>::max(). At
    /// runtime, the size of the container may be limited to a value smaller
    /// than max_size() by the amount of RAM available.
    ///
    /// \return The theoretical maximum number of elements the array can hold.
    size_type max_size() const { return BaseClass::max_size(); }

    /// \brief Increase the capacity of the array to a value that's greater or
    /// equal to new_capacity.
    ///
    /// If new_capacity is greater than the current capacity(), new storage is
    /// allocated and elements are moved the that new storage, otherwise the
    /// method does nothing.
    ///
    /// \param new_capacity The new capacity of the array.
    void reserve(size_type new_capacity) { BaseClass::reserve(new_capacity); }

    /// \brief Get the number of elements that the container has currently
    /// allocated space for.
    ///
    /// \return The number of elements that the container has currently
    /// allocated space for.
    size_type capacity() const noexcept { return BaseClass::capacity(); }

    /// \brief Requests the removal of unused capacity.
    void shrink_to_fit() noexcept { BaseClass::shrink_to_fit(); }

    /*----- modifier functions -----*/

    /// \brief Removes all elements from the container.
    /// \note Leaves capacity unchanged.
    void clear() noexcept { BaseClass::clear(); }

    /// \brief Inserts value before pos.
    ///
    /// \param pos iterator before which the content will be inserted. pos may
    ///        be the `end()` iterator
    /// \param value element value to insert
    ///
    /// \return Iterator pointing to the inserted value
    /// \{
    iterator insert(const_iterator pos, const value_type& value) {
        return BaseClass::insert(pos, value);
    }
    iterator insert(const_iterator pos, value_type&& value) {
        return BaseClass::insert(pos, std::move(value));
    }
    /// \}

    /// \brief Inserts count copies of the value before pos.
    ///
    /// \param pos iterator before which the content will be inserted. pos may
    ///        be the `end()` iterator
    /// \param count number of copies to make
    /// \param value element value to copy
    ///
    /// \return Iterator pointing to the first element inserted, or pos if
    /// count==0.
    iterator insert(
        const_iterator pos, size_type count, const value_type& value) {
        return BaseClass::insert(pos, count, value);
    }

    /// \brief Inserts elements from range <tt>[first,last)</tt> before pos.
    ///
    /// \param pos iterator before which the content will be inserted. pos may
    ///            be the end() iterator
    /// \param first iterator to first element to insert
    /// \param last end iterator of range to insert
    ///
    /// \warning \a first and \a last can't be iterators into container for
    /// which insert is called
    ///
    /// \pre ` (begin() <=   pos &&   pos <= end())`
    /// \pre `!(begin() <= first && first <= end())`
    /// \pre `!(begin() <=  last &&  last <= end())`
    ///
    /// \return Iterator pointing to the first element inserted, or pos if
    /// first==last.
    template <
        class InputIterator,
        typename = enable_if_input_iterator_t<InputIterator>>
    iterator insert(
        const_iterator pos, InputIterator first, InputIterator last) {
        return BaseClass::insert(pos, first, last);
    }

    /// \brief inserts elements from initializer list \a init before pos.
    ///
    /// \param pos iterator before which the content will be inserted. pos may
    /// be the end() iterator
    ///
    /// \param init initializer list to insert the values from
    ///
    /// \return Iterator pointing to the first element inserted, or pos if init
    /// is empty.
    iterator insert(
        const_iterator pos, std::initializer_list<value_type> init) {
        return BaseClass::insert(pos, init.begin(), init.end());
    }

    /// \brief Removes the element at pos from the container.
    ///
    /// \param pos iterator to the element to remove. Must be valid and
    /// dereferenceable
    ///
    /// \return Iterator following the last removed element. If the iterator pos
    /// refers to the last element, the end() iterator is returned.
    iterator erase(const_iterator pos) { return BaseClass::erase(pos); }

    /// \brief Removes the elements in the range <tt>[first,last)</tt> from the
    /// container.
    ///
    /// \param first beginning of range to remove
    ///
    /// \param last end of range to remove
    ///
    /// \return Iterator following the last removed element. If the iterator pos
    /// refers to the last element, the end() iterator is returned.
    iterator erase(const_iterator first, const_iterator last) {
        return BaseClass::erase(first, last);
    }

    /// \brief Appends the given element value to the end of the container.
    /// \{
    void push_back(const value_type& value) { BaseClass::push_back(value); }
    void push_back(value_type&& value) {
        BaseClass::push_back(std::move(value));
    }
    /// \}

    /// \brief Appends an element constructed from the given arguments to the
    /// end of the container.
    ///
    /// \warning This assumes the constructor taking the given arguments does
    /// not throw.
    template <typename... Args, typename = enable_if_constructible_t<Args...>>
    void emplace_back(Args&&... args) {
        BaseClass::emplace_back(std::forward<Args>(args)...);
    }

    /// \brief Removes the last element of the container.
    ///
    /// \pre `!empty()`
    ///
    /// \note Calling pop_back on an empty container is undefined.
    void pop_back() { BaseClass::pop_back(); }

    /// \brief Resizes the container to contain \p count elements.
    ///
    /// If the current size is greater than count, the container is reduced to
    /// its first count elements. If the current size is less than count,
    /// additional default elements are appended.
    ///
    /// \post `size() == count`
    ///
    /// \param count new size of the container.
    void resize(size_type count) { BaseClass::resize(count); }

    /// \brief Resizes the container to contain \p count elements.
    ///
    /// If the current size is greater than count, the container is reduced to
    /// its first count elements. If the current size is less than count,
    /// additional copies of \p value are appended.
    ///
    /// \post `size() == count`
    ///
    /// \param count new size of the container.
    /// \param value the value to initialize the new elements with.
    void resize(size_type count, const value_type& value) {
        BaseClass::resize(count, value);
    }

    /// \brief Exchange the content of the array by the content of \a other,
    /// which is another array object containing elements of the same type.
    ///
    /// Array sizes can be different.
    ///
    /// After a call to this function, the elements in this array are those
    /// which were in \a other before the call, and the elements of \a other are
    /// those which were in this array. All iterators, references and pointers
    /// remain valid for the swapped arrays.
    ///
    /// \param other An array of the same type the swap with.
    void swap(Array& other) noexcept { BaseClass::swap(other); }

private:
    // WARNING - this class MUST NOT have any data members or virtual functions
    // (It must be perfectly ABI compatible with the UntypedArray).
};

//------------------------------------------------------------------------------
//
/// \cond AMINO_INTERNAL_DOCS
template <Internal::TypeCategory>
struct MaybeWarn {
    static inline constexpr void amino_array_of_unsupported_element() {}
};
template <>
struct MaybeWarn<Internal::TypeCategory::eUninstantiable> {
    AMINO_INTERNAL_DEPRECATED(
        "The element type of this array is not supported in Amino.\n    "
        "All types must be default constructible, copy/move constructible,"
        "copy/move assignable, and destructible.\n    "
        "Class types wrapped in Amino::Ptr must provide a default getter "
        "(see Amino/Cpp/ClassDeclare.h and Amino/Cpp/ClassDefine.h).\n    "
        "It won't be type-erased, nor support virtualized operations.")
    static inline constexpr void amino_array_of_unsupported_element() {}
};
/// \endcond

template <typename T>
inline constexpr void warn_if_unsupported_element() {
    MaybeWarn<Internal::GetTypeCategory<T>::value>::
        amino_array_of_unsupported_element();
}

} // namespace Amino

#endif

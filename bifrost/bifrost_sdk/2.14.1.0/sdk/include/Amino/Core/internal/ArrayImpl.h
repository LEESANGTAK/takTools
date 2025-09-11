//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

#ifndef AMINO_ARRAY_IMPL_H
#define AMINO_ARRAY_IMPL_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  ArrayImpl.h
/// \brief Internal implementation of Amino::Array
/// \see   Amino::Internal::ArrayImpl

//==============================================================================
// EXTERNAL DECLARATIONS
//==============================================================================

#include <Amino/Core/ArrayFwd.h>
#include <Amino/Core/PtrFwd.h>

#include "ArrayDataRep.h"
#include "UntypedTypeRepT.h"
#include "WrappedIterator.h"

#include <algorithm>
#include <iterator>
#include <type_traits>

namespace Amino {
namespace Internal {

//-----------------------------------------------------------------------------
// STRUCT MultiDimensionalArray
//-----------------------------------------------------------------------------

/// \brief Traits used to create multidimensional array types.
///
/// (see \ref Amino::ArrayD_t)
template <unsigned D, typename T>
struct MultiDimensionalArray;

template <unsigned D, typename T>
using MultiDimensionalArray_t = typename MultiDimensionalArray<D, T>::type;

template <typename T>
struct MultiDimensionalArray<1, T> {
    using type = Array<T>;
};

template <unsigned D, typename T>
struct MultiDimensionalArray {
    using type = Array<Ptr<MultiDimensionalArray_t<D - 1, T>>>;
};

//=============================================================================
// CLASS ArrayStaticHandler<T, bool>
//=============================================================================

template <typename T, bool>
struct ArrayStaticHandler;

//=============================================================================
// CLASS ArrayImpl
//=============================================================================

/// \brief \ref Amino::Array's private implementation.
///
/// \tparam T The type of the array element
template <typename T>
class ArrayImpl : public ArrayDataRep {
    // WARNING - this class MUST NOT have any data members or virtual functions
    static_assert(
        std::is_same<std::remove_cv_t<T>, T>::value,
        "ArrayImpl must have a non-const, non-volatile value_type");

protected:
    /// \copydoc Amino::Array::value_type
    using value_type = T;

    /// \copydoc Amino::Array::pointer
    using pointer = value_type*;

    /// \copydoc Amino::Array::const_pointer
    using const_pointer = value_type const*;

    /// \copydoc Amino::Array::reference
    using reference = value_type&;

    /// \copydoc Amino::Array::const_reference
    using const_reference = value_type const&;

    /// \copydoc Amino::Array::iterator
    using iterator = WrappedIterator<pointer, ArrayImpl<T>>;

    /// \copydoc Amino::Array::const_iterator
    using const_iterator = WrappedIterator<const_pointer, ArrayImpl<T>>;

    /// \copydoc Amino::Array::enable_if_input_iterator_t
    template <typename InputIterator>
    using enable_if_input_iterator_t = std::enable_if_t<std::is_convertible<
        typename std::iterator_traits<InputIterator>::iterator_category,
        std::input_iterator_tag>::value>;

private:
    /// \brief The allocator type used to define the storage allocation model.
    using allocator_type = UntypedTypeRepT<T>;

    /// \brief The value_type which volatile and const qualifiers removed.
    using mutable_value_type = std::remove_cv_t<value_type>;

protected:
    /*----- constructors and assignment functions -----*/

    /// \copydoc Amino::Array::Array()
    ArrayImpl() : ArrayDataRep(allocator_type(), 0) {}

    /// \copydoc Amino::Array::Array(size_type)
    explicit ArrayImpl(size_type n) : ArrayDataRep(allocator_type(), n) {
        allocator_type alloc = get_allocator_t();
        auto           it    = get_begin_storage();
        auto           end   = get_end_storage();
        while (it != end) alloc.construct(it++);
    }

    /// \copydoc Amino::Array::Array(size_type,const value_type&)
    ArrayImpl(size_type n, const value_type& value)
        : ArrayDataRep(allocator_type(), n) {
        construct_range(get_begin_storage(), get_end_storage(), value);
    }

    /// \copydoc Amino::Array::Array(InputIterator,InputIterator)
    template <
        class InputIterator,
        typename = enable_if_input_iterator_t<InputIterator>>
    ArrayImpl(InputIterator first, InputIterator last)
        : ArrayDataRep(allocator_type(), last - first) {
        construct_range(get_begin_storage(), get_end_storage(), first);
    }

    /// \copydoc Amino::Array::Array(std::initializer_list<value_type>)
    ArrayImpl(std::initializer_list<value_type> init)
        : ArrayDataRep(allocator_type(), init.size()) {
        construct_range(get_begin_storage(), get_end_storage(), init.begin());
    }

    /// \copydoc Amino::Array::Array(const Array&)
    ArrayImpl(const ArrayImpl& other)
        : ArrayDataRep(allocator_type(), other.size()) {
        construct_range(get_begin_storage(), get_end_storage(), other.begin());
    }

    /// \copydoc Amino::Array::Array(Array&&)
    ArrayImpl(ArrayImpl&& other) noexcept : ArrayDataRep(allocator_type()) {
        swap(other);
        assert(other.get_begin_element() == nullptr);
    }

    /// \copydoc Amino::Array::~Array()
    ~ArrayImpl() { clear(); }

    /// \copydoc Amino::Array::operator=(const Array&)
    ArrayImpl& operator=(const ArrayImpl& other) {
        if (this != &other) {
            if (other.size() <= size()) {
                std::copy(other.cbegin(), other.cend(), begin());
                destroy_range(
                    get_begin_element() + other.size(), get_end_element());
                ArrayDataRep::set_size(other.size());
            } else if (other.size() <= capacity()) {
                auto oldSize  = size();
                auto lastCopy = other.cbegin() + oldSize;
                std::copy(other.cbegin(), lastCopy, begin());
                ArrayDataRep::set_size(other.size());
                construct_range(
                    get_begin_element() + oldSize, get_end_element(), lastCopy);
            } else {
                destroy_range(get_begin_element(), get_end_element());
                uninitialized_resize(other.size());
                construct_range(
                    get_begin_element(), get_end_element(), other.begin());
            }
        }
        return *this;
    }

    /// \copydoc Amino::Array::operator=(Array&&)
    ArrayImpl& operator=(ArrayImpl&& other) noexcept {
        // Self-assignment on a move operator is undefined behavior.
        // Caveat: std::swap(array1, array1) would perform self move assign, and
        // may arguably not be a coding error (that's debatable). To allow self
        // swapping with std::swap, the extra "get_begin_element() == nullptr"
        // is added to the assertion. The self assignment in std::swap always
        // happens after the move assignment to a temporary, which leaves the
        // array emptied (default constructed).
        assert(this != &other || get_begin_element() == nullptr);
        clear();
        swap(other);
        return *this;
    }

    /// \copydoc Amino::Array::assign(size_type,const value_type&)
    void assign(size_type count, const value_type& value) {
        auto oldEnd = get_end_element();
        if (count > capacity()) {
            destroy_range(get_begin_element(), oldEnd);
            uninitialized_resize(count);
            construct_range(get_begin_element(), get_end_element(), value);
        } else if (size() >= count) {
            ArrayDataRep::set_size(count);
            std::fill(get_begin_element(), get_end_element(), value);
            destroy_range(get_end_element(), oldEnd);
        } else {
            ArrayDataRep::set_size(count);
            std::fill(get_begin_element(), oldEnd, value);
            construct_range(oldEnd, get_end_element(), value);
        }
    }

    /// \copydoc Amino::Array::assign(InputIterator,InputIterator)
    template <
        class InputIterator,
        typename = enable_if_input_iterator_t<InputIterator>>
    void assign(InputIterator first, InputIterator last) {
        const size_type len    = std::distance(first, last);
        auto            oldEnd = get_end_element();
        if (len > capacity()) {
            destroy_range(get_begin_element(), oldEnd);
            uninitialized_resize(len);
            construct_range(get_begin_element(), get_end_element(), first);
        } else if (size() >= len) {
            ArrayDataRep::set_size(len);
            destroy_range(get_end_element(), oldEnd);
            std::copy(first, last, get_begin_element());
        } else {
            auto middle = first;
            std::advance(middle, size());
            std::copy(first, middle, begin());
            ArrayDataRep::set_size(len);
            construct_range(oldEnd, get_end_element(), middle);
        }
    }

    /*----- element accessor functions -----*/

    /// \copydoc Amino::Array::at(size_type)
    reference at(size_type n) {
        assert(n < size());
        return *get_element(n);
    }

    /// \copydoc Amino::Array::at(size_type) const
    const_reference at(size_type n) const {
        assert(n < size());
        return *get_element(n);
    }

    /// \copydoc Amino::Array::operator[](size_type)
    reference operator[](size_type n) {
        assert(n < size());
        return *get_element(n);
    }

    /// \copydoc Amino::Array::operator[](size_type) const
    const_reference operator[](size_type n) const {
        assert(n < size());
        return *get_element(n);
    }

    /// \copydoc Amino::Array::front()
    reference front() {
        assert(!empty());
        return *get_begin_element();
    }

    /// \copydoc Amino::Array::front()
    const_reference front() const {
        assert(!empty());
        return *get_begin_element();
    }

    /// \copydoc Amino::Array::back()
    reference back() {
        assert(!empty());
        return *(get_end_element() - 1);
    }

    /// \copydoc Amino::Array::back() const
    const_reference back() const {
        assert(!empty());
        return *(get_end_element() - 1);
    }

    /// \copydoc Amino::Array::data()
    /// \{
    pointer       data() noexcept { return get_begin_element(); }
    const_pointer data() const noexcept { return get_begin_element(); }
    /// \}

    /*----- iterators functions -----*/

    /// \copydoc Amino::Array::begin()
    /// \{
    iterator       begin() noexcept { return iterator{get_begin_element()}; }
    const_iterator begin() const noexcept {
        return const_iterator{get_begin_element()};
    }
    const_iterator cbegin() const noexcept {
        return const_iterator{get_begin_element()};
    }
    /// \}

    /// \copydoc Amino::Array::end()
    /// \{
    iterator       end() noexcept { return iterator{get_end_element()}; }
    const_iterator end() const noexcept {
        return const_iterator{get_end_element()};
    }
    const_iterator cend() const noexcept {
        return const_iterator{get_end_element()};
    }
    /// \}

    /*----- capacity related functions -----*/

    using ArrayDataRep::empty;

    using ArrayDataRep::size;

    /// \copydoc Amino::Array::max_size()
    size_type max_size() const noexcept { return size_type(-1); }

    /// \copydoc Amino::Array::reserve(size_type)
    void reserve(size_type new_capacity) {
        if (new_capacity > capacity()) {
            allocator_type alloc       = get_allocator_t();
            auto           oldData     = data();
            auto           oldCapacity = capacity();
            auto           oldBegin    = get_begin_element();
            auto           oldEnd      = get_end_element();
            ArrayDataRep::initialize(
                size(), new_capacity, alloc.allocate(new_capacity));
            move_range(oldBegin, oldEnd, get_begin_storage());
            destroy_range(oldBegin, oldEnd);
            alloc.deallocate(oldData, oldCapacity);
        }
    }

    using ArrayDataRep::capacity;

    /// \copydoc Amino::Array::shrink_to_fit()
    void shrink_to_fit() noexcept {
        if (capacity() > size()) {
            allocator_type alloc       = get_allocator_t();
            auto           oldData     = data();
            auto           oldCapacity = capacity();
            auto           oldBegin    = get_begin_element();
            auto           oldEnd      = get_end_element();
            ArrayDataRep::initialize(
                size(), size(), empty() ? nullptr : alloc.allocate(size()));
            move_range(oldBegin, oldEnd, get_begin_storage());
            destroy_range(oldBegin, oldEnd);
            alloc.deallocate(oldData, oldCapacity);
        }
    }

    /*----- modifier functions -----*/

    /// \copydoc Amino::Array::clear()
    void clear() noexcept {
        destroy_range(get_begin_element(), get_end_element());
        ArrayDataRep::set_size(0);
    }

    /// Same as Array::insert(const_iterator, const value_type&)
    iterator insert(const_iterator pos, const value_type& value) {
        return insert(pos, 1, value);
    }

    /// Same as Amino::Array::insert(Array::const_iterator,value_type&&)
    iterator insert(const_iterator pos, value_type&& value) {
        allocator_type alloc = get_allocator_t();
        assert(pos >= cbegin() && pos <= cend());
        const size_type n    = pos - cbegin();
        auto            nPos = get_element(n);
        if (capacity() != size()) {
            auto endPos = get_end_element();
            if (nPos != endPos) {
                // Move old end to uninitialized memory past end:
                auto back = endPos - 1;
                alloc.construct(endPos, std::move(*back));
                std::move_backward(nPos, back, endPos);
                *nPos = std::move(value);
            } else {
                alloc.construct(nPos, std::move(value));
            }
            ArrayDataRep::set_size(size() + 1);
        } else {
            auto oldData     = data();
            auto oldCapacity = capacity();
            auto oldBegin    = get_begin_element();
            auto oldEnd      = get_end_element();
            auto oldPos      = nPos;
            auto newCapacity = new_capacity(1);
            ArrayDataRep::initialize(
                size() + 1, newCapacity, alloc.allocate(newCapacity));
            nPos = get_element(n);
            move_range(oldBegin, oldPos, get_begin_element());
            move_range(oldPos, oldEnd, nPos + 1);
            alloc.construct(nPos, std::move(value));
            destroy_range(oldBegin, oldEnd);
            alloc.deallocate(oldData, oldCapacity);
        }
        return iterator(nPos);
    }

    // clang-format off
    /// \copydoc Amino::Array::insert(const_iterator,size_type,const value_type&)
    // clang-format on
    iterator insert(
        const_iterator pos, size_type count, const value_type& value) {
        allocator_type alloc = get_allocator_t();
        assert(pos >= cbegin() && pos <= cend());
        const size_type n    = pos - cbegin();
        auto            nPos = get_element(n);
        if (capacity() - size() >= count) {
            // Preserve value if it comes from the inside
            auto end = get_end_element();
            if (nPos == end) {
                construct_range(end, end + count, value);
            } else {
                auto value_ptr = &value;
                if (nPos <= value_ptr && value_ptr < end) value_ptr += count;
                if (size_type(end - nPos) < count) {
                    // Move tail into uninitialized memory:
                    move_range(nPos, end, nPos + count);
                    // Construct new section:
                    construct_range(
                        end, end + count - (end - nPos), *value_ptr);
                    // Fill into old section
                    std::fill(nPos, end, *value_ptr);
                } else {
                    // Move entries to uninitialized area:
                    move_range(end - count, end, end);
                    // Then move remaining initialized entries:
                    std::move_backward(nPos, end - count, end);
                    // Use fill since working on initialized memory
                    std::fill(nPos, nPos + count, *value_ptr);
                }
            }
            ArrayDataRep::set_size(size() + count);
        } else {
            auto oldData     = data();
            auto oldCapacity = capacity();
            auto oldBegin    = get_begin_element();
            auto oldEnd      = get_end_element();
            auto oldPos      = nPos;
            auto newCapacity = new_capacity(count);
            ArrayDataRep::initialize(
                size() + count, newCapacity, alloc.allocate(newCapacity));
            nPos = get_element(n);
            move_range(oldBegin, oldPos, get_begin_element());
            move_range(oldPos, oldEnd, nPos + count);
            construct_range(nPos, nPos + count, value);
            destroy_range(oldBegin, oldEnd);
            alloc.deallocate(oldData, oldCapacity);
        }
        return iterator(nPos);
    }

    // clang-format off
    /// \copydoc Amino::Array::insert(const_iterator,InputIterator,InputIterator)
    // clang-format on
    template <
        class InputIterator,
        typename = enable_if_input_iterator_t<InputIterator>>
    iterator insert(
        const_iterator pos, InputIterator first, InputIterator last) {
        allocator_type alloc = get_allocator_t();
        // assert(!(begin() <= first && first <= end()));
        // assert(!(begin() <= last && last <= end()));
        assert(pos >= cbegin() && pos <= cend());
        auto count = size_type(last - first);
        if (!count) {
            return iterator(const_cast<T*>(pos.base()));
        }
        const size_type n    = pos - cbegin();
        auto            nPos = get_element(n);
        if (capacity() - size() >= count) {
            auto end = get_end_element();
            if (nPos == end) {
                construct_range(end, end + count, first);
            } else {
                if (size_type(end - nPos) < count) {
                    // Move tail into uninitialized memory:
                    move_range(nPos, end, nPos + count);
                    auto leftSize = size_type(end - nPos);
                    auto middle   = first;
                    std::advance(middle, leftSize);
                    // Copy into old section
                    std::copy(first, middle, nPos);
                    // Construct new section:
                    construct_range(end, end + count - leftSize, middle);
                } else {
                    // Move entries to uninitialized area:
                    move_range(end - count, end, end);
                    // Then move remaining initialized entries:
                    std::move_backward(nPos, end - count, end);
                    // Use fill since working on initialized memory
                    std::copy(first, last, nPos);
                }
            }
            ArrayDataRep::set_size(size() + count);
        } else {
            auto oldData     = data();
            auto oldCapacity = capacity();
            auto oldBegin    = get_begin_element();
            auto oldEnd      = get_end_element();
            auto oldPos      = nPos;
            auto newCapacity = new_capacity(count);
            ArrayDataRep::initialize(
                size() + count, newCapacity, alloc.allocate(newCapacity));
            nPos = get_element(n);
            move_range(oldBegin, oldPos, get_begin_element());
            move_range(oldPos, oldEnd, nPos + count);
            construct_range(nPos, nPos + count, first);
            destroy_range(oldBegin, oldEnd);
            alloc.deallocate(oldData, oldCapacity);
        }
        return iterator(nPos);
    }

    // emplace ?

    /// \copydoc Amino::Array::erase(const_iterator)
    iterator erase(const_iterator pos) {
        assert(pos >= cbegin() && pos < cend());
        auto nPos = get_element(pos - cbegin());
        std::move(nPos + 1, get_end_element(), nPos);
        // destroy at end after move
        get_allocator_t().destroy(get_element(size() - 1));
        ArrayDataRep::set_size(size() - 1);
        return iterator(nPos);
    }

    /// \copydoc Amino::Array::erase(const_iterator,const_iterator)
    iterator erase(const_iterator first, const_iterator last) {
        assert(first >= cbegin() && first <= cend());
        assert(last >= cbegin() && last <= cend());
        assert(first <= last);
        auto firstPos       = get_element(first - cbegin());
        auto lastPos        = get_element(last - cbegin());
        auto soon_to_be_end = std::move(lastPos, get_end_storage(), firstPos);
        // destroy at end after move
        destroy_range(soon_to_be_end, get_end_storage());
        ArrayDataRep::set_size(size() - (last - first));
        return iterator(firstPos);
    }

    /// \copydoc Amino::Array::push_back(const value_type&)
    void push_back(const value_type& value) {
        auto addr = push_back_uninitialized();
        get_allocator_t().construct(addr, value);
    }

    /// \copydoc Amino::Array::push_back(value_type&&)
    void push_back(value_type&& value) {
        auto addr = push_back_uninitialized();
        get_allocator_t().construct(addr, std::move(value));
    }

    /// \copydoc Amino::Array::emplace_back
    template <typename... Args>
    void emplace_back(Args&&... args) {
        auto addr = push_back_uninitialized();
        get_allocator_t().construct(addr, std::forward<Args>(args)...);
    }

    /// \copydoc Amino::Array::pop_back
    void pop_back() {
        assert(!empty());
        erase(end() - 1);
    }

    /// \copydoc Amino::Array::resize(size_type)
    void resize(size_type count) {
        if (count > size()) {
            uninitialized_append(count - size());
        } else if (count < size()) {
            erase(cbegin() + count, cend());
        }
    }

    /// \copydoc Amino::Array::resize(size_type,const value_type&)
    void resize(size_type count, const value_type& value) {
        if (count > size())
            resize_grow(count, value);
        else if (count < size())
            resize_shrink(count);
    }

    /// \copydoc Amino::Array::swap(Array&)
    void swap(ArrayImpl& other) noexcept { ArrayDataRep::raw_swap(other); }

private:
    /// \brief Get the given pointer as a pointer to the array element type.
    ///
    /// \param ptr The generic pointer.
    ///
    /// \return The \a value_type pointer.
    static pointer as_pointer_type(void* ptr) {
        return static_cast<pointer>(ptr);
    }

    /// \brief Get the given constant pointer as a constant pointer to the array
    /// element type.
    ///
    /// \param ptr The generic constant pointer.
    ///
    /// \return The \p value_type constant pointer.
    static const_pointer as_pointer_type(const void* ptr) {
        return static_cast<const_pointer>(ptr);
    }

    /// \brief Get a pointer to the element at position \p n.
    ///
    /// \param n The index of the element.
    ///
    /// \return The pointer to the element with index \p n.
    pointer get_element(size_type n) const { return get_begin_element() + n; }

    /// \brief Get a pointer to the first element.
    ///
    /// \return The pointer to the first element.
    pointer get_begin_element() const {
        return as_pointer_type(ArrayDataRep::get_head());
    }

    /// \brief Get a pointer to the past-the-end element.
    ///
    /// \return The pointer to the past-the-end element.
    pointer get_end_element() const { return get_begin_element() + size(); }

    /// \brief Get a pointer to the first uninitialized element.
    ///
    /// \return The pointer to the first uninitialized element.
    mutable_value_type* get_begin_storage() const {
        return const_cast<mutable_value_type*>(get_begin_element());
    }

    /// \brief Get a pointer to the past-the-end uninitialized element.
    ///
    /// \return The pointer to the past-the-end uninitialized element.
    mutable_value_type* get_end_storage() const {
        return const_cast<mutable_value_type*>(get_end_element());
    }

    /// \brief Get a pointer to the uninitialized element at position \p n.
    ///
    /// \param n The index of the element.
    ///
    /// \return The pointer to the element with index \p n.
    mutable_value_type* get_storage(size_type n) const {
        return const_cast<mutable_value_type*>(get_element(n));
    }

    /// \brief Implementation of \ref resize, when the array grows in size
    void resize_grow(size_type count, const value_type& value) {
        assert(count > size());
        uninitialized_append(count - size(), value);
    }

    /// \brief Implementation of \ref resize, when the array shrinks in size
    void resize_shrink(size_type count) {
        assert(count < size());
        erase(cbegin() + count, cend());
    }

    /// \brief Destroy a range
    void destroy_range(pointer it, pointer end) {
        allocator_type alloc = get_allocator_t();
        while (it != end) alloc.destroy(it++);
    }

    /// \brief Construct a range by copying a single value
    void construct_range(
        mutable_value_type* it,
        mutable_value_type* end,
        const value_type&   value) {
        allocator_type alloc = get_allocator_t();
        while (it != end) alloc.construct(it++, value);
    }

    /// \brief Construct a range by copying from input iterator
    template <
        class InputIterator,
        typename = enable_if_input_iterator_t<InputIterator>>
    void construct_range(
        mutable_value_type* it, mutable_value_type* end, InputIterator values) {
        allocator_type alloc = get_allocator_t();
        while (it != end) alloc.construct(it++, *values++);
    }

    /// \brief Construct a range by moving values from another equally sized
    /// range. To be used when the destination overlaps the source, but the
    /// first element of destination does not.
    void move_range(
        pointer first, pointer last, mutable_value_type* destBegin) {
        allocator_type alloc = get_allocator_t();
        while (first != last) alloc.construct(destBegin++, std::move(*first++));
    }

    /// \brief Makes sure capacity is large enough. Assumes all entries are
    /// currently uninitialized.
    void uninitialized_resize(size_type newSize) {
        assert(newSize > capacity());
        allocator_type alloc = get_allocator_t();
        alloc.deallocate(data(), capacity());
        ArrayDataRep::initialize(newSize, newSize, alloc.allocate(newSize));
    }

    /// \brief Appends count default initialized entries at the end of the
    /// container
    void uninitialized_append(size_type count) {
        assert(count);
        if (capacity() - size() < count) {
            reserve(new_capacity(count));
        }
        auto itNewRange = get_end_storage();
        ArrayDataRep::set_size(size() + count);
        auto           newEnd = get_end_storage();
        allocator_type alloc  = get_allocator_t();
        while (itNewRange != newEnd) alloc.construct(itNewRange++);
    }

    /// \brief Appends count copies of value at the end of the container
    ///
    /// \note Does not create a temporary since \p value is fixed.
    void uninitialized_append(size_type count, const value_type& value) {
        assert(count);
        if (capacity() - size() < count) {
            reserve(new_capacity(count));
        }
        auto itNewRange = get_end_storage();
        ArrayDataRep::set_size(size() + count);
        auto           newEnd = get_end_storage();
        allocator_type alloc  = get_allocator_t();
        while (itNewRange != newEnd) alloc.construct(itNewRange++, value);
    }

    /// \brief push back an uninitialized element and returns a pointer to that
    /// element.
    ///
    /// Used by push_back and emplace_back.
    mutable_value_type* push_back_uninitialized() {
        allocator_type alloc  = get_allocator_t();
        size_t         n      = size();
        auto           oldEnd = get_end_storage();
        if (capacity() != n) {
            ArrayDataRep::set_size(size() + 1);
            return oldEnd;
        }
        auto oldData     = data();
        auto oldCapacity = capacity();
        auto oldBegin    = get_begin_storage();
        auto newCapacity = new_capacity(1);
        ArrayDataRep::initialize(
            n + 1, newCapacity, alloc.allocate(newCapacity));
        move_range(oldBegin, oldEnd, get_begin_storage());
        destroy_range(oldBegin, oldEnd);
        alloc.deallocate(oldData, oldCapacity);
        return get_storage(n);
    }

    void assign_uninitialized(value_type const* values) {
        construct_range(get_begin_storage(), get_end_storage(), values);
    }

    /// \brief Algorithm to find new capacity when appending \p count elements
    size_type new_capacity(size_type count) {
        // Doubling, unless count is larger than current capacity:
        return capacity() + std::max(capacity(), count);
        // We also have the option of 50% increase if doubling is deemed too
        // wasteful.
    }

private:
    constexpr allocator_type get_allocator_t() const noexcept {
        assert(isCompatible_toDeprecate(allocator_type()));
        return allocator_type();
    }
};

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

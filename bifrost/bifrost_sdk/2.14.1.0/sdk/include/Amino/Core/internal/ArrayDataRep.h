//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

#ifndef AMINO_INTERNAL_ARRAY_DATA_REP_H
#define AMINO_INTERNAL_ARRAY_DATA_REP_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  ArrayDataRep.h
/// \brief Internal representation of Amino::Array
/// \see   Amino::Internal::ArrayImpl

// The list of include files should be kept as lean as possible to keep the
// Math bitcode files small.

#include "UntypedTypeRep.h"

#include <cassert>
#include <cstddef>
#include <utility>

namespace Amino {
namespace Internal {

//==============================================================================
// FORWARD DECLARATIONS
//==============================================================================

class UntypedArray;

//==============================================================================
// CLASS ArrayDataRep
//==============================================================================

/// \brief Base untyped representation of an array of fixed size
class ArrayDataRep {
public:
    /*----- types -----*/

    /// \brief A signed integral type. Usually the same as \p ptrdiff_t.
    using difference_type = ptrdiff_t;

    /// \brief An unsigned integral that can represent any non-negative value
    ///        of \p difference_type. Usually the same as \p size_t.
    using size_type = size_t;

    /*----- member functions -----*/

    /// \brief ArrayDataRep is not copy/move constructible/assignable
    ///
    /// Only concrete derived implementation classes should implement these
    /// operations.
    /// \{
    ArrayDataRep(const ArrayDataRep&)            = delete;
    ArrayDataRep(ArrayDataRep&& o) noexcept      = delete;
    ArrayDataRep& operator=(const ArrayDataRep&) = delete;
    ArrayDataRep& operator=(ArrayDataRep&&)      = delete;
    /// \}

    /// \copydoc Array::empty()
    bool empty() const noexcept { return (m_size == 0); }

    /// \copydoc Array::size()
    size_type size() const noexcept { return m_size; }

    /// \copydoc Amino::Array::capacity()
    size_type capacity() const noexcept { return m_capacity; }

    /// \todo BIFROST-8723 This compatibility check is good but insufficient.
    bool isCompatible_toDeprecate(UntypedTypeRep const& rhs) const noexcept {
        auto const& lhs = m_elemRep;
        return lhs.get_sizeof() == rhs.get_sizeof() &&
               lhs.get_alignof() == rhs.get_alignof();
    }

protected:
    /*----- member functions -----*/

    /// \brief Construct an empty ArrayDataRep with the given allocator and
    /// virtual handler.
    constexpr explicit ArrayDataRep(UntypedTypeRep const& elemRep) noexcept
        : m_elemRep(elemRep) {
        assert(m_elemRep.get_sizeof() > 0);
    }

    /// \brief Construct an empty ArrayDataRep with the given allocator and
    /// virtual handler and allocates memory for the given number of elements.
    ///
    /// \warning The memory is NOT initialized. The concrete derived
    /// implementation class must initialize it.
    ArrayDataRep(UntypedTypeRep const& elemRep, size_type size) noexcept
        : ArrayDataRep(elemRep) {
        if (size != 0) initialize(size, size, m_elemRep.allocate(size));
    }

    /// \copydoc Amino::Array::~Array()
    ~ArrayDataRep() noexcept { deallocate(); }

    /// \copydoc Array::swap()
    void raw_swap(ArrayDataRep& other) noexcept {
        std::swap(m_array, other.m_array);
        std::swap(m_size, other.m_size);
        std::swap(m_capacity, other.m_capacity);
        std::swap(m_elemRep, other.m_elemRep);
    }

    /// \brief Initialize the precomputed member variables.
    void initialize(size_type n, size_type c, void* array) {
        m_size     = n;
        m_capacity = c;
        m_array    = array;
    }

    /// \brief Get raw a pointer to the first element.
    /// \return The raw pointer to the first element.
    void* get_head() const { return m_array; }

    /// \brief Sets the array size.
    void set_size(size_type newSize) { m_size = newSize; }

    /// \brief Deallocates the array's memory.
    ///
    /// \pre The array must be empty (all elements must have been destroyed
    /// already)
    void deallocate() {
        assert(size() == 0); // elements should have been destroyed
        assert((capacity() == 0) == (m_array == nullptr));
        if (m_array) m_elemRep.deallocate(m_array, capacity());
        initialize(0, 0, nullptr);
    }

private:
    friend UntypedArray;

    /*----- data members -----*/

    /// \brief Pointer to the start of the memory allocated for the array
    /// elements.
    void* m_array = nullptr;

    /// \brief The number of elements in the array.
    size_type m_size = 0;

    /// \brief The capacity of the array
    size_type m_capacity = 0;

    /// \brief The untyped data rep used by an allocator to create and delete
    /// the array of elements.
    UntypedTypeRep m_elemRep;
};

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

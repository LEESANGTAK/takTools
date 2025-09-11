//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef INDEX_SET_H
#define INDEX_SET_H

#include "IndexSetExport.h"

#include <Amino/Core/ArrayFwd.h>
#include <Amino/Core/BuiltInTypes.h>
#include <Amino/Core/PtrFwd.h>

#include <Amino/Cpp/Annotate.h>
#include <Amino/Cpp/ClassDeclare.h>

#include <set>

namespace Examples {
namespace SDK {

using ArrayLong = Amino::Array<Amino::long_t>;
using MutableArrayLong = Amino::MutablePtr<ArrayLong>;

//==============================================================================
// CLASS IndexSet
//==============================================================================

class AMINO_ANNOTATE("Amino::Class") INDEX_SET_DECL IndexSet {
public:
    /// \brief Default constructor.
    /// The default constructor is mandatory.
    /// This is what's used by the entry point provided by the macro
    /// AMINO_DECLARE_DEFAULT_CLASS is using the return a default value for this
    /// IndexSet type.
    IndexSet() = default;

    /// \brief Copy constructor.
    /// The copy constructor is mandatory.
    /// This will be called everytime an IndexSet needs to be mutated in-place
    /// but the reference count of the Amino::Ptr managing it is greater than
    /// one.
    IndexSet(IndexSet const& other) = default;

    /// \brief Destructor.
    ~IndexSet() = default;

    /// \brief Access the underlying std::set.
    ///
    /// Notice that constness is propagated to the member. This is VERY
    /// important to have value semantics compliant types / persistent data
    /// structure.
    ///
    /// In this case, it can't be violated (without const_cast (which would be
    /// wrong)), but in some cases it could, but it must not!
    ///
    /// For example, if the std::set was rather wrapped in a std::unique_ptr,
    /// then all access to the pointee (the std::set) would not be const! That's
    /// because it would be the std::unique_ptr that would be const, but that
    /// wouldn't affect the constness of it's pointee. If the IndexSet is const,
    /// then the std::set MUST NOT be modified. It should not be possible to
    /// access the mutable std::set from the const IndexSet. The constness
    /// of IndexSet must always be propagated to the accessed members.
    ///
    /// Violation of value semantics will lead to undefined behavior (UB) and
    /// crashes that can be very hard to debug.
    /// \{
    std::set<Amino::long_t> const* operator->() const { return &m_set; }
    std::set<Amino::long_t>*       operator->() { return &m_set; }
    std::set<Amino::long_t> const& operator*() const { return m_set; }
    std::set<Amino::long_t>&       operator*() { return m_set; }
    /// \}

private:
    std::set<Amino::long_t> m_set;
};

//==============================================================================
// FREE FUNCTIONS
//==============================================================================

//------------------------------------------------------------------------------
//
// C++ builtin types can be returned from operators by value.
// To give them a name, use the "outName" annotation in the function annotation.
INDEX_SET_DECL
bool find_in_index_set(IndexSet const& set, Amino::long_t value)
    AMINO_ANNOTATE("Amino::Node outName=found");

//------------------------------------------------------------------------------
//
INDEX_SET_DECL void add_to_index_set(
    IndexSet& set AMINO_ANNOTATE("Amino::InOut outName=out_set"),
    Amino::long_t value) AMINO_ANNOTATE("Amino::Node");

//------------------------------------------------------------------------------
//
// Here, elements is an output only (not Amino::InOut) because we're not taking
// elements as an input to modify it, we only producing this output from the
// given IndexSet.
//
// Note that this operator is *creating* a new array each time it's called.
// If this is going to be called often, it would probably be better to have an
// "elements" Amino::Ptr<Amino::Array<long>> member in the IndexSet and return
// it instead.
INDEX_SET_DECL
void get_index_set_elements(IndexSet const& set, MutableArrayLong& elements)
    AMINO_ANNOTATE("Amino::Node");

//------------------------------------------------------------------------------
//
// Perform the union of 2 sets. Here, first is an Amino::InOut because we're
// adding the elements from the second set to the first set in-place. We give it
// the outName=union.
INDEX_SET_DECL
void union_index_set(IndexSet& first
                         AMINO_ANNOTATE("Amino::InOut outName=union"),
                     const IndexSet& second) AMINO_ANNOTATE("Amino::Node");

//------------------------------------------------------------------------------
//
// Perform the union of 2 sets where the node is associative.
///   - `associativity=VAL `      - Allows specifying the associativity of the
///                                 `Node`. Valid values are:
///                                     - LeftToRight
///                                     - RightToLeft
///                                 Fully associative operations like addition
///                                 can be either one of these, but one must be
///                                 selected so Amino knows how to unfold when
///                                 more than two connections are found on an
///                                 associative port.
INDEX_SET_DECL
void associative_union_index_set(
    IndexSet& first
        AMINO_ANNOTATE("Amino::InOut Amino::IsAssociative outName=union"),
    const IndexSet& second AMINO_ANNOTATE("Amino::Port Amino::IsAssociative"))
    AMINO_ANNOTATE("Amino::Node associativity=LeftToRight");

//------------------------------------------------------------------------------
//
// Perform the difference of 2 sets. Here, first is an Amino::InOut because
// we're removing the elements of the second set from the first set in-place. We
// give it the outName=difference.
INDEX_SET_DECL void difference_index_set(
    IndexSet& first AMINO_ANNOTATE("Amino::InOut outName=difference"),
    const IndexSet& second) AMINO_ANNOTATE("Amino::Node");

} // namespace SDK
} // namespace Examples

// Macro for generating the getDefault entry point declaration related
// to a given opaque type.
// This is necessary to allow Amino graphs to create default values for
// opaque, class types.
// See AMINO_DEFINE_DEFAULT_CLASS in IndexSet.cpp
AMINO_DECLARE_DEFAULT_CLASS(INDEX_SET_DECL, Examples::SDK::IndexSet);

#endif // INDEX_SET_H

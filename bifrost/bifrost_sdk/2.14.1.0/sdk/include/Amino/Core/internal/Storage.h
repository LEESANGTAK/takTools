//-
// =============================================================================
// Copyright 2023 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_INTERNAL_STORAGE_H
#define AMINO_INTERNAL_STORAGE_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  Storage.h
/// \brief Uninitialized storage the private data members of SDK classes
/// \see   Amino::Internal::Storage

namespace Amino {
namespace Internal {

//==============================================================================
// CLASS Storage
//==============================================================================

/// \brief Uninitialized storage the private data members of SDK classes
///
/// Provides the nested type type, which is a trivial standard-layout type
/// suitable for use as uninitialized storage for any object whose size is at
/// most a multiple of `NumPtr` pointers and with alignment requirements less
/// than the one of a pointer.
///
/// The behavior is undefined if \p NumPtr is zero.
///
/// \note The type defined by Storage<>::type can be used to create
/// uninitialized memory blocks suitable to hold the objects of given type. As
/// with any other uninitialized storage, the objects are created using
/// placement new and destroyed with explicit destructor calls.
///
/// \note The intended usage is for hiding the implementation of the data member
/// exposed in the Amino SDK. The data member of the SDK objects
///
/// \todo BIFROST-TBD - FIXME std::size_t should be used instead of
/// `decltype(sizeof(int))`. This is unfortunately not possible yet until
/// cpp2json is able to parse system header files.
template <decltype(sizeof(int)) NumPtr>
struct Storage {
    struct type {
        // Note: Using `unsigned char` for uninitialized storage to respect the
        // strict C++ aliasing rules.
        //
        // NOLINTNEXTLINE(cppcoreguidelines-avoid-c-arrays,modernize-avoid-c-arrays)
        alignas(alignof(void*)) unsigned char data[NumPtr * sizeof(void*)];
    };
};

/// \brief Helper type for \ref Storage.
template <decltype(sizeof(int)) NumPtr>
using Storage_t = typename Storage<NumPtr>::type;

} // namespace Internal
} // namespace Amino
/// \endcond

#endif // AMINO_INTERNAL_STORAGE_H

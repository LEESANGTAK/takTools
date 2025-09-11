//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file ClassDefine.h
///
/// \brief Macros used to define functions and traits about classes exposed to
/// Amino.
///
/// This should be included in the .cpp file, and its counterpart \ref
/// ClassDeclare.h should be included in the .h file.

#ifndef AMINO_CLASS_DEFINE_H_
#define AMINO_CLASS_DEFINE_H_

#include <Amino/Core/internal/DefaultClassDefine.h>

//==============================================================================
// DECLARATION FOR AMINO CLASS / OPAQUE C++ TYPES DEFAULT VALUES
//==============================================================================

/// \brief Macro for generating the getDefault entry point definition related
/// to a given opaque type.
///
/// \warning The \ref AMINO_DEFINE_DEFAULT_CLASS must be added in the .cpp file
/// (must to satisfy ODR). It must be added in the global namespace (i.e. not
/// in a namespace).
///
/// The default value created by this function will be used within Amino graphs
/// when a port of a user class type does not have a value set. It will take
/// this default value. It's important because null \ref Amino::Ptr are not
/// allowed to flow in Amino graphs.
///
/// By default, the default value for the opaque class will simply be default
/// constructed. In cases where the class type cannot be default constructed,
/// the library writer can provide the default \ref Amino::Ptr as the optional
/// second argument to the \ref AMINO_DEFINE_DEFAULT_CLASS macro. This may be
/// necessary if the class has no default constructor or if the class is pure
/// virtual. Otherwise, passing a custom \ref Amino::Ptr as the second argument
/// is almost never a good idea, and is most likely a code smell (as it's
/// purposefully not using the available default constructor to create a default
/// value), and should be avoided, unless there's a very compeling reason to do
/// so.
///
/// Example:
/// \code{.cpp}
///
/// namespace MyNs {
/// class AMINO_ANNOTATE("Amino::Class") MyClass1 {
/// public:
///     // MyClass1 is not default constructible!
///     MyClass1() = delete;
///     MyClass1(int a, int b, int c);
/// };
/// class AMINO_ANNOTATE("Amino::Class") MyClass2 {
/// public:
///     // MyClass2 is pure virtual!
///     virtual void doSomething() = 0;
///     virtual ~MyClass2();
/// };
///
/// // MyClass2Impl is a concrete implementation of MyClass2 that should be used
/// // as the default value for MyClass2.
/// class MyClass2Impl : public MyClass2 {
/// public:
///     void doSomething() override { /*...*/ }
///     ~MyClass2Impl() override;
/// };
/// }
/// AMINO_DEFINE_DEFAULT_CLASS(MyNs::MyClass1,
///     Amino::newClassPtr<MyNs::MyClass1>(1, 2, 3));
/// AMINO_DEFINE_DEFAULT_CLASS(MyNs::MyClass2,
///     Amino::newClassPtr<MyNs::MyClass2Impl>());
///
/// \endcode
///
/// This is necessary to allow Amino graphs to create default values for
/// opaque, class types.
#define AMINO_DEFINE_DEFAULT_CLASS(...) \
    AMINO_INTERNAL_DEFINE_DEFAULT_CLASS(__VA_ARGS__)

#endif

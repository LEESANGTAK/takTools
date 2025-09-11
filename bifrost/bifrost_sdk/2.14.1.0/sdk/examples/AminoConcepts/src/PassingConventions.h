//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \brief Port passing conventions in Amino.
///
/// The port passing convention determines how an argument has to be passed to
/// an operator. Not all types support the same passing conventions and not all
/// passing conventions are equivalent. This file should help the reader
/// understand which passing conventions to use for passing arguments.
///

#include "AminoConceptsExport.h"

#include "Types.h"

#include <Amino/Cpp/Annotate.h>

// Include Amino Core classes that will be used as parameter types for
// the function that will be exposed to Amino.
//
// Note that since the header file typically only *declares* the functions,
// one can use the forward declaring headers, instead of the headers defining
// the types.
#include <Amino/Core/AnyFwd.h>
#include <Amino/Core/PtrFwd.h>
#include <Amino/Core/String.h>

namespace Examples {
namespace SDK {

//------------------------------------------------------------------------------
/// \brief Artificial class used in the functions below to show examples with
/// the different passing conventions and when some conventions should be
/// preferred to others.
///
/// \note The names of the members are chosen to match the names of the input
/// parameters in the `input_passing_conventions` function. They otherwise don't
/// make sense.
class AMINO_ANNOTATE("Amino::Class") AMINO_CONCEPTS_DECL PassingConventionUser {
public:
    PassingConventionUser():
        builtin_by_value(0.0F),
        builtin_by_const_ref(0),
        enum_by_value(MyEnum::eX),
        enum_by_const_ref(MyEnum::eX),
        string_by_value(""),
        string_by_const_ref(0),
        any_by_value(0),
        any_by_value2(nullptr),
        any_by_value3(nullptr),
        any_by_const_ref(false),
        any_by_const_ref2(0.0F),
        struct_by_const_ref(),
        class_by_const_ref(0),
        class_by_ptr_value(nullptr),
        class_by_ptr_const_ref(nullptr),
        class_by_mutable_ptr_value(nullptr) {}

public:
    Amino::float_t      builtin_by_value;
    Amino::int_t        builtin_by_const_ref;
    MyEnum              enum_by_value;
    MyEnum              enum_by_const_ref;
    Amino::String       string_by_value;
    size_t              string_by_const_ref;
    Amino::Any          any_by_value;
    Amino::Ptr<MyClass> any_by_value2;
    Amino::Ptr<MyClass> any_by_value3;
    bool                any_by_const_ref;
    Amino::float_t      any_by_const_ref2;
    MyStruct            struct_by_const_ref;
    size_t              class_by_const_ref;
    Amino::Ptr<MyClass> class_by_ptr_value;
    Amino::Ptr<MyClass> class_by_ptr_const_ref;
    Amino::Ptr<MyClass> class_by_mutable_ptr_value;
};

//------------------------------------------------------------------------------
/// \brief Creates an operator that takes many input arguments to showcase
/// how the input arguments can be passed to a function to be used in an Amino
/// graph.
///
/// Many of the guidelines that apply in general in C++ for passing arguments
/// also apply in the context of passing arguments to functions exposed to
/// Amino.
///
/// Types that are managed by Amino::Ptr (Amino::Array<T> and custom classes)
/// may be passed with or without being wrapped in an Amino::Ptr. The general
/// rule is that it's better not to include the Amino::Ptr in the signature
/// if the function doesn't need to change the ownership of the value (e.g. it
/// doesn't need to move the Ptr nor copy it).
/// (Note that this rule is also true in general in C++, to know if the function
/// should take a T const&, a std::unique_ptr or a std::shared_ptr for example)
///
/// \note This function doesn't show examples that pass Amino::Arrays. That's
/// because supported passing conventions for Amino::Array are exactly the same
/// as the supported conventions for custom opaque classes. Therefore all
/// arguments that pass inputs of type `MyClass` could also pass arrays the
/// same way by replacing `MyClass` by `Amino::Array<T>`.
///
AMINO_CONCEPTS_DECL void input_passing_conventions(
    // C++ builtin types can be passed by value
    //
    // This is always the preferred convention to pass C++ builtin types.
    Amino::float_t builtin_by_value,

    // C++ builtin types can be passed by const reference
    //
    // This convention is fully supported but passing by value should be
    // preferred for C++ builtin types (see builtin_by_value).
    Amino::int_t const& builtin_by_const_ref,

    // Enums can be passed by value.
    //
    // This is always the preferred conventions for passing enums.
    MyEnum enum_by_value,

    // Enums can be passed by const reference
    //
    // This convention is fully supported but passing by value should be
    // preferred for enums (see enum_by_value).
    MyEnum const& enum_by_const_ref,

    // String can be passed by value.
    //
    // This is the preferred convention if this value is going to be stored
    // (moved) in another class or container.
    Amino::String string_by_value,

    // String can be passed by const reference.
    //
    // This is the preferred convention if the String only needs to be read but
    // not copied nor moved.
    Amino::String const& string_by_const_ref,

    // Any can be passed by value.
    //
    // This is the preferred convention if the Any is going the be stored (moved)
    // in another class or container.
    //
    // It's also a good choice if the payload need to be stolen (moved out)
    // and that there's a performance benefit from moving it out rather than
    // just copying it.
    //
    // Warning: Any is an advanced type. Most users should not need to pass or
    // return Any from their functions.
    Amino::Any any_by_value,
    Amino::Any any_by_value2,
    Amino::Any any_by_value3,

    // Any can be passed by const reference.
    //
    // This is the preferred convention if the Any will only be read and that
    // the payload don't need to be stolen from it.
    Amino::Any const& any_by_const_ref,

    // Struct inputs must always be passed by const reference.
    //
    // Amino does not support passing structs by value.
    MyStruct const& struct_by_const_ref,

    // Classes can be passed by const reference.
    //
    // This is the preferred convention if the function only needs to read
    // the class value without ever modifying it.
    MyClass const& class_by_const_ref,

    // Classes can be passed by Amino::Ptr value.
    //
    // This is the preferred convention if the value needs to be stored in
    // another class / container.
    Amino::Ptr<MyClass> class_by_ptr_value,

    // Classes can be passed by const reference to Amino::Ptr.
    //
    // This passing convention is almost never a good choice. It could be a
    // reasonable choice if the Amino::Ptr will conditionally be copied in
    // another class / container.
    Amino::Ptr<MyClass> const& class_by_ptr_const_ref,

    // Classes can be passed by Amino::MutablePtr value.
    //
    // This is a good choice if the value always need to be mutated and is going
    // to be stored in another class / container.
    //
    // If the intention is to mutate the value and return it (by moving it to an
    // output parameter), then a better option is to use an InOut port,
    // described below.
    Amino::MutablePtr<MyClass> class_by_mutable_ptr_value,

    // Output argument used to show how the input arguments are used in the
    // function that justify the passing convention that was used.
    // (See input_passing_conventions in passing_conventions.cpp).
    Amino::MutablePtr<PassingConventionUser>& output) AMINO_ANNOTATE("Amino::Node");

//------------------------------------------------------------------------------
/// \brief Creates an operator that takes many in/out arguments to showcase
/// how the in/out arguments can be passed to a function to be used in an Amino
/// graph.
///
/// In/Out passing conventions can be used when a function needs to take an
/// input value, modify it in-place, and return it. This is why it is called
/// in/out; because it's both an input and an output.
///
/// Unlike regular input and output arguments, the In/Out arguments must be
/// annotated to indicate that they're meant to be used as In/Out arguments.
/// Otherwise they would be interpreted as outputs only.
///
/// \warning The In/Out arguments that are managed by Amino::Ptr must NEVER be
/// null.
///
/// \note Not all types can be passed with the In/Out conventions. It is
/// currently only supported for Amino::String, Amino::Any, Amino::Array and
/// custom classes.
///
/// \note This function doesn't show examples that pass Amino::Arrays. That's
/// because supported passing conventions for Amino::Array are exactly the same
/// as the supported conventions for custom opaque classes. Therefore all
/// arguments that pass inputs of type `MyClass` could also pass arrays the
/// same way by replacing `MyClass` by `Amino::Array<T>`.
///
AMINO_CONCEPTS_DECL void io_passing_conventions(
    // Strings can be passed by reference and marked in/out.
    Amino::String& string_by_ref AMINO_ANNOTATE("Amino::InOut"),

    // Any can be passed by reference and marked in/out.
    Amino::Any& any_by_ref AMINO_ANNOTATE("Amino::InOut"),

    // Classes can be passed by reference.
    MyClass& class_by_ref AMINO_ANNOTATE("Amino::InOut"),

    // Classes can be passed by Amino::Ptr reference.
    Amino::Ptr<MyClass>& class_by_ptr_ref AMINO_ANNOTATE("Amino::InOut"))
    AMINO_ANNOTATE("Amino::Node");

//------------------------------------------------------------------------------
/// \brief Creates an operator that has many output arguments to showcase
/// how the output arguments can be passed to a function to be used in an Amino
/// graph.
///
/// \warning The output arguments that are managed by Amino::Ptr must NEVER be
/// null.
///
/// \note This function doesn't show examples that pass Amino::Arrays. That's
/// because supported passing conventions for Amino::Array are exactly the same
/// as the supported conventions for custom opaque classes. Therefore all
/// arguments that pass inputs of type `MyClass` could also pass arrays the
/// same way by replacing `MyClass` by `Amino::Array<T>`.
///
AMINO_CONCEPTS_DECL Amino::float_t output_passing_conventions(
    // Input argument used to show how the output arguments are used in the
    // function that justify the passing convention that was used.
    // (See output_passing_conventions in passing_conventions.cpp).
    PassingConventionUser const& input,

    // C++ builtin types can be passed by reference.
    //
    // The preferred convention for C++ builtin types is by returned value (using
    // the return keyword), but this convention can be used if the function has
    // more than one output that could be returned by value.
    Amino::float_t& builtin_by_ref,

    // Enums can be passed by reference.
    //
    // The preferred convention for enum types is by returned value (using
    // the return keyword), but this convention can be used if the function has
    // more than one output that could be returned by value.
    MyEnum& enum_by_ref,

    // String can be passed by reference.
    //
    // This is the only output convention for String.
    Amino::String& string_by_ref,

    // Any can be passed by reference.
    //
    // This is the only output convention for Any.
    Amino::Any& any_by_ref,

    // Structs can be passed by reference.
    //
    // This is the only output convention for structs.
    MyStruct& struct_by_ref,

    // Classes can be passed by Amino::Ptr reference.
    //
    // This is the preferred convention if the returned class is not a newly
    // created one (e.g. it's copied from another class / container).
    Amino::Ptr<MyClass>& class_by_ptr_ref,

    // Classes can be passed by reference to Amino::MutablePtr.
    //
    // This is the preferred convention if the returned class is a newly created
    // class.
    Amino::MutablePtr<MyClass>& class_by_mutable_ptr_ref)
    AMINO_ANNOTATE("Amino::Node outName=my_float_output");

} // namespace SDK
} // namespace Examples

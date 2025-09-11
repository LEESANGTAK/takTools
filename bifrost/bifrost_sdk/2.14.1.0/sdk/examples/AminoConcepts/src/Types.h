//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \brief Types in Amino.
///
/// This files explains what are the existing types in an Amino library and
/// how to extend it with custom types (enums, structs, classes). This file
/// should help the reader understand how to expose its custom types to Amino
/// graphs, what the requirements are and what are the differences between the
/// different kinds of types that can be exposed.
///

#include "AminoConceptsExport.h"

// The types declared in this header are all the builtin C++ types supported
// in Amino graphs.
#include <Amino/Core/BuiltInTypes.h>

// This header contains the annotation macro to use to expose new custom types
// (and functions) to Amino (AMINO_ANNOTATE).
#include <Amino/Cpp/Annotate.h>

// This header contains the macro to declare an entry function to obtain a
// default value for an opaque custom class (see MyClass below).
#include <Amino/Cpp/ClassDeclare.h>

// This header contains the "smart pointers" used to manage the lifescope and
// the write access to some types. It define the Amino::Ptr<T> and the
// Amino::MutablePtr<T> types, and some other related types and functions.
//
// WARNING: The Amino::Ptr<T> and Amino::MutablePtr<T> have some commonality
// with std::shared_ptr<T> and std::unique_ptr<T>, but also perform capture and
// type erasure and have stricter access to the object they managed. The
// Amino::Ptr<T> and Amino::MutablePtr<T> are only meant to be used when the
// objects they manage need to be exposed and flowing in an Amino graph. They
// are NOT a replacement for existing std smart pointers.
#include <Amino/Core/Ptr.h>

// This header defines the Amino::String class. It represent a string (similar
// to std::string), that can be used in Amino graphs.
//
// WARNING: The Amino::String is NOT a replacement for std::string. It is only
// meant to be used for strings that need to be used and flow in Amino graphs.
// In many regards they are less efficient than std::string because they need to
// satisfy more requirements to be used in Amino graphs.
#include <Amino/Core/String.h>

// This header defines the Amino::Any class. It represent a type-safe container
// that can hold (almost) any value (of any type) that satifies some
// constraints.
//
// WARNING: The Amino::Any is NOT a replacement for std::any. It is only meant
// to be used in Amino graphs. It has more constraints than std::any to allow
// it to be used in Amino graphs.
//
// WARNING: The Amino::Any is a very advanced type. In most cases, it shouldn't
// be needed. It always comes with more constraints and overhead than just
// passing the value it contains.
#include <Amino/Core/Any.h>

// This header defines the Amino::Array<T> container. It's a random-access
// contiguous container of elements of type T.
//
// WARNING: The Amino::Array<T> is similar to a std::vector<T> but is NOT
// a replacement for std::vector<T>. It is only meant to be used if the
// contiguous container need to be used in Amino graphs.
#include <Amino/Core/Array.h>

#include <vector>

/// \brief The namespace in which our types will be defined.
///
/// Like most langages this allows avoiding collisions in names (type names,
/// function names, variable names). They serve the same purpose when exposing
/// custom types and function to Amino.
namespace Examples {
namespace SDK {

//------------------------------------------------------------------------------
//
/// \brief Structure that contains all Amino built-in types.
///
/// By default the Amino library already contains many types. In particular,
/// it contains almost all the builtin C++ types (bool, char, short, int, long,
/// unsigned char, unsigned short, unsigned int, unsigned long, float, double).
/// It also defines a String class (the Amino::String) and a type-safe container
/// for copy-constructible types (the Amino::Any).
///
/// It's also possible to extend the types in the Amino library by annotating
/// types in C++.
///
/// All types in Amino can be stored in a random-access contiguous container;
/// the Amino::Array.
///
/// \note Unlike the other builtin types, the Amino::Array is managed by an
/// Amino::Ptr. That's because in Amino, the lifescope of arrays are managed
/// by Amino::Ptr. It is also the case for all custom opaque classes (see \ref
/// MyClass).
struct AMINO_ANNOTATE("Amino::Struct") TheAminoBuiltInTypes {
    Amino::bool_t                 m_bool;
    Amino::char_t                 m_signed_char;
    Amino::short_t                m_signed_short;
    Amino::int_t                  m_signed_int;
    Amino::long_t                 m_signed_long;
    Amino::uchar_t                m_unsigned_char;
    Amino::ushort_t               m_unsigned_short;
    Amino::uint_t                 m_unsigned_int;
    Amino::ulong_t                m_unsigned_long;
    Amino::float_t                m_float;
    Amino::double_t               m_double;
    Amino::String                 m_string;
    Amino::Any                    m_any;
    Amino::Ptr<Amino::Array<int>> m_array_of_T{Amino::PtrDefaultFlag{}};
};

//------------------------------------------------------------------------------
//
/// \brief Defines a custom enumerator to Amino.
///
/// This allows adding a new type in the Amino library called `MyEnum` in the
/// namespace `Examples::SDK`. The fully qualified name (FQN) of this new type
/// is therefore `Examples::SDK::MyEnum`. This FQN becomes a unique identifier
/// for that type.
///
/// The enum types in Amino must meet some requirements:
///  - They must not be explicitly typed, or they must be typed to int (: int).
///  - They must have an enumerator that has the value zero (that is the default
///    value for the enum).
///
/// \note They are not required to be an `enum class` rather than just an `enum`
/// but it's generally better practice to declare enums as `enum class` in
/// general.
enum class AMINO_ANNOTATE("Amino::Enum") MyEnum {
    eX, ///< Enum with value = 0
    eY, ///< Enum with value = 1
    eZ  ///< Enum with value = 2
};

//------------------------------------------------------------------------------
//
/// \brief Defines a custom structure to Amino.
///
/// This allows adding a new type in the Amino library called `MyStruct` in the
/// namespace `Examples::SDK`. The fully qualified name (FQN) of this new type
/// is therefore `Examples::SDK::MyStruct`. This FQN becomes a unique identifier
/// for that type.
///
/// Annotating a type with the "Amino::Struct" indicates that we want not only
/// to expose a new type called `Examples::SDK::MyStruct`, but also we want its
/// members to be known. In this case, this defines a struct called
/// `Examples::SDK::MyStruct` that has three members: `myEnum` of type
/// `Examples::SDK::MyEnum`, `anInt` of type `int` and aDouble of type `double`,
/// in that order.
///
/// The structure types in Amino must meet some requirements:
///  - All their members must have public visibility.
///  - They can't be templated.
///  - They must not inherit from other classes.
///  - They must not be polymorphic / have virtual table / have virtual
///    functions (pure or not).
///  - All their member types must be known to Amino (either builtin supported
///    Amino types (see \ref TheAminoBuiltInTypes) or custom types (enums,
///    structs, classes) that are also exposed to Amino.
///  - The members that have types that are managed by Amino::Ptr (Amino::Array
///    and custom opaque classes) must be managed by Amino::Ptr in the
///    structure. They must also default construct to non-null Ptr. The
///    flag `Amino::PtrDefaultFlag{}` should be used to ensure that (see
///    how it's used in \ref TheAminoBuiltInTypes above).
///  - Their default constructor must exist and default construct all its
///    members (this is the case when the default constructor is either
///    automatically defined by the compiler or if the default constructor
///    is explicitly defined in the code and defaulted (= default). (The only
///    exception to that is for Ptr members because they must default construct
///    to non-null Ptr).
///
/// They may have member functions and static member functions (as long as
/// they're not virtual). They will be ignored by the parser.
struct AMINO_ANNOTATE("Amino::Struct") MyStruct {
    MyEnum          myEnum;
    Amino::int_t    anInt;
    Amino::double_t aDouble;

    /// \brief Some member functions and static member functions.
    ///
    /// That's ok. They will be ignored by the parser.
    /// \{
    void        member_function() {}
    static void static_member_function() {}
    template <typename T>
    void templated_member_function() {}
    template <int N>
    static void templated_static_member_function() {}
    /// \}
};

//------------------------------------------------------------------------------
//
/// \brief Declares a custom opaque class to Amino.
///
/// This allows adding a new type in the Amino library called `MyClass` in the
/// namespace `Examples::SDK`. The fully qualified name (FQN) of this new type
/// is therefore `Examples::SDK::MyClass`. This FQN becomes a unique identifier
/// for that type.
///
/// Unlike Amino::Struct annotated types, Amino::Class annotated types are
/// opaque to Amino. In this case, it declares that a type
/// `Examples::SDK::MyClass` exists but nothing else, hence the adjective
/// "opaque". It doesn't expose the content of the class (the classes members,
/// member functions, etc.). This makes Amino::Class more flexible than
/// Amino::Struct. The members don't need to be public or known to Amino. The
/// class can be polymorphic or have parent classes. But also have
/// disadvantages that struct don't have. They must always be managed by
/// Amino::Ptr to be used in Amino graphs, typically resulting in more heap
/// allocations and extra indirection to get the class.
///
/// The class types exposed to Amino must meet some requirements:
///  - They must not be templated.
///  - There must exist an entry point to get a default value for that opaque
///    class (see below).
///
/// The class may be polymorphic but are not required to be. They don't need
/// to define a virtual destructor because the Amino::Ptr captures how to
/// destroy it's pointee when the Ptr/MutablePtr is constructed.
///
class AMINO_ANNOTATE("Amino::Class") AMINO_CONCEPTS_DECL MyClass {
public:
    MyClass():
        m_std_vector_int(10, 0),
        m_non_exposed_enum(NonExposedEnum::eA),
        m_unsupported_type(0.0L) {}

public:
    /// \brief A private type that is not exposed to Amino.
    enum class NonExposedEnum { eA, eB };

    /// \brief Some member functions.
    /// They will be ignored by the parser.
    /// \{
    auto        getNonExposedEnum() const { return m_non_exposed_enum; }
    auto        getUnsupportedType() const { return m_unsupported_type; }
    auto const& getStdVectorInt() const { return m_std_vector_int; }
    auto&       getStdVectorInt() { return m_std_vector_int; }
    /// \}

private:
    /// \brief Some class members.
    /// They will be ignored by the parser. They don't need to have types that
    /// are known to Amino.
    /// \{
    std::vector<int> m_std_vector_int;
    NonExposedEnum   m_non_exposed_enum;
    long double      m_unsupported_type;
    /// \}
};

} // namespace SDK
} // namespace Examples

//------------------------------------------------------------------------------
//
/// \brief Declare the entry point that Amino will call to get the default
/// value for the type `Examples::SDK::MyClass`. This is used when an input port
/// of type `Examples::SDK::MyClass` is not connected. In this case, Amino
/// will pass a default value of type `Examples::SDK::MyClass`. Since the class
/// is opaque, Amino can't know how to construct a default value of type
/// `Examples::SDK::MyClass`. This is why this function must be provided.
///
/// Note that this macro is used outside all namespaces (it's not in the
/// `Examples::SDK` namespaces. This is how this macro needs to be used.
/// It won't compile when used elsewhere than in the global namespace.
///
/// \warning This is only the *declaration* of the entry point to allow Amino
/// to create the default value for the class `Examples::SDK::MyClass`, but
/// a definition must also be provided in the source file (.cpp) otherwise
/// Amino won't be able to find the entry point (the symbol won't be in the
/// shared library so it won't be able to link to it).
AMINO_DECLARE_DEFAULT_CLASS(AMINO_CONCEPTS_DECL, Examples::SDK::MyClass);

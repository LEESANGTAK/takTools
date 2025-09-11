//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+
// clang-format off
///
/// \file  Annotate.h
/// \brief Header Parser Annotation Macro & Parser Documentation
///
/// Header Parser Annotation Documentation
/// ======================================
///
///  The Amino header parser processes one or more C++ files with the purpose
///  of extracting type and node definitions for use in Amino graphs. This
///  parser will ignore all constructs that are not specifically flagged for use
///  by Amino. The means for performing this flagging is through the use of
///  "Annotations".
///
///  The parser can be invoked from the command line like this;
///
///  \code{.cpp}
///  cpp2json -I<some_include_path> -D<some_definition> test.h -o test.json
///  \endcode
///
///  (`-I` and `-D` can each be used multiple times on the command line to add
/// multiple include directories and definitions.)
///
///  The annotations are specified using a macro called AMINO_ANNOTATE. It takes
///  a single string argument. It is only defined to have a non empty payload
///  when the Parser is processing the file, and not when the usual compiler is
///  active.
///
///  \warning On any given construct (class, struct, parameter or function
///  prototype) there should be only one `AMINO_ANNOTATE`. The annotation string
///  can contain multiple tokens.
///
///  The annotation string tokens recognized by the Amino header parser are;
///
///  -# `Amino::Node   `  - Declare a Node definition to Amino (operator)
///  -# `Amino::Class  `  - Declare an "opaque" type to Amino
///  -# `Amino::Struct `  - Declare a "native" struct to Amino
///  -# `Amino::Enum   `  - Declare an enumeration to Amino
///  -# `Amino::Port   `  - Declare port (optional)
///  -# `Amino::InOut  `  - Declare an in/out port for a Node
///  -# `Amino::Converter`   - Declare a Node a type converter
///  -# `Amino::Promoter`    - Declare a Node a type promoter
///  -# `Amino::DefaultOverload` - Declare a Node the default in an overload set
///  -# `Amino::IsAssociative`   - Declare that a port is associative
///
/// The following tokens are internally supported by Amino. They are not fully
/// supported for client code, and may be removed/modified in the future:
///
///  -# `Amino::JobPort`     - Declare job port
///  -# `Amino::Deserialize` - Declare a for serialization reading
///  -# `Amino::Serialize`   - Declare a for serialization writing
///
/// On some of these (except `Class`, `Struct`, `Deserialize` and `Serialize`)
/// additional (and optional) tags can be provided. These are:
///
///   - `name=UserNS::NewName `   - override the name, including a namespace
///                                 (namespaces are for nodes only, ports may
///                                 not have a namespace). This tag is valid on
///                                 `Port`, `InOut`, and `Node`.
///   - `outName=retValPortName ` - provide a name for the output port using the
///                                 return value slot. This tag is valid on
///                                 `Node`, and `InOut`.
///   - `associativity=VAL `      - Allows specifying the associativity of the
///                                 `Node`. Valid values are:
///                                     - LeftToRight
///                                     - RightToLeft
///                                 Fully associative operations like addition
///                                 can be either one of these, but one must be
///                                 selected so Amino knows how to unfold when
///                                 more than two connections are found on an
///                                 associative port.
///   - 'metadata={name, type, data} | [{name, type, data}, {name, type, data}]'
///                               - Support adding metadata items to node defs,
///                                 classes, structs or enums, or ports. The
///                                 'type' field will be optional. If omitted,
///                                 it will be assumed to be string.
///
///  "Amino::Class", "Amino::Struct", "Amino::Enum", "Amino::Node",
///  "Amino::Port", or "Amino::InOut" should be the first thing to appear in the
///  annotation string. Optional tags come after in any order.
///
///  Several of these optional tags can be used concurrently. For example;
///
///  \code{.cpp}
///
///  float someFunction(MyClass const& in)
///      AdskAnnotate("Amino::Node "
///                   "Amino::DefaultOverload "
///                   "name = foobar "
///                   "outName = result "
///                   "metadata=[{DocPath, ../foobarDocs.md},"
///                             "{IconPath, ../foobarIcon.png}]");
///
///  \endcode
///
///  That example would say that this `someFunction` is a node definition named
///  `foobar`. The implicit output port using the return value is named
///  `result`. This is the default overload in an overload set named `foobar`.
///  And finally, metadata provides the file paths for the documentation and
///  icon to be used in the graph editing UI.
///
///
/// `Amino::Class` Annotation
/// ==========================
///
///  This is used to declare a class as an opaque data object to Amino. The
///  annotation appears immediately after the `class` keyword in C++.
///
///  The following will declare a class for Amino called MyObject. This class
///  will be passable to nodes and through a Amino graph. It will be opaque data
///  to the graph. Through the use of `Amino::Ptr`, it will be life-scope
///  managed. (Currently the life-scope management is reference count based.)
///  \see Amino::Ptr
///
///  \code{.cpp}
///
///     #include <Amino/Cpp/Annotate.h> // for AMINO_ANNOTATE macro
///
///     class AMINO_ANNOTATE("Amino::Class") MyObject
///     {
///         public:
///             // default constructor is mandatory
///             MyObject();
///
///             // The copy constructor is mandatory
///             MyObject(MyObject const &);
///     };
///
///  \endcode
///
///  The `Amino::Class` annotation must appear immediately after the `class`
///  keyword. Intervening `dll_export` or other keywords cannot appear between
///  `class` and `AMINO_ANNOTATE`.
///
///  Amino classes must also provide a function to return a default constructed
///  value for that type. See \ref ClassDeclare.h and \ref ClassDefine.h.
///
/// `Amino::Struct` Annotation
/// ============================
///
///  This annotation exposes a "native struct" to the Amino graph. It comes
///  immediately after the `struct` keyword.
///
///  Native structs expose their members to the Amino graph (unlike
///  Classes). No member functions or inheritance or other new "C++" features
///  are allowed (the parser will report an error if these rules are violated.).
///  The member can be of any type known or exposed to Amino.
///
///  \warning If a member is an opaque class (annotated with "Amino::Class"),
///  then this member must be managed by an \ref Amino::Ptr. Struct with
///  \ref Amino::Ptr members must be used very carefully within C++ operators
///  as their \ref Amino::Ptr members must never be null when returned from
///  operators.
///
///  For example;
///  \code{.cpp}
///
///     #include <Amino/Cpp/Annotate.h> // for AMINO_ANNOTATE macro
///
///     struct AMINO_ANNOTATE("Amino::Struct") float4
///     {
///         float x, y, z, w;
///     };
///
///  \endcode
///
///  As with `Amino::Class` this must appear right next to the struct
///  keyword, with no other intervening tokens.
///
///
/// `Amino::Enum` Annotation
/// ============================
///
///  This annotation exposes a "native enumeration" to the Amino graph. It comes
///  immediately after the `enum` keyword.
///
///  This annotation can only be used on standard enums -- enum classes are not
///  allowed (the parser will report an error if these rules are violated).
///
///  For example;
///  \code{.cpp}
///
///     #include <Amino/Cpp/Annotate.h> // for AMINO_ANNOTATE macro
///
///     enum AMINO_ANNOTATE("Amino::Enum") Color
///     {
///         eRED,
///         eGREEN,
///         eBLUE
///     };
///
///  \endcode
///
///  As with `Amino::Class` this must appear right next to the enum
///  keyword, with no other intervening tokens.
///
///  \warning Explicitly typed enums are not (yet) supported. eg;
///  \code{.cpp}
///
///     #include <Amino/Cpp/Annotate.h> // for AMINO_ANNOTATE macro
///
///     enum AMINO_ANNOTATE("Amino::Enum") Color : unsigned char
///     { eRED, eGREEN, eBLUE };
///  \endcode
///
///
/// Type restrictions
/// =================
///
///  As the Amino type system does not support parameterized (templated) types,
///  Amino types in C++ (annotated with "Amino::Class", or "Amino::Struct") must
///  not be template types themselves. It is, however, acceptable for them to
///  derive from templated base classes (if they are fully specialized), or to
///  contain members who are templated classes. But the class or struct itself
///  that is annotated with the Amino tags may not have any template parameters
///  (that is be templated directly) themselves, either fully specialized,
///  partially specialized or unspecialized.
///
///  The only exceptions to this rule is the "built-in" template type
///  \ref Amino::Array. This container is fully known by Amino.
///
///
/// `Amino::Node` Annotation
/// ==========================
///
///  This annotation declares a node (also known as a function or operator) to
///  Amino. This is used on function prototype statements in C++. It is placed
///  at the end of the C++ prototype statement, just before the terminating `;`.
///
///  For example;
///
///  \code{.cpp}
///  float add(float a, float b) Adsk_Annotate("Amino::Node outName=result");
///  \endcode
///
///  This declares a node definition called `add` with two input ports of type
///  float named `a` and `b`, and a single output port of type float named
///  `result`.
///
///  There are a number of rules for specifying nodes and ports. The biggest
///  part to understand is how the parser tells input ports from output ports
///  from in/out ports.
///
///  Input ports are parameters which are passed by value (or by \ref Amino::Ptr
///  value) and by const reference (or const reference to an \ref Amino::Ptr)
///
///  Output ports are all non-const references or returned by value (using the
///  c++ `return` keyword).
///
///  In/Out ports are also non-const references, but must be annotated with
///  `Amino::InOut` (otherwise the parser has no way of differentiating them
///  from output ports).
///
///  There is an additional constraint on the ordering of the ports. The
///  ordering currently *must* follow the following pattern;
///
///  - Input or In/Out ports come first
///  - Output ports.
///
///  \note this ordering constraint may be relaxed in future
///
///  Lets look another example;
///
///  \code{.cpp}
///     void floatToMultiFloats(float f, float& out1, float& out2)
///         AMINO_ANNOTATE("Amino::Node");
///  \endcode
///
///  This declares a node called `floatToMultiFloats` with 1 input port called
///  `f` and two output ports called `out1` and `out2`. The Amino parser
///  recognizes the output ports as such because they are non const references.
///
///  Nodes can optionally be declared as type converters or promoters. (Using
///  the `Amino::IsConverter` or `Amino::IsPromoter` tokens in the annotation
///  string after the `Amino::Node` token. (these tokens are separated by
///  spaces) Converters are available to to user to suggest type conversions
///  where types mismatch. Promoters can be automatically inserted by the Amino
///  compiler to resolve type mismatches. You can only specify one of these two
///  optional flags.
///
///  One node in an overload set can also be declared as the "default". This has
///  no semantic meaning -- it is a convenience for the UI to use when the
///  ports have not yet been connected and the system cannot yet determine
///  which overload of an overload set to use. This is done using the
///  `Amino::DefaultOverload` token after the `Amino::Node` token.
///
/// `Amino::InOut` Annotation
/// ===========================
///
///  This is used to mark a node port as an In/Out port. It comes immediately
///  after the argument name in the parameter list of a C++ prototype
///  statement.
///
///  For example;
///
///  \code{.cpp}
///     void floatToMultiFloats(float f,
///                             MyClass& inOut AMINO_ANNOTATE("Amino::InOut"),
///                             float& out2)   AMINO_ANNOTATE("Amino::Node");
///  \endcode
///
///  This declares a node with 1 input port, one in/out port, and 1 output
///  port. (Some types don't support In/Out conventions. See the
///  "Port Passing Conventions" below.)
///
///
/// `Amino::Port` Annotation
/// ==========================
///
///  The `Amino::Port` annotation is always optional. Its only purpose is to
///  allow renaming of ports or attaching metadata to it. It comes immediately
///  after an argument name in the parameter list of a C++ prototype statement
///  that has been annotated with `Amino::Node`.
///
///  For example;
///
///  \code{.cpp}
///     float floatToFloat(float f AMINO_ANNOTATE("Amino::Port name=inputFloat"))
///                 AMINO_ANNOTATE("Amino::Node outName=floatResult");
///  \endcode
///
///  This creates a Node with a single input port named `inputFloat`, and a
///  single output port named `floatResult`. In the absence of this annotation,
///  the input port would have been named `f`.
///
///
/// `Amino::JobPort` Annotation
/// =============================
///
///  The `Amino::JobPort` annotation comes immediately after an argument name in
///  the parameter list of a C++ prototype statement that has been annotated
///  with `Amino::Node`. It allow declaring ports that behave as global
///  constants for a job. All similarly named job ports will be initialized with
///  the same immutable constant value. Job ports are not connectable.
///
/// \warning This is mostly used internally. It can be used to pass
/// \ref Amino::RuntimeServices but it is preferable to avoid using this
/// otherwise, as it may change in the future.
///
/// \note RuntimeServices are implicitly job ports, and therefore the annotation
/// is optional when using RuntimeServices.
///
///  For example;
///
///  \code{.cpp}
///     float updatePosition(
///         float position,
///         float velocity,
///         float timestep AMINO_ANNOTATE("Amino::JobPort")
///     ) AMINO_ANNOTATE("Amino::Node");
///
///     float floatToFloatWithRuntimeLogging(
///         float input,
///         const Amino::RuntimeServices& rs // implicitly a JobPort
///     ) AMINO_ANNOTATE("Amino::Node outName=floatResult");
///  \endcode
///
///  This creates a Node with a single input port named `input` and a single
///  output port named `floatResult`, and a RuntimeServices job port.
///
///
/// Port Passing Conventions
/// ========================
///
///  For each type of data, there are one or more ways of expressing input,
///  output and in/out ports.
///
///
///  | %Kind     | %Type   | Passing Convention            | Example of C++ Signature                         |
///  |-----------|---------|-------------------------------|--------------------------------------------------|
///  | Input/Job | Native  | PassedByValue                 | `int      op(float                        port)` |
///  | Input/Job | Native  | PassedByReference             | `int      op(float                 const& port)` |
///  | Input/Job | Enum    | PassedByValue                 | `int      op(MyEnum                       port)` |
///  | Input/Job | Enum    | PassedByReference             | `int      op(MyEnum                const& port)` |
///  | Input/Job | Struct  | PassedByReference             | `int      op(MyStruct              const& port)` |
///  | Input/Job | Any     | PassedByValue                 | `int      op(Any                          port)` |
///  | Input/Job | Any     | PassedByReference             | `int      op(Any                   const& port)` |
///  | Input/Job | Class   | PassedByValue                 | `int      op(MyClass               const& port)` |
///  | Input/Job | Class   | PassedByPtrValue              | `int      op(Amino::Ptr<MyClass>          port)` |
///  | Input     | Class   | PassedByMutablePtrValue       | `int      op(Amino::MutablePtr<MyClass>   port)` |
///  | Input/Job | Class   | PassedByReferenceToPtr        | `int      op(Amino::Ptr<MyClass>   const& port)` |
///  | Input/Job | String  | PassedByReferenceToPtr        | `int      op(Amino::String         const& port)` |
///  |           |         |                               |                                                  |
///  | Output    | Native  | ReturnedByValue               | `float    op()`                                  |
///  | Output    | Native  | PassedByReference             | `void     op(float                      & port)` |
///  | Output    | Enum    | ReturnedByValue               | `MyEnum   op()`                                  |
///  | Output    | Enum    | PassedByReference             | `void     op(MyEnum                     & port)` |
///  | Output    | Struct  | PassedByReference             | `void     op(MyStruct                   & port)` |
///  | Output    | Any     | PassedByReference             | `void     op(Any                        & port)` |
///  | Output    | Class   | PassedByReferenceToPtr        | `void     op(Amino::Ptr<MyClass>        & port)` |
///  | Output    | Class   | PassedByReferenceToMutablePtr | `void     op(Amino::MutablePtr<MyClass> & port)` |
///  | Output    | String  | PassedByReferenceToPtr        | `void     op(Amino::String              & port)` |
///  |           |         |                               |                                                  |
///  | In/Out    | Any     | PassedByReference             | `void     op(Amino::Any                 & port)` |
///  | In/Out    | Class   | PassedByValue                 | `void     op(MyClass                    & port)` |
///  | In/Out    | Class   | PassedByReferenceToPtr        | `void     op(Amino::Ptr<MyClass>        & port)` |
///  | In/Out    | String  | PassedByReferenceToPtr        | `void     op(Amino::String              & port)` |
///
///  \note Passing conventions for \ref Amino::Array are the same as the ones
///  for classes ("Amino::Class").
///
///  All types used in the function signatures must be known to Amino. They
///  must therefore either be builtin types (see \ref BuiltInTypes.h),
///  annotated structs ("Amino::Struct"), annotated classes ("Amino::Class"),
///  annotated enums ("Amino::Enum") or \ref Amino::Array<T> where the template
///  type is known to Amino. Classes must always be managed with
///  \ref Amino::Ptr.
///
///
/// Using Namespaces
/// ================
///
///  The parser is fully aware of C++ namespaces, and uses them when creating
///  the names seen in the Amino graph for types and nodes. The name with its
///  namespace can always be overridden using the `name=` modifier on the Node
///  tag. (There is no name override facility for Classes or Structs)
///
///  In the following example,
///  \code{.cpp}
///
///     #include <Amino/Cpp/Annotate.h> // for AMINO_ANNOTATE macro
///
///     namespace UserNS {
///     class AMINO_ANNOTATE("Amino::Class") MyObject
///     {
///         public:
///             // default constructor is mandatory
///             MyObject();
///
///             // The copy constructor is mandatory
///             MyObject(MyObject const &);
///     };
///
///
///     float add(float a, float b) Adsk_Annotate("Amino::Node outName=result")
///     float add2(float a, float b)
///         Adsk_Annotate("Amino::Node name=OtherNs::myName outName=result")
///
///     } // end UserNS;
///  \endcode
///
///  Will create a class definition called `UserNS::MyObject`, and a node
///  definition called `UserNS::add`, and a second one called `OtherNs::myName`.
///
///
/// Using typedefs or macros
/// ========================
///
///  The parser will see past all typedefs to the final root (non-typedef'd)
///  type. Similarly, all macro expansion will have been performed before the
///  parser executes.
///
///  So neither typedefs nor macros can hide types from Amino.
///
///
///  Serialize & Deserialize
///  --------------------------------
///
///  Two methods may be implemented to support serialization on a user
///  defined class. This is necessary only if non-default values of such types
///  may be set as node inputs in an Amino graph.
///
///  \warning Only used internally for now (SerializationData is not public).
///
///   \code{.cpp}
///       bool deserialize(
///           const Amino::SerializationData& input,
///           Amino::Ptr<MyClass>&            output
///       ) AMINO_ANNOTATE("Amino::Deserialize");
///
///       bool serialize(
///           MyClass const&            input,
///           Amino::SerializationData& output
///       ) AMINO_ANNOTATE("Amino::Serialize");
///   \endcode
///
///
/// General Notes on C++ Data Types
/// ===============================
///
///  The native types supported by Amino can be found in \ref BuiltInTypes.h.
///  It is recommended to use Amino's type aliases to avoid type missuses.
///  In particular `long` and `unsigned long` are not supported because their
///  size is platform dependent (32 or 64 bits). Also `char` isn't supported
///  since it is also platform dependent (can be either signed or unsigned).
///
///
/// Metadata Annotation
/// ===================
///
///  Metadata can optionally be added to Nodes, Classes, Structs, Enums and
///  Ports. (After Amino::Node, Amino::Class, Amino::Struct, Amino::Enum,
///  Amino::Port, or Amino::InOut in an annotation string.)
///
///  \note Individual struct and enum members do not currently support metadata.
///
///  The metadata is an additional and optional tag on an annotation string in
///  the form;
///
///  \code
///   metadata = {metaName, type, contents}
///  \endcode
///
///  or leaving off the type field (it will default to "string");
///
///  \code
///   metadata = {metaName, contents}
///  \endcode
///
///  Arrays of multiple metadata items may be specified by using the square
///  brackets [ ], with the metadata items in a comma separated list between
///  them;
///
///  \code
///   metadata = [{metaName, contents}, {metaName2, contents2}]
///  \endcode
///
///  Any characters can be part of the metadata, but special characters used by
///  the parser to parse metadata will have to be "escaped". If you want "=",
///  "\", "[", "]", "{", "}" or "," you will have to escape them using the
///  escape sequence "\\". So for a "}" in the metadata, you would use "\\}".
///  For example;
///
///  \code
///   metadata = {metaName, float3, \\{1.0\\, 2.0\\, 3.0\\} }
///  \endcode
///
///  \warning There should not be more than one "metadata =" tag on a given
///  annotation. Instead the value of metadata should be specified as an array.
///
///  \note That the metadata name field and contents field can contain spaces,
///  commas, or any printable characters (some may need to be escaped - in
///  particular characters in the set "=\[]{}," must be escaped.).
///
///  Metadata has no semantic content for Amino -- it will never alter the
///  results of graph computation. It can be used to pass information to the UI
///  such as documentation paths, a color, an icon, a shape, port grouping, a
///  tool-tip string and so on. The metadata gathered by the C++ parser will be
///  serialized to json when the named entity it is attached to is serialized.
///
///  \warning Currently supported metadata types are bool, int, long, float,
///  double, and string. (int and float are handled and serialized as long and
///  double respectively) If any unsupported types are encountered, they will be
///  treated as string. If a badly formed int or float value is encountered as
///  metadata, it will be treated as a string instead.
///
///  \warning Currently, metadata cannot be nested.
///
/// Other Information
/// ===================
///
///  Doxygen generated documentation
///  -------------------------------
///
///  \warning When using Doxygen to generate HTML documentation for the source
///  code, Doxygen might emit warnings complaining that the declaration
///  corresponding to a definition could not be found for an operator annotated
///  with the AMINO_ANNOTATE() macro. The solution is also put the
///  AMINO_ANNOTATE() annotation on the function definition. It won't change its
///  definition as far as the C++ header parser is concerned.
///

// clang-format on
#ifndef AMINO_ANNOTATE_H
#define AMINO_ANNOTATE_H

#ifndef AMINO_ANNOTATE
#define AMINO_ANNOTATE(AnnotationStr__)
#endif

#endif

//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
// The Simple Associative example demonstrates how to implement and annotate an associative operator. 
//
// The example contains three versions of the same binary operator: a standard binary operator, a LeftToRight associative operator, 
// and  a RightToLeft associative operator. All three operators have the same implementations in the SimpleAssociative.cpp file.
// It is only their annotation in this header file that causes them to be instantiated differently in a Bifrost graph.
//+

#ifndef SIMPLE_ASSOCIATIVE_H
#define SIMPLE_ASSOCIATIVE_H

#include "SimpleAssociativeExport.h"

#include <Amino/Core/String.h>
#include <Amino/Cpp/Annotate.h>

namespace Examples {
namespace SDK {

// group() is the binary version of the operator. It takes two Amino::String inputs, first and second, concatenates them within 
// parentheses, and outputs the string "(first+second)" to the grouped output parameter. 
// It is annotated only with Amino::Node.
SIMPLE_ASSOCIATIVE_DECL
void group(const Amino::String& first,
                  const Amino::String& second,
                  Amino::String&       grouped)
    AMINO_ANNOTATE("Amino::Node");

//------------------------------------------------------------------------------
// group_associative_LeftToRight() is the LeftToRight associative version of the operator. Its signature is identical to
// group(). However because both its input parameters are annotated with Amino::IsAssociative, its input parameters will
// be instantiated into a dynamic port where a new port is created as soon as a connection is made to an existing port. 
// The operator itself is annotated with the associativity=LeftToRight token, defining how the inputs to the node are grouped.
// In LeftToRight associativity, inputs are grouped associatively starting from the first input port.
// This operator's input will be ((((first+second*)+second*)+second*) ...), where second* is the dynamic port created
// when the previous port was connected.
SIMPLE_ASSOCIATIVE_DECL
void group_associative_LeftToRight(
                  const Amino::String& first AMINO_ANNOTATE("Amino::Port Amino::IsAssociative"),
                  const Amino::String& second AMINO_ANNOTATE("Amino::Port Amino::IsAssociative"),
                  Amino::String&       grouped)
    AMINO_ANNOTATE("Amino::Node associativity=LeftToRight");

//------------------------------------------------------------------------------
// Just like with group_associative_LeftToRight(), group_associative_RightToLeft()'s input parameters are annotated 
// with Amino::IsAssociative, and will be instantiated into a dynamic port where a new port. However, the operator itself 
// is annotated with the associativity=RightToLeft token. In RightToLeft associativity, inputs are grouped associatively 
// starting from the last input port. So unlike group_associative_LeftToRight(), this operator's input will be 
// (first + (second*+ (second*+second*))...),  where second* is the dynamic port created when the previous port was connected.
SIMPLE_ASSOCIATIVE_DECL
void group_associative_RightToLeft(
                  const Amino::String& first AMINO_ANNOTATE("Amino::Port Amino::IsAssociative"),
                  const Amino::String& second AMINO_ANNOTATE("Amino::Port Amino::IsAssociative"),
                  Amino::String&       grouped)
    AMINO_ANNOTATE("Amino::Node associativity=RightToLeft");



//------------------------------------------------------------------------------

} // namespace SDK
} // namespace Examples

#endif // SIMPLE_ASSOCIATIVE_H

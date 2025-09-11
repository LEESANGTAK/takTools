//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
// 
// The Simple Associative example demonstrates how to implement and annotate an associative operator. 
//
// The example contains three versions of the same binary operator: a standard binary operator, a LeftToRight associative operator, 
// and  a RightToLeft associative operator. All three operators have the same implementations; only their annotations in
// SimpleAssociative.h differ.
//
// Associative operators must have exactly two input parameters and only one output parameter. 
//+

#include "SimpleAssociative.h"

#include <string>

//------------------------------------------------------------------------------
// group() is the binary version of the operator. It takes two Amino::String inputs, first and second, concatenates them within 
// parentheses, and outputs the string "(first+second)" to the grouped parameter.
void Examples::SDK::group(const Amino::String& first,
                                 const Amino::String& second,
                                 Amino::String&  grouped) {
    grouped = "(" + first + "+" + second + ")";
}

//------------------------------------------------------------------------------
// group_associative_LeftToRight() is the LeftToRight associative version of the operator. Its implementation is identical to
// group(); however because of its annotation in SimpleAssociative.h, its parameters are instantiated 
// as dynamic ports. Its output becomes ((((first+second*)+second*)+second*) ...), where second* is the dynamic port created
// when the previous port was connected.
void Examples::SDK::group_associative_LeftToRight(const Amino::String& first,
                                 const Amino::String& second,
                                 Amino::String&  grouped) {
     grouped = "(" + first + "+" + second + ")";
}

//------------------------------------------------------------------------------
// group_associative_RightToLeft() is the RightToLeft associative version of the operator. Its implementation is identical to
// group(); however because of its annotation in SimpleAssociative.h, its parameters are instantiated 
// as dynamic ports. Its output differs from the output of group_associative_LeftToRight() also because of its annotation.
// The RightToLeft annotation differs from the LeftToRight annotation in that its associative grouping starts from its last port
// instead of from its first port. Its outcome then becomes (first + (second*+ (second*+second*))...), 
// where second* is the dynamic port created when the previous port was connected.

void Examples::SDK::group_associative_RightToLeft(const Amino::String& first,
                                 const Amino::String& second,
                                 Amino::String&  grouped) {
    grouped = "(" +  first + "+" + second + ")";
}


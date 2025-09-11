//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "PassingConventions.h"

// Amino Core classes
#include <Amino/Core/Any.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Core/String.h>

namespace Examples {
namespace SDK {

//------------------------------------------------------------------------------
//
void input_passing_conventions(
    Amino::float_t                            builtin_by_value,
    Amino::int_t const&                       builtin_by_const_ref,
    MyEnum                                    enum_by_value,
    MyEnum const&                             enum_by_const_ref,
    Amino::String                             string_by_value,
    Amino::String const&                      string_by_const_ref,
    Amino::Any                                any_by_value,
    Amino::Any                                any_by_value2,
    Amino::Any                                any_by_value3,
    Amino::Any const&                         any_by_const_ref,
    MyStruct const&                           struct_by_const_ref,
    MyClass const&                            class_by_const_ref,
    Amino::Ptr<MyClass>                       class_by_ptr_value,
    Amino::Ptr<MyClass> const&                class_by_ptr_const_ref,
    Amino::MutablePtr<MyClass>                class_by_mutable_ptr_value,
    Amino::MutablePtr<PassingConventionUser>& output) {
    output = Amino::newMutablePtr<PassingConventionUser>();

    //--------------------------------------------------------------------------
    // Passing a C++ builtin type by value is always the prefered convention.
    output->builtin_by_value = builtin_by_value;

    //--------------------------------------------------------------------------
    // Passing a C++ builtin type by const& is ok, but passing by value is
    // preferable (see builtin_by_value).
    output->builtin_by_const_ref = builtin_by_const_ref;

    //--------------------------------------------------------------------------
    // Passing enums by value is always the prefered convention.
    output->enum_by_value = enum_by_value;

    //--------------------------------------------------------------------------
    // Passing an enum by const& is ok, but passing by value is preferable (see
    // enum_by_value).
    output->enum_by_const_ref = enum_by_const_ref;

    //--------------------------------------------------------------------------
    // Passing a String by value is a good choice if it's going to be moved
    // in another class / container.
    output->string_by_value = std::move(string_by_value);

    //--------------------------------------------------------------------------
    // Passing a String by const& is a good choice if we only need to read
    // from it, but we don't need to copy it or mutate it.
    output->string_by_const_ref = string_by_const_ref.size();

    //--------------------------------------------------------------------------
    // Passing an Any by value is a good choice if it's going to be moved in
    // another class / container, or if it could be moved to an output
    // argument.
    output->any_by_value = std::move(any_by_value);

    //--------------------------------------------------------------------------
    // Passing an Any by value is a good choice if the function wants to
    // steal its payload (move the payload out and take ownership of it)
    // and that there's a potential performance benefit from moving the
    // payload out reather than just copying it.
    //
    // In this case, we want to steal the payload as an Amino::Ptr<MyClass>.
    // It has a performance benefit because moving an Amino::Ptr is more
    // efficient than copying it.
    output->any_by_value2 =
        Amino::any_cast<Amino::Ptr<MyClass>>(std::move(any_by_value2));

    //--------------------------------------------------------------------------
    // Passing an Any by value is critical if the payload is going to be
    // extracted as an Amino::Ptr<T> AND mutated. That's the only way that a
    // copy of the object could be avoided and the mutation could be done
    // in-place. It does not guaranties that no copy will be made, but not doing
    // so would guaranty that a copy would be made.
    auto payload3 =
        Amino::any_cast<Amino::Ptr<MyClass>>(std::move(any_by_value3));
    if (payload3) {
        // Use a guard helper to mutate the value and store it back in the
        // Amino::Ptr. See Amino::createPtrGuard for details.
        auto guard = Amino::createPtrGuard(payload3);
        guard->getStdVectorInt().push_back(42);
    }
    output->any_by_value3 = std::move(payload3);

    //--------------------------------------------------------------------------
    // Passing an Any by const& is a good choice we only read it.
    output->any_by_const_ref = !any_by_const_ref.has_value();

    //--------------------------------------------------------------------------
    // Passing an Any by const& is a good choice if we want to get the
    // payload, but there's no benefit to move it.
    //
    // In this case, there's no benefit because the cost moving a float is
    // equivalent to just copying it.
    //
    // Warning: Any is an advanced type. Most of the time it should not be
    // needed. For example, in this case just passing a float would most likely
    // be a better option.
    output->builtin_by_value =
        Amino::any_cast<Amino::float_t>(any_by_const_ref);

    //--------------------------------------------------------------------------
    // Inputs of struct types can only be passed by const& in Amino.
    //
    // That indeed implies that it can't be moved and that none of its
    // member can be moved nor mutated either. If the function critically
    // requires to do that in order to be efficient, the best option
    // currently available would be to pass the members individually rather
    // than the whole struct.
    output->struct_by_const_ref = struct_by_const_ref;

    //--------------------------------------------------------------------------
    // Passing a class by const& is a good choice if we only need to read
    // it.
    output->class_by_const_ref = class_by_const_ref.getStdVectorInt().size();

    //--------------------------------------------------------------------------
    // Passing a class by Amino::Ptr value is a good choice if it's going to
    // be moved in another class / container.
    output->class_by_ptr_value = std::move(class_by_ptr_value);

    //--------------------------------------------------------------------------
    // Passing a class by Amino::Ptr const& is almost never a good choice.
    //
    // It could be a reasonnable choice if the function conditionally needs
    // to store it and never needs to mutate the pointee.
    output->class_by_ptr_const_ref =
        class_by_ptr_const_ref->getStdVectorInt().size() < 10
            ? class_by_ptr_const_ref
            : Amino::newClassPtr<MyClass>();

    //--------------------------------------------------------------------------
    // Passing a class by MutablePtr value is a good choice if the value
    // always has to be mutated and stored in another class / container.
    //
    // It's typically not the best option if the function wants to mutate it
    // in-place and then return it by assigning to an output parameter. In
    // this case, a better option is to use an in/out port.
    class_by_mutable_ptr_value->getStdVectorInt().push_back(10);
    output->class_by_mutable_ptr_value = std::move(class_by_mutable_ptr_value);
}

//------------------------------------------------------------------------------
//
void io_passing_conventions(Amino::String&       string_by_ref,
                            Amino::Any&          any_by_ref,
                            MyClass&             class_by_ref,
                            Amino::Ptr<MyClass>& class_by_ptr_ref) {
    //--------------------------------------------------------------------------
    // Passing a String by & In/Out is a good choice if it's going to be
    // mutated in-place.
    string_by_ref.append("_a_suffix");

    //--------------------------------------------------------------------------
    // Passing an Any by & In/Out is a good choice if it's going to be mutated
    // in-place.
    auto* payload = Amino::any_cast<float>(&any_by_ref);
    if (payload) *payload += 42.0F;

    //--------------------------------------------------------------------------
    // Passing a class by & In/Out is a good choice if it's going to be mutated
    // in-place.
    class_by_ref.getStdVectorInt().push_back(99);

    //--------------------------------------------------------------------------
    // Passing a class by Ptr& In/Out is good choice if it can both be mutated
    // or reassigned to a different Ptr.
    bool isValid = class_by_ptr_ref->getStdVectorInt().size() < 10;
    if (isValid) {
        // Mutate
        auto guard = Amino::createPtrGuard(class_by_ptr_ref);
        guard->getStdVectorInt().push_back(101);
    } else {
        // Assign a new pointer.
        auto newClass = Amino::newMutablePtr<MyClass>();
        newClass->getStdVectorInt().resize(10, 101);
        class_by_ptr_ref = std::move(newClass);
    }
    // WARNING: All the output and In/Out parameters that are managed by
    // Ptr/MutablePtr must NEVER be null.
    assert(class_by_ptr_ref != nullptr);
}

//------------------------------------------------------------------------------
//
Amino::float_t output_passing_conventions(
    PassingConventionUser const& input,
    Amino::float_t&              builtin_by_ref,
    MyEnum&                      enum_by_ref,
    Amino::String&               string_by_ref,
    Amino::Any&                  any_by_ref,
    MyStruct&                    struct_by_ref,
    Amino::Ptr<MyClass>&         class_by_ptr_ref,
    Amino::MutablePtr<MyClass>&  class_by_mutable_ptr_ref) {
    //--------------------------------------------------------------------------
    // C++ builtin output by & is a good choice if the return slot is alredy
    // used.
    builtin_by_ref = input.builtin_by_value;

    //--------------------------------------------------------------------------
    // Enum types output by & is a good choice if the return slot is alredy
    // used.
    enum_by_ref = input.enum_by_value;

    //--------------------------------------------------------------------------
    // String output by & is the only output convention for String.
    string_by_ref = input.string_by_value.substr(0, 5);

    //--------------------------------------------------------------------------
    // Any output by & is the only output convention for Any.
    any_by_ref = input.any_by_value;

    //--------------------------------------------------------------------------
    // Struct output by & is the only output convention for structs.
    struct_by_ref = input.struct_by_const_ref;

    //--------------------------------------------------------------------------
    // Class output by Ptr& is a good choice if the returned class is not newly
    // created (in this case it returning an already instanciated class in the
    // input).
    class_by_ptr_ref = input.class_by_ptr_value;

    // WARNING: All the output and In/Out parameters that are managed by
    // Ptr/MutablePtr must NEVER be null.
    //
    // The author must be extra careful to make sure that all code paths in
    // the function will assign to all outputs.
    assert(class_by_ptr_ref != nullptr);
    if (enum_by_ref == MyEnum::eX) {
        // THIS IS A BUG!
        // `class_by_mutable_ptr_ref` (below) was not assigned yet! There will
        // be a nullptr in the graph. This is not allowed and will lead to
        // undefined behavior (UB).
        return 0.0F;
    }

    //--------------------------------------------------------------------------
    // Class output by MutablePtr& is the prefered convention if the returned
    // class is newly created. This provides extra information to Amino that
    // this class has unique ownership when this function returns, which can
    // allow the compiler to perform some optimizations.
    class_by_mutable_ptr_ref = Amino::newMutablePtr<MyClass>();
    class_by_mutable_ptr_ref->getStdVectorInt().push_back(
        input.builtin_by_const_ref);
    assert(class_by_mutable_ptr_ref != nullptr);

    //--------------------------------------------------------------------------
    // Builtin and enum can be returned using the return slot.
    // This is the prefered output convention for those types.
    return input.builtin_by_value * 42.0F;
}

} // namespace SDK
} // namespace Examples

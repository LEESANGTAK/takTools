//-
//*****************************************************************************
// Copyright (c) 2024 Autodesk, Inc.
// All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+
//
/// \file Bifrost/Object/Object.h
///
/// \brief Bifrost object interface declaration.
///

#ifndef BIFROST_OBJECT_H
#define BIFROST_OBJECT_H

#include "ObjectExport.h"
#include "ObjectFwd.h"

#include <Amino/Core/Any.h>
#include <Amino/Core/ArrayFwd.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Core/String.h>
#include <Amino/Core/StringView.h>
#include <Amino/Cpp/Annotate.h>

//==============================================================================
// NAMESPACE Bifrost
//==============================================================================

//------------------------------------------------------------------------------
/// \brief Use a define, otherwise clang-format gets confused.
/// \warning : Ignoring namespace is an internal feature, should not be used by
/// external code.
#define BIFROST_IGNORE_NAMESPACE AMINO_ANNOTATE("Amino::Namespace ignore")
namespace Bifrost BIFROST_IGNORE_NAMESPACE {
#undef BIFROST_IGNORE_NAMESPACE

/// \defgroup BifrostObject Bifrost Object
/// \brief Class and utility functions for the Bifrost Objects.
///@{

/// \class Object Object.h
/// \brief An interface for dictionary-like objects.
///
/// The Object interface class specifies the methods to be implemented by a
/// class that needs to be handled as a Object.
///
/// Classes that implement of this interface are assumed to:
/// \li Have exposed data fields accessible as (key, value) pairs.
/// With the key being an Amino::String and the value an Amino::Any value.
/// \li Have data stored in Amino::Any follow Amino value semantic rules.
/// In particular, Amino::Any instance of a user class \<T\> stored in an
/// Amino::Any must be an Amino::Ptr<T> and behave correctly under Amino
/// reference counting.
class AMINO_ANNOTATE("Amino::Class metadata=[{type_kind, dictionary}]") OBJECT_DECL Object {
public:
    /*----- static member functions -----*/

    /// \brief Check if a given object contains all of the properties of the
    /// specified prototype.
    ///
    /// This check is recursive. If the prototype's value is an object, then
    /// \ref isA is also called to check that the object's property contains
    /// all the property of the prototypes's property.
    ///
    /// \param [in] object The reference to the object to check if it matches
    ///             the prototype.
    /// \param [in] prototype The reference to the prototype object to compare
    ///             with.
    ///
    /// \return True if the object contains all of the properties that the
    /// prototype object contains; false otherwise.
    static bool isA(Object const& object, Object const& prototype);

    /*----- types -----*/

    /// \brief A property in a Bifrost::Object.
    ///
    /// A property is a key-value pair, string->any.
    /// This class is used by the \ref createObject function. It can be useful
    /// to directly construct an object with a set of properties, instead of
    /// creating the object and calling \ref setProperty many times.
    struct Property {
        template <typename T>
        Property(Amino::String key, T&& value);

        Amino::String m_key;
        Amino::Any    m_value;
    };

    /*----- member functions -----*/

    /// \brief Constructor
    Object();

    /// \brief Destructor.
    virtual ~Object();

    /// \todo BIFROST-TBD CppParser does not accept pure virtual classes!
    ///
    /// This ifndef guard should not be used to lie to the CppParser!

    /// \name Interface description
    /// \{

    /// \brief Returns the number of properties in the %object
    virtual size_t size() const noexcept = 0;

    /// \brief Check if this object is empty.
    /// \return True if empty, else False.
    virtual bool empty() const noexcept = 0;

    /// \brief Check if the property exists.
    /// \param [in] key The property's name.
    /// \return True if the property exists in the object.
    virtual bool hasProperty(Amino::StringView key) const noexcept = 0;

    /// \brief Get a property
    /// \param [in] key The property name to fetch
    /// \return The property. The Amino::Any will be empty if no such property
    /// was found in the object or if the property was found but its associated
    /// value is an empty Amino::Any.
    virtual Amino::Any getProperty(Amino::StringView key) const noexcept = 0;

    /// \brief Extract a property. The property is removed and returned.
    /// \param [in] key The property's name to extract.
    /// \return A non-empty Amino::Any if the property existed
    virtual Amino::Any extractProperty(Amino::StringView key) noexcept = 0;

    /// \brief Erase a property.
    /// \param [in] key The property's name
    /// \return True if the property was erased (removed from the object)
    virtual bool eraseProperty(Amino::StringView key) noexcept = 0;

    /// \brief Clear the object. After size() == 0 and empty() is true.
    virtual void eraseAllProperties() noexcept = 0;

    /// \brief Get all of the keys stored in this object.
    /// \return Return a ptr to an array of the keys.
    /// See Ptr.h for more information.
    virtual Amino::Ptr<Amino::Array<Amino::String>> keys() const noexcept = 0;

    /// \}

    /// \brief Set a property.
    /// Replace or add depending on if the property already exists or not in the
    /// object.
    /// \param [in] key The property's name.
    /// \param [in] value The value of this property.
    /// \{
    template <typename T>
    bool setProperty(Amino::StringView key, T&& value) noexcept;

    template <typename S, typename T>
    typename std::enable_if<std::is_same<std::decay_t<S>,Amino::String>::value,bool>::type
    setProperty(S&& key, T&& value) noexcept;
    /// \}

protected:
    /// \brief Only subclasses allowed to use copy/move constructor/assignments.
    ///
    /// The Object not is publicly copiable/movable because it's a pure virtual
    /// class. The copy/move constructor and assignments are still defaulted
    /// but protected, to allows subclasses to = default their copy/move
    /// constructor and assignments if they want to.
    /// \{
    Object(Object&&) noexcept = default;
    Object(Object const&)     = default;
    Object& operator=(Object&&) noexcept = default;
    Object& operator=(Object const&) = default;
    /// \}

    /// \brief Set a property with an Amino::Any.
    ///
    /// Prefer using setProperty instead of this method. Use this method only
    /// when the Amino::Any being passed in comes from getProperty(). For
    /// example when copying properties from one object to another.
    ///
    /// Replace or add depending on if the property already exists or not in the
    /// object.
    ///
    /// \param [in] key The property's name.
    /// \param [in] value A Amino::Any.
    ///
    /// \{
    virtual bool setPropertyAny(Amino::StringView key, Amino::Any value) noexcept    = 0;
    virtual bool setPropertyAny(Amino::String const& key, Amino::Any value) noexcept = 0;
    /// \}
};

//==============================================================================
// GLOBAL FUNCTIONS
//==============================================================================

/// \defgroup BifrostObjectGlobalFunctions Bifrost Object Functions
/// \brief Functions to create and manipulate Bifrost Objects.
///@{
//------------------------------------------------------------------------------
//
/// \brief Construct a new Object
/// \return A Amino::MutablePtr to a new Object.
OBJECT_DECL
Amino::MutablePtr<Object> createObject();

//------------------------------------------------------------------------------
//
/// \brief Construct a new Object with the given properties
/// \return A Amino::MutablePtr to the new object with the given
/// properties.
OBJECT_DECL
Amino::MutablePtr<Object> createObject(
    std::initializer_list<Object::Property> properties);

///@}
///@}

//==============================================================================
// Implementation details
//==============================================================================

//------------------------------------------------------------------------------
//
/// \cond AMINO_INTERNAL_DOCS
/// \brief Private implementation details used by the Object.
namespace Internal {
template <typename T>
inline Amino::Any makeAny(T&& v) {
    return Amino::Any{std::forward<T>(v)};
}
inline Amino::Any makeAny(Amino::Any v) { return v; }
inline Amino::Any makeAny(const char* v) {
    return Amino::Any{Amino::String(v)};
}
inline Amino::Any makeAny(Amino::StringView v) {
    return Amino::Any{Amino::String(v)};
}   
template <typename T>
inline Amino::Any makeAny(Amino::MutablePtr<T> v) {
    return Amino::Any{Amino::Ptr<T>{std::move(v)}};
}
} // namespace Internal

//==============================================================================
// CLASS Object::Property
//==============================================================================

template <typename T>
Object::Property::Property(Amino::String key, T&& value)
    : m_key(std::move(key)),
      m_value(Internal::makeAny(std::forward<T>(value))) // LCOV_EXCL_BR_LINE
{}

//==============================================================================
// CLASS Object
//==============================================================================

template <typename T>
bool Object::setProperty(Amino::StringView key, T&& value) noexcept {
    // LCOV_EXCL_BR_START
    if (key.empty()) {
        return false; // keys not allowed to be empty strings
    }
    return setPropertyAny(key, Internal::makeAny(std::forward<T>(value)));
    // LCOV_EXCL_BR_STOP
}

template <typename S, typename T>
typename std::enable_if<std::is_same<std::decay_t<S>, Amino::String>::value, bool>::type
Object::setProperty(S&& key, T&& value) noexcept {
    // LCOV_EXCL_BR_START
    if (key.empty()) {
        return false; // keys not allowed to be empty strings
    }
    return setPropertyAny(key, Internal::makeAny(std::forward<T>(value)));
    // LCOV_EXCL_BR_STOP
}

/// \endcond

} // namespace Bifrost BIFROST_IGNORE_NAMESPACE

#endif // BIFROST_OBJECT_H

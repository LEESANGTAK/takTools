//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef PERIODIC_TABLE_ELEMENT_H
#define PERIODIC_TABLE_ELEMENT_H

#include "ExecutorWatchpointExport.h"

#include <Amino/Cpp/Annotate.h>
#include <Amino/Cpp/ClassDeclare.h>

#include <Amino/Core/BuiltInTypes.h>
#include <Amino/Core/PtrFwd.h>
#include <Amino/Core/String.h>

#include <utility>

namespace Examples {
namespace SDK {

//==============================================================================
// Class PeriodicTableElement
//==============================================================================

/// \brief Define a class representing an address.
///
/// The class has the name "PeriodicTableElement" and is defined in the
/// "Examples::SDK" namespace. Its fully qualified name is therefore
/// "Examples::SDK::PeriodicTableElement". This fully qualified name is therefore a
/// unique identifier for our "PeriodicTableElement" class.
class AMINO_ANNOTATE("Amino::Class") EXECUTOR_WATCHPOINT_DECL PeriodicTableElement {
public:
    PeriodicTableElement()                                  = default;
    PeriodicTableElement(PeriodicTableElement const& other) = default;
    ~PeriodicTableElement()                                 = default;

    PeriodicTableElement(Amino::String  name,
                         Amino::float_t mass,
                         Amino::uint_t  number,
                         Amino::String  symbol)
        : m_name{std::move(name)}, m_mass{mass}, m_number{number}, m_symbol{std::move(symbol)} {}

    Amino::String  getName() const { return m_name; }
    Amino::float_t getMass() const { return m_mass; }
    Amino::uint_t  getNumber() const { return m_number; }
    Amino::String  getSymbol() const { return m_symbol; }

private:
    Amino::String  m_name{};
    Amino::float_t m_mass{};
    Amino::uint_t  m_number{};
    Amino::String  m_symbol{};
};

//------------------------------------------------------------------------------
//
/// \brief Get a periodic table element
EXECUTOR_WATCHPOINT_DECL
void get_periodic_table_element(Amino::String const&                                 name,
                                Amino::bool_t&                                       found,
                                Amino::MutablePtr<Examples::SDK::PeriodicTableElement>& element)
    AMINO_ANNOTATE("Amino::Node");

//------------------------------------------------------------------------------
//
/// \brief Get the properties of an element
void get_periodic_table_element_properties(Examples::SDK::PeriodicTableElement const& element,
                                           Amino::String&                          name,
                                           Amino::float_t&                         mass,
                                           Amino::uint_t&                          number,
                                           Amino::String& symbol) AMINO_ANNOTATE("Amino::Node");

} // namespace SDK
} // namespace Examples

// Macro for generating the getDefault entry point declaration related
// to a given opaque type.
// This is necessary to allow Amino graphs to create default values for
// opaque, class types.
// See AMINO_DEFINE_DEFAULT_CLASS in IndexSet.cpp
AMINO_DECLARE_DEFAULT_CLASS(EXECUTOR_WATCHPOINT_DECL, Examples::SDK::PeriodicTableElement);

#endif // PERIODIC_TABLE_ELEMENT_H

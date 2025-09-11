//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They
// may not be disclosed to, copied  or used by any third party without the
// prior written consent of Autodesk, Inc.
// =============================================================================
//+

#include "PeriodicTableElement.h"

#include <Amino/Cpp/ClassDefine.h>

#include <Amino/Core/Ptr.h>

#include <algorithm>
#include <map>
#include <string>

namespace {
using SimplePeriodicTable = std::map<std::string, Examples::SDK::PeriodicTableElement>;

/*
    The periodic table information is extracted from:
        "source"        : "https://github.com/Bowserinator/Periodic-Table-JSON",
        "license"       : "Creative Common Attribution-ShareAlike 3.0 Unported",
        "license_link"  : "http://creativecommons.org/licenses/by-sa/3.0"
*/
SimplePeriodicTable periodicTable{{"hydrogen", {"Hydrogen", 1.008F, 1, "H"}},
                                  {"helium", {"Helium", 4.0026022F, 2, "He"}},
                                  {"lithium", {"Lithium", 6.94F, 3, "Li"}},
                                  {"beryllium", {"Beryllium", 9.01218315F, 4, "Be"}},
                                  {"boron", {"Boron", 10.81F, 5, "B"}},
                                  {"carbon", {"Carbon", 12.011F, 6, "C"}},
                                  {"nitrogen", {"Nitrogen", 14.007F, 7, "N"}},
                                  {"oxygen", {"Oxygen", 15.999F, 8, "O"}},
                                  {"fluorine", {"Fluorine", 18.9984031636F, 9, "F"}},
                                  {"neon", {"Neon", 20.17976F, 10, "Ne"}},
                                  {"sodium", {"Sodium", 22.989769282F, 11, "Na"}},
                                  {"magnesium", {"Magnesium", 24.305F, 12, "Mg"}},
                                  {"aluminium", {"Aluminium", 26.98153857F, 13, "Al"}},
                                  {"silicon", {"Silicon", 28.085F, 14, "Si"}},
                                  {"phosphorus", {"Phosphorus", 30.9737619985F, 15, "P"}},
                                  {"sulfur", {"Sulfur", 32.06F, 16, "S"}},
                                  {"chlorine", {"Chlorine", 35.45F, 17, "Cl"}},
                                  {"argon", {"Argon", 39.9481F, 18, "Ar"}},
                                  {"potassium", {"Potassium", 39.09831F, 19, "K"}},
                                  {"calcium", {"Calcium", 40.0784F, 20, "Ca"}},
                                  {"scandium", {"Scandium", 44.9559085F, 21, "Sc"}},
                                  {"titanium", {"Titanium", 47.8671F, 22, "Ti"}},
                                  {"vanadium", {"Vanadium", 50.94151F, 23, "V"}},
                                  {"chromium", {"Chromium", 51.99616F, 24, "Cr"}},
                                  {"manganese", {"Manganese", 54.9380443F, 25, "Mn"}},
                                  {"iron", {"Iron", 55.8452F, 26, "Fe"}},
                                  {"cobalt", {"Cobalt", 58.9331944F, 27, "Co"}},
                                  {"nickel", {"Nickel", 58.69344F, 28, "Ni"}},
                                  {"copper", {"Copper", 63.5463F, 29, "Cu"}},
                                  {"zinc", {"Zinc", 65.382F, 30, "Zn"}},
                                  {"gallium", {"Gallium", 69.7231F, 31, "Ga"}},
                                  {"germanium", {"Germanium", 72.6308F, 32, "Ge"}},
                                  {"arsenic", {"Arsenic", 74.9215956F, 33, "As"}},
                                  {"selenium", {"Selenium", 78.9718F, 34, "Se"}},
                                  {"bromine", {"Bromine", 79.904F, 35, "Br"}},
                                  {"krypton", {"Krypton", 83.7982F, 36, "Kr"}},
                                  {"rubidium", {"Rubidium", 85.46783F, 37, "Rb"}},
                                  {"strontium", {"Strontium", 87.621F, 38, "Sr"}},
                                  {"yttrium", {"Yttrium", 88.905842F, 39, "Y"}},
                                  {"zirconium", {"Zirconium", 91.2242F, 40, "Zr"}},
                                  {"niobium", {"Niobium", 92.906372F, 41, "Nb"}},
                                  {"molybdenum", {"Molybdenum", 95.951F, 42, "Mo"}},
                                  {"technetium", {"Technetium", 98.0F, 43, "Tc"}},
                                  {"ruthenium", {"Ruthenium", 101.072F, 44, "Ru"}},
                                  {"rhodium", {"Rhodium", 102.905502F, 45, "Rh"}},
                                  {"palladium", {"Palladium", 106.421F, 46, "Pd"}},
                                  {"silver", {"Silver", 107.86822F, 47, "Ag"}},
                                  {"cadmium", {"Cadmium", 112.4144F, 48, "Cd"}},
                                  {"indium", {"Indium", 114.8181F, 49, "In"}},
                                  {"tin", {"Tin", 118.7107F, 50, "Sn"}},
                                  {"antimony", {"Antimony", 121.7601F, 51, "Sb"}},
                                  {"tellurium", {"Tellurium", 127.603F, 52, "Te"}},
                                  {"iodine", {"Iodine", 126.904473F, 53, "I"}},
                                  {"xenon", {"Xenon", 131.2936F, 54, "Xe"}},
                                  {"cesium", {"Cesium", 132.905451966F, 55, "Cs"}},
                                  {"barium", {"Barium", 137.3277F, 56, "Ba"}},
                                  {"lanthanum", {"Lanthanum", 138.905477F, 57, "La"}},
                                  {"cerium", {"Cerium", 140.1161F, 58, "Ce"}},
                                  {"praseodymium", {"Praseodymium", 140.907662F, 59, "Pr"}},
                                  {"neodymium", {"Neodymium", 144.2423F, 60, "Nd"}},
                                  {"promethium", {"Promethium", 145.0F, 61, "Pm"}},
                                  {"samarium", {"Samarium", 150.362F, 62, "Sm"}},
                                  {"europium", {"Europium", 151.9641F, 63, "Eu"}},
                                  {"gadolinium", {"Gadolinium", 157.253F, 64, "Gd"}},
                                  {"terbium", {"Terbium", 158.925352F, 65, "Tb"}},
                                  {"dysprosium", {"Dysprosium", 162.5001F, 66, "Dy"}},
                                  {"holmium", {"Holmium", 164.930332F, 67, "Ho"}},
                                  {"erbium", {"Erbium", 167.2593F, 68, "Er"}},
                                  {"thulium", {"Thulium", 168.934222F, 69, "Tm"}},
                                  {"ytterbium", {"Ytterbium", 173.0451F, 70, "Yb"}},
                                  {"lutetium", {"Lutetium", 174.96681F, 71, "Lu"}},
                                  {"hafnium", {"Hafnium", 178.492F, 72, "Hf"}},
                                  {"tantalum", {"Tantalum", 180.947882F, 73, "Ta"}},
                                  {"tungsten", {"Tungsten", 183.841F, 74, "W"}},
                                  {"rhenium", {"Rhenium", 186.2071F, 75, "Re"}},
                                  {"osmium", {"Osmium", 190.233F, 76, "Os"}},
                                  {"iridium", {"Iridium", 192.2173F, 77, "Ir"}},
                                  {"platinum", {"Platinum", 195.0849F, 78, "Pt"}},
                                  {"gold", {"Gold", 196.9665695F, 79, "Au"}},
                                  {"mercury", {"Mercury", 200.5923F, 80, "Hg"}},
                                  {"thallium", {"Thallium", 204.38F, 81, "Tl"}},
                                  {"lead", {"Lead", 207.21F, 82, "Pb"}},
                                  {"bismuth", {"Bismuth", 208.980401F, 83, "Bi"}},
                                  {"polonium", {"Polonium", 209.0F, 84, "Po"}},
                                  {"astatine", {"Astatine", 210.0F, 85, "At"}},
                                  {"radon", {"Radon", 222.0F, 86, "Rn"}},
                                  {"francium", {"Francium", 223.0F, 87, "Fr"}},
                                  {"radium", {"Radium", 226.0F, 88, "Ra"}},
                                  {"actinium", {"Actinium", 227.0F, 89, "Ac"}},
                                  {"thorium", {"Thorium", 232.03774F, 90, "Th"}},
                                  {"protactinium", {"Protactinium", 231.035882F, 91, "Pa"}},
                                  {"uranium", {"Uranium", 238.028913F, 92, "U"}},
                                  {"neptunium", {"Neptunium", 237.0F, 93, "Np"}},
                                  {"plutonium", {"Plutonium", 244.0F, 94, "Pu"}},
                                  {"americium", {"Americium", 243.0F, 95, "Am"}},
                                  {"curium", {"Curium", 247.0F, 96, "Cm"}},
                                  {"berkelium", {"Berkelium", 247.0F, 97, "Bk"}},
                                  {"californium", {"Californium", 251.0F, 98, "Cf"}},
                                  {"einsteinium", {"Einsteinium", 252.0F, 99, "Es"}},
                                  {"fermium", {"Fermium", 257.0F, 100, "Fm"}},
                                  {"mendelevium", {"Mendelevium", 258.0F, 101, "Md"}},
                                  {"nobelium", {"Nobelium", 259.0F, 102, "No"}},
                                  {"lawrencium", {"Lawrencium", 266.0F, 103, "Lr"}},
                                  {"rutherfordium", {"Rutherfordium", 267.0F, 104, "Rf"}},
                                  {"dubnium", {"Dubnium", 268.0F, 105, "Db"}},
                                  {"seaborgium", {"Seaborgium", 269.0F, 106, "Sg"}},
                                  {"bohrium", {"Bohrium", 270.0F, 107, "Bh"}},
                                  {"hassium", {"Hassium", 269.0F, 108, "Hs"}},
                                  {"meitnerium", {"Meitnerium", 278.0F, 109, "Mt"}},
                                  {"darmstadtium", {"Darmstadtium", 281.0F, 110, "Ds"}},
                                  {"roentgenium", {"Roentgenium", 282.0F, 111, "Rg"}},
                                  {"copernicium", {"Copernicium", 285.0F, 112, "Cn"}},
                                  {"nihonium", {"Nihonium", 286.0F, 113, "Nh"}},
                                  {"flerovium", {"Flerovium", 289.0F, 114, "Fl"}},
                                  {"moscovium", {"Moscovium", 289.0F, 115, "Mc"}},
                                  {"livermorium", {"Livermorium", 293.0F, 116, "Lv"}},
                                  {"tennessine", {"Tennessine", 294.0F, 117, "Ts"}},
                                  {"oganesson", {"Oganesson", 294.0F, 118, "Og"}},
                                  {"ununennium", {"Ununennium", 315.0F, 119, "Uue"}}};
} // namespace

void Examples::SDK::get_periodic_table_element(
    Amino::String const&                                 name,
    Amino::bool_t&                                       found,
    Amino::MutablePtr<Examples::SDK::PeriodicTableElement>& element) {
    std::string lowercaseName(name.data(), name.size());

    std::transform(lowercaseName.begin(), lowercaseName.end(), lowercaseName.begin(),
                   [](char c) { return static_cast<char>(std::tolower(c)); });

    auto elem = periodicTable.find(lowercaseName);
    if (elem != periodicTable.end()) {
        found   = true;
        element = Amino::newMutablePtr<Examples::SDK::PeriodicTableElement>(elem->second);

    } else {
        found   = false;
        element = Amino::newMutablePtr<Examples::SDK::PeriodicTableElement>();
    }
}

void Examples::SDK::get_periodic_table_element_properties(
    Examples::SDK::PeriodicTableElement const& element,
    Amino::String&                          name,
    Amino::float_t&                         mass,
    Amino::uint_t&                          number,
    Amino::String&                          symbol) {
    name   = element.getName();
    mass   = element.getMass();
    number = element.getNumber();
    symbol = element.getSymbol();
}

/// Macro for generating the getDefault entry point definition
/// This is necessary to allow Amino graphs to create default values for
/// opaque, class types.
AMINO_DEFINE_DEFAULT_CLASS(Examples::SDK::PeriodicTableElement);

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
/// \file GeoProperty.h
///
/// \brief Utility functions for manipulating Geometry Properties that conform to the geometry schema.
///

#ifndef BIFROST_GEOMETRY_GEO_PROPERTY_H
#define BIFROST_GEOMETRY_GEO_PROPERTY_H

#include <Bifrost/Geometry/GeometryExport.h>

#include <Bifrost/Geometry/GeoPropertyKey.h>
#include <Bifrost/Geometry/GeometryTypes.h>
#include <Bifrost/Math/Types.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/StringView.h>

namespace Bifrost {
namespace Geometry {

// -----------------------------------------------------------------------------
// GeoProperty methods
//

/// \defgroup GeoProperties Geometry Properties
/// \brief Utility functions for manipulating GeoProperties that conform to the geometry schema.
///@{

/// \defgroup GeoPropertyTarget GeoProperty Target
/// \brief Functions for querying and setting the target of a geo property.
///@{
/*! \brief Get referenced counted pointer of the target of a specified geometry property.
    \param [in] object Geometry object.  The target will be fetched from this object.
    \param [in] geoProp Property that contains the target field.
    \return A reference counted pointer to the target property found in object.
    The reference counted pointer secures access to the data
*/
Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getGeoPropTarget(const Bifrost::Object& object,
                                                                   const Bifrost::Object& geoProp);

/*! \brief Get the name of the target for the specified geo property.
    \param [in] object Geometry object.
    \param [in] geoProp The geo property to query.
    \return The target of the specified geo property, or an empty string on error.
*/
Amino::String BIFROST_GEOMETRY_DECL getGeoPropTargetName(const Bifrost::Object& object,
                                                         Amino::StringView      geoProp);

/*! \brief Get the name of the target for the specified geo property.
    \param [in] geoProp The geo property to query.
    \return The target of the specified geo property, or an empty string on error.
*/
Amino::String BIFROST_GEOMETRY_DECL getGeoPropTargetName(const Bifrost::Object& geoProp);

/*! \brief Determines the topological component that the specified geometry
    property is defined over.

    In most cases this will return the same value as getGeoPropTargetName().
    However if the geo property is indexed, that function will return the name of
    the geo property that contains the indices, whereas this function will
    resolve to the final topological component that the data is defined over.
    \param [in] object The object to query.
    \param [in] geoProp The geo property within the object to query.
    \return The name of the component that the geo property is defined over,
            or an empty string on error.
*/
Amino::String BIFROST_GEOMETRY_DECL getTargetComponent(const Bifrost::Object& object,
                                                       Amino::StringView      geoProp);

/*! \brief Walks the target chain from the given geo property to the terminal geo
    component property.

    This is typically used to determine the indexing of a
    data geo property. If the returned target array is empty, the data geo property
    maps 1:1 to the topological components its defined over. If the returned
    target array contains one element, that element will be the name of a range
    geo property that maps topological component indices to indices within
    the specified data geo property's data array. Note that Bifrost geometry
    validators enforce just one level of indirection.

    For example, in a mesh if normals target the vertices directly, this function
    will return an empty array. However if normals target the face vertices,
    then this function will return an array of one element, which will be the name
    of the range geo property that contains the per-face indices that index
    into the array of normals.

    \param [in] object The object to query.
    \param [in] geoProp The geo property to query.
    \return The ranges in-between the geo property and the geo component. The
            array may be empty if no ranges exists, or if errors occur.
*/
Amino::Array<Amino::String> BIFROST_GEOMETRY_DECL getTargetChain(const Bifrost::Object& object,
                                                                 Amino::StringView      geoProp);
///@}

// ---------------------------------------------------------------------------------------
// ComponentGeoProperty methods

/// \defgroup ComponentGeoProperty Component GeoProperty
/// \brief Functions for manipulating Component GeoProperties.
///@{

/*! \brief Returns the prototypical component geometry property object.

    The returned pointer may be used in conjunction with Bifrost::Object::isA to
    determine if an object conforms to the component geometry property schema.
    The returned object may not be modified.
    \return The component geo property prototype.
*/
Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getComponentGeoPropPrototype();

/*! \brief Populate a Geometry object with the required properties to conform to the
    component geometry property schema.
    \param [in] elementCount The number of elements (stored).
    \param [in,out] object Object to be populated.
*/
void BIFROST_GEOMETRY_DECL populateComponentGeoProperty(Amino::uint_t    elementCount,
                                                        Bifrost::Object& object);

/*! \brief Set the number of elements in a component of a geometry.

    For example, to set the number of points to 10, in a points geometry:
    \code{.cpp}
        setElementCount(sPointComp, 10, pointsGeo);
    \endcode

    \param [in] component Name of the component geometry property.
    \param [in] elementCount Number of elements (stored).
    \param [in,out] object Object that contains the geometry property component
        that will be modified.
    \return true on success, false otherwise.
*/
bool BIFROST_GEOMETRY_DECL setElementCount(Amino::StringView component,
                                           Amino::uint_t     elementCount,
                                           Bifrost::Object&  object);

/*! \brief Get the number of elements in a component of a geometry.

    For example, to get the number of points in a points geometry:
    \code{.cpp}
        auto pointCount = getElementCount(pointsGeo, sPointComp);
    \endcode

    \param [in] object Geometry object which contains the ComponentGeoProperty.
    \param [in] component Name of the component geometry property.
    \return The number of elements or zero on error.
*/
Amino::uint_t BIFROST_GEOMETRY_DECL getElementCount(const Bifrost::Object& object,
                                                    Amino::StringView      component);

/*! \brief Get the number of component elements in a ComponentGeoProperty object.
    \param [in] compGeoProp Component Geo Property to query.
    \return The number of elements or zero on error.
*/
Amino::uint_t BIFROST_GEOMETRY_DECL getElementCount(const Bifrost::Object& compGeoProp);
///@}

// -----------------------------------------------------------------------------
// DataGeoProperty methods

/// \defgroup DataGeoProperty Data GeoProperty
/// \brief Functions for manipulating Data GeoProperties.
///@{

/*! \brief Returns the prototypical data geometry property object.

    The returned pointer may be used in conjunction with  Bifrost::Object::isA to
    determine if an object conforms to the data geometry property schema. The
    returned object may not be modified.

    If the generic data geometry property object is returned then it will  match
    with any data geometry property whatever the specific data and default
    types of the data geometry property checked with Bifrost::Object::isA.

    \param [in] property The name of a standard data geometry property found on a
    standard geometry prototype built from a geometry schema. If the data geometry property
    does not exists then an invalid data geometry property prototype is returned
    and nothing will match with it.

    \return The data geometry property prototype.
*/
Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL
getDataGeoPropPrototype(Amino::StringView property = Geometry::sGenericDataGeoProp);

/*! \brief Populate a Geometry object with the required properties to conform to
    the data geometry property schema.

    The geo property is initially empty.

    \param [in] defaultValue The default value of the data geometry property.
    \param [in,out] object Object to be populated.
*/
template <typename T>
void populateDataGeoProperty(T defaultValue, Bifrost::Object& object) {
    Amino::Ptr<Amino::Array<T>> data = Amino::newClassPtr<Amino::Array<T>>();
    object.setProperty(Geometry::sData, data);

    object.setProperty(Geometry::sTarget, Geometry::sNullString);

    Amino::Ptr<Amino::Array<Amino::String>> depends =
        Amino::newClassPtr<Amino::Array<Amino::String>>(0);
    object.setProperty(Geometry::sDependsOn, depends);

    object.setProperty(Geometry::sDefault, defaultValue);

    object.setProperty(Geometry::sInterp, Bifrost::Geometry::Common::DataInterpolationMode::Linear);
}

/*! \brief Populate a Geometry object with the required properties to conform to
    the data geometry property schema.

    The geo property is initialized with the specified data.

    \param [in] defaultValue The default value of the data geometry property.
    \param [in] data The Amino::Array of initial data.
    \param [in] target The target of the geo property.
    \param [in,out] geoProp Object to be populated.
*/
template <typename DataType>
void populateDataGeoProperty(const DataType&                    defaultValue,
                             Amino::Ptr<Amino::Array<DataType>> data,
                             Amino::StringView                  target,
                             Bifrost::Object&                   geoProp) {
    populateDataGeoProperty(defaultValue, geoProp);

    geoProp.setProperty(Geometry::sTarget, target);
    geoProp.setProperty(Geometry::sData, data);
}

/*! \brief Get a geo property from an object, with the specified name.
    \param [in] object The data geo property.
    \param [in] property The property name.
    \return The data geo property object, or nullptr if it does not exist.
*/
Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getDataGeoProperty(const Bifrost::Object& object,
                                                                     Amino::StringView property);

/*! \brief Get the actual data array from a data geometry property.
    \param [in] object Object on which to look for the data geometry property.
    \param [in] property Data geometry property name. If this name does not
                specify a valid data geometry property, this function will fail.
    \return Referenced counted pointer to the array of data.
    The reference count secures the data access.
*/
template <typename T>
Amino::Ptr<Amino::Array<T>> getDataGeoPropValues(const Bifrost::Object& object,
                                                 Amino::StringView      property) {
    Amino::Any propVal = object.getProperty(property);
    auto       dataObj = Amino::any_cast<Amino::Ptr<Bifrost::Object>>(&propVal);
    if (!dataObj || dataObj->get() == nullptr || !(*dataObj)->hasProperty(Geometry::sData)) {
        return nullptr;
    }

    auto dataVal = (*dataObj)->getProperty(Geometry::sData);
    auto data    = Amino::any_cast<Amino::Ptr<Amino::Array<T>>>(&dataVal);
    return data ? std::move(*data) : nullptr;
}

/*! \brief Sets the actual data array in a data geometry property.
    \param [in] property Data geometry property name. If this name does not
                specify a valid data geometry property, this function will fail.
    \param [in] dataPropValues The new Amino::Array of data to set in the data geo property.
    \param [in,out] object Parent object of the data geometry property.
    \return true on success, false otherwise.
*/
template <typename DataType>
bool setDataGeoPropValues(Amino::StringView                  property,
                          Amino::Ptr<Amino::Array<DataType>> dataPropValues,
                          Bifrost::Object&                   object) {
    Amino::Any val     = object.getProperty(property);
    auto       dataObj = Amino::any_cast<Amino::Ptr<Bifrost::Object>>(&val);
    if (!dataObj || dataObj->get() == nullptr || !(*dataObj)->hasProperty(Geometry::sData)) {
        return false;
    }

    auto dataObj2 = dataObj->toMutable();
    dataObj2->setProperty(Geometry::sData, dataPropValues);
    object.setProperty(property, std::move(dataObj2));

    return true;
}

/*! \brief Queries if the specified property is an offset array.
    \param [in] object Object on which to look for the data geometry property.
    \param [in] property Data geometry property name.
    \return True if the data geo property exists on the object and is an offset array.
*/
bool BIFROST_GEOMETRY_DECL isOffsetDataGeoProp(const Bifrost::Object& object,
                                               Amino::StringView      property);
///@}

// -----------------------------------------------------------------------------
// RangeGeoProperty methods

/// \defgroup RangeGeoProperty Range GeoProperty
/// \brief Functions for manipulating Range GeoProperties.
///@{

/*! \brief Returns the prototypical range geometry property object.

    The returned pointer may be used in conjunction with  Bifrost::Object::isA to
    determine if an object conforms to the range geometry property schema. The
    returned object may not be modified.
    \return The range geo property prototype.
*/
Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getRangeGeoPropPrototype();

/*! \brief Populate a Geometry object with the required properties to conform to the range
    geometry property schema.

    \param [in,out] object Geometry object to be populated.
*/
void BIFROST_GEOMETRY_DECL populateRangeGeoProperty(Bifrost::Object& object);

/*! \brief Populate a Geometry object with the required properties to conform to
    the range geometry property schema.

    It is templated on the index array type.

    \param [in] indices The indices that map components to data. May be nullptr.
    \param [in] target The target for the range.
    \param [in,out] geoProp Geometry object to be populated.
    \return true on success, false otherwise.
*/
bool BIFROST_GEOMETRY_DECL populateRangeGeoProperty(Amino::Ptr<Amino::Array<Index>> indices,
                                                    Amino::StringView               target,
                                                    Bifrost::Object&                geoProp);

/*! \brief Get a range geo property from an object.

    A nullptr is returned if the specified property could not be found.

    \param [in] object The object to query.
    \param [in] property The name of the range geo property to return.
    \return The range geo property, or nullptr if it could not be found.
*/
Amino::Ptr<Bifrost::Object> BIFROST_GEOMETRY_DECL getRangeGeoProperty(const Bifrost::Object& object,
                                                                      Amino::StringView property);

/*! \brief Get the indices for the specified range geometry property.
    \param [in] object Object on which to look for the rage geometry property
                indices.
    \param [in] property Range geometry property name. If this name does not
                specify a valid range geometry property, this function will fail.
    \return Referenced counted pointer to the array of data or nullptr if the
            range does not exist. The reference count secures the data access.
*/
Amino::Ptr<Amino::Array<Index>> BIFROST_GEOMETRY_DECL
getRangeGeoPropIndices(const Bifrost::Object& object, Amino::StringView property);

/*! \brief Get the indices for the specified range object.

    \param [in] rangeGeoProp The range geo property
    \return The index array, or nullptr if it could not be found.
*/
Amino::Ptr<Amino::Array<Index>> BIFROST_GEOMETRY_DECL
getRangeGeoPropIndices(const Bifrost::Object& rangeGeoProp);

/*! \brief Get the indices for the specified range geometry property.

    \param [in] property Range geometry property name.  If this name does not
                specify a valid range geometry property, this function will fail.
    \param [in] indices The Amino::Array of indices to set on the range geometry property.
    \param [in,out] object Object on which to look for the range geometry property.
    \return true on success, false otherwise.
*/
bool BIFROST_GEOMETRY_DECL setRangeGeoPropIndices(Amino::StringView               property,
                                                  Amino::Ptr<Amino::Array<Index>> indices,
                                                  Bifrost::Object&                object);

/*! \brief Creates a trivial indexing with the specified size.

    \param [in] count The number of indices required.
    \param [in] indices The index array to populate.
*/
void BIFROST_GEOMETRY_DECL populateTrivialRangeIndices(size_t count, Amino::Array<Index>& indices);

/*! \brief Gets the name of a data geo property's corresponding range geo
    property.

    Note this only returns a string name, it does not guarantee the property
    exists in an Object.

    \param [in] geoProp
    \return The name of the corresponding range geo property (appends sIndexSuffix).
*/
Amino::String BIFROST_GEOMETRY_DECL getGeoPropRangeName(Amino::StringView geoProp);
///@}

// -----------------------------------------------------------------------------
// General Geometry Property functions

/// \defgroup GeoPropertyFunctions Various GeoProperty Functions
/// \brief Functions for helping find GeoProperties.
///@{

/*! \brief Given a prototype, ex.: a geo property prototype (component, range, or data),
    return an array of objects that match the input prototype.
    \param [in] object The object that will be searched.
    \param [in] prototype The object propertype that serves as search criterion.
    \return Array of matching objects.
*/
Amino::Array<Amino::Ptr<Bifrost::Object>> BIFROST_GEOMETRY_DECL
getGeoPropsByPrototype(Bifrost::Object const& object, Bifrost::Object const& prototype);

/*! \brief Given a target string, return an array of geo prop objects that have that target.
    \param [in] object The object that will be searched.
    \param [in] target string that as search criterion.
    \return Array of matching objects.
*/
Amino::Array<Amino::Ptr<Bifrost::Object>> BIFROST_GEOMETRY_DECL
getGeoPropsByTarget(Bifrost::Object const& object, Amino::StringView target);

/*! \brief Given a prototype, ex.: a geo property prototype (component, range, or data),
    return an array of property keys that match the input prototype.
    \param [in] object The object that will be searched.
    \param [in] prototype The object propertype that serves as search criterion.
    \return Array of matching property keys.
*/
Amino::Array<Amino::String> BIFROST_GEOMETRY_DECL
getGeoPropNamesByPrototype(Bifrost::Object const& object, Bifrost::Object const& prototype);

/*! \brief Given a target string, return an array of property keys that have that target.
    \param [in] object The object that will be searched.
    \param [in] target string that as search criterion.
    \return Array of matching property keys.
*/
Amino::Array<Amino::String> BIFROST_GEOMETRY_DECL
getGeoPropNamesByTarget(Bifrost::Object const& object, Amino::StringView target);

/*! \brief Given a pattern, return an array of property keys that have that pattern.
    \param [in] object The object that will be searched.
    \param [in] pattern string search criterion.
    \return Array of matching property keys.
*/
Amino::Array<Amino::String> BIFROST_GEOMETRY_DECL getGeoPropsByName(Bifrost::Object const& object,
                                                                    Amino::StringView      pattern);

/*! \brief Given a name, return a name that is similar but unique to the specified object.
    \param [in] propertyName The name to unique-ify.
    \param [in] object The object to check against.
    \return A property name that is not used by any other property in object. If the property
    name is already unused, then it is returned unchanged.
*/
Amino::String BIFROST_GEOMETRY_DECL getUniqueGeoPropName(Amino::StringView      propertyName,
                                                         Bifrost::Object const& object);
///@}

///@}

} // namespace Geometry
} // namespace Bifrost

#endif // BIFROST_GEO_PROPERTY_H

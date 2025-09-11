//-
//*****************************************************************************
// Copyright 2024 Autodesk, Inc.
// All rights reserved.
//
// These coded instructions, statements, and computer programs contain
// unpublished proprietary information written by Autodesk, Inc. and are
// protected by Federal copyright law. They may not be disclosed to third
// parties or copied or duplicated in any form, in whole or in part, without
// the prior written consent of Autodesk, Inc.
//*****************************************************************************
//+

/// \file GeoPropertyGuard.h

#ifndef BIFROST_GEOMETRY_GEO_PROPERTY_GUARD_H
#define BIFROST_GEOMETRY_GEO_PROPERTY_GUARD_H

#include <Bifrost/Geometry/GeometryExport.h>

#include <Bifrost/Geometry/GeoProperty.h> // DataInterpolationMode
#include <Bifrost/Math/Types.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Core/StringView.h>

namespace Bifrost {

template <typename T>
class PropertyGuard;

/// \brief Check if an object has a property with type `T` and name `propertyName`.
/// \param [in] object The input object.
/// \param [in] propertyName The name of the property to check for.
/// \return true if `object` has a property with type `T` and name `propertyName`.
template <typename T>
bool hasProperty(const Bifrost::Object& object, Amino::StringView propertyName);

/// \brief Create a PropertyGuard for the given object and property name.
/// \param [in,out] object The input object.
/// \param [in] propertyName The name of the property to extract.
/// \return A `PropertyGuard` RAII class that extracts the property with type `T` and name
/// `propertyName` from `object` and sets the property back when the guard is destructed.
template <typename T>
PropertyGuard<T> createPropGuard(Bifrost::Object& object, Amino::StringView propertyName);

/// \brief Create a PropertyGuard for an Amino::Ptr<T> property.
/// \param [in,out] object The input object.
/// \param [in] propertyName The name of the property to extract.
/// \return A `PropertyGuard` RAII class that extracts the property with type `Amino::Ptr<T>` and
/// name `propertyName` from `object` and sets the property back when the guard is destructed.
template <typename T>
PropertyGuard<Amino::Ptr<T>> createPtrPropGuard(Bifrost::Object&  object,
                                                Amino::StringView propertyName);

} // namespace Bifrost

namespace Bifrost {
namespace Geometry {

template <typename T>
class DataGeoPropertyGuard;

class RangeGeoPropertyGuard;

/// \brief Check if a geometry object has a valid geo property with type `T` and name `property`.
/// \param [in] geometry The input geometry.
/// \param [in] property The name of the geometry property to check for.
/// \tparam T The data type of the geo property.
/// \return true if `geometry` has a valid geometry property with type `T` and name `property`.
template <typename T>
bool hasDataGeoProperty(const Bifrost::Object& geometry, Amino::StringView property);

/// \brief Create a DataGeoPropertyGuard for the specified geo property.
/// \param [in,out] geometry The input Bifrost geometry object.
/// \param [in] propertyName The name of the property to extract.
/// \tparam T The data type of the geo property.
/// \return A `DataGeoPropertyGuard` RAII class that extracts the geometry property with type `T`
/// and name `propertyName` from `object` and sets the property back when the guard is destructed.
/// If the geo property does not exist in the geometry, the returned guard's boolean cast operator
/// will return false.
template <typename T>
DataGeoPropertyGuard<T> createDataGeoPropGuard(Bifrost::Object&  geometry,
                                               Amino::StringView propertyName);

/// \brief Check if a geometry object has a valid Range geo property with name `property`.
/// \param [in] geometry The input geometry.
/// \param [in] property The name of the Range geo property to check for.
/// \return true if `geometry` has a valid Range geo property with name `property`.
BIFROST_GEOMETRY_DECL
bool hasRangeGeoProperty(const Bifrost::Object& geometry, Amino::StringView property);

/// \brief Create a RangeGeoPropertyGuard for the specified range geo property.
/// \param [in,out] geometry The input Bifrost geometry object.
/// \param [in] propertyName The name of the property to extract.
/// \return A `RangeGeoPropertyGuard` RAII class that extracts the geometry property with type `T`
/// and name `propertyName` from `object` and sets the property back when the guard is destructed.
/// If the geo property does not exist in the geometry, the returned guard's boolean cast operator
/// will return false.
BIFROST_GEOMETRY_DECL
RangeGeoPropertyGuard createRangeGeoPropGuard(Bifrost::Object&  geometry,
                                              Amino::StringView propertyName);

} // namespace Geometry
} // namespace Bifrost

///////////////////////////////////////////////////////////////////////////////
// Implementation:
///////////////////////////////////////////////////////////////////////////////

namespace Bifrost {

template <typename T>
bool hasProperty(const Bifrost::Object& object, Amino::StringView propertyName) {
    auto any = object.getProperty(propertyName);
    return any.type() == Amino::Any{T{}}.type();
}

template <typename T>
PropertyGuard<T> createPropGuard(Bifrost::Object& object, Amino::StringView propertyName) {
    return hasProperty<T>(object, propertyName)
               ? PropertyGuard<T>(object, Amino::String(propertyName))
               : PropertyGuard<T>{};
}

template <typename T>
PropertyGuard<Amino::Ptr<T>> createPtrPropGuard(Bifrost::Object&  object,
                                                Amino::StringView propertyName) {
    return createPropGuard<Amino::Ptr<T>>(object, propertyName);
}

// -----------------------------------------------------------------------------
/// \class PropertyGuard GeoPropertyGuard.h
/// \brief This class is a RAII guard for a Bifrost::Object property.
/// \tparam T The data type of the property.
///
/// This class is used to extract, modify and then set back a property value within a
/// Bifrost::object. This is the preferred method to modify a property of an Object since extracting
/// the property does not increase its reference count, and thus if there are no other references to
/// the value, it will be modified in-place and no copy-on-write will occur. See Amino::Ptr for more
/// details on reference counting.
///
/// Do not construct a PropertyGuarddirectly. Use Bifrost::createPropGuard instead.
template <typename T>
class PropertyGuard {
public:
    /// \brief Creates an invalid guard.
    PropertyGuard() = default;

    /// \brief Destroyes the guard and sets the property value back into the Object.
    ~PropertyGuard() {
        if (m_object != nullptr) {
            m_object->setProperty(m_propertyName, std::move(m_property));
        }
    }

    /// \brief Copy constructor is deleted.
    PropertyGuard(const PropertyGuard&) = delete;
    PropertyGuard& operator=(const PropertyGuard&) = delete;

    /// \brief Moving a guard is allowed.
    PropertyGuard(PropertyGuard&& io) noexcept
    : m_object(std::exchange(io.m_object, nullptr))
    , m_propertyName(std::move(io.m_propertyName))
    , m_property(std::move(io.m_property))
    {
    }

    /// \copydoc Bifrost::PropertyGuard::PropertyGuard(PropertyGuard&&)
    PropertyGuard& operator=(PropertyGuard&& io) noexcept
    {
        if (this != &io) {
            m_object = std::exchange(io.m_object, nullptr);
            m_propertyName = std::move(io.m_propertyName);
            m_property = std::move(io.m_property);
        }
        return *this;
    }

    /// \brief Check if this PropertyGuard has acquired a property.
    explicit operator bool() const noexcept { return m_object != nullptr; }

    /// \brief Returns the value of the property.
    const T& operator*() const noexcept {
        assert(m_object != nullptr);
        return m_property;
    }

    /// \copydoc Bifrost::PropertyGuard::operator*() const noexcept
    T& operator*() noexcept {
        assert(m_object != nullptr);
        return m_property;
    }

    /// \brief Returns a pointer to the property.
    const T* operator->() const noexcept {
        assert(m_object != nullptr);
        return &m_property;
    }

    /// \copydoc Bifrost::PropertyGuard::operator->() const noexcept
    T* operator->() noexcept {
        assert(m_object != nullptr);
        return &m_property;
    }

private:
    friend PropertyGuard<T> createPropGuard<T>(Bifrost::Object&, Amino::StringView);

    PropertyGuard(Bifrost::Object& object, Amino::String propertyName)
        : m_object(&object), m_propertyName(std::move(propertyName)) {
        auto any = m_object->extractProperty(m_propertyName);
        m_property = Amino::any_cast<T>(std::move(any));
    }

    Bifrost::Object* m_object = nullptr;
    Amino::String m_propertyName;
    T m_property;
};

/// \brief Specialization of PropertyGuard for Amino::Ptr<T>.
template <typename T>
class PropertyGuard<Amino::Ptr<T>> {
public:
    PropertyGuard() = default;

    ~PropertyGuard() {
        if (m_object != nullptr) {
            m_object->setProperty(m_propertyName, std::move(m_property));
        }
    }

    PropertyGuard(const PropertyGuard&) = delete;
    PropertyGuard& operator=(const PropertyGuard&) = delete;

    PropertyGuard(PropertyGuard&& io) noexcept
    : m_object(std::exchange(io.m_object, nullptr))
    , m_propertyName(std::move(io.m_propertyName))
    , m_property(std::move(io.m_property))
    {
    }

    PropertyGuard& operator=(PropertyGuard&& io) noexcept
    {
        if (this != &io) {
            m_object = std::exchange(io.m_object, nullptr);
            m_propertyName = std::move(io.m_propertyName);
            m_property = std::move(io.m_property);
        }
        return *this;
    }

    explicit operator bool() const noexcept { return m_object != nullptr; }

    const T& operator*() const noexcept {
        assert(m_object != nullptr);
        return *m_property;
    }

    T& operator*() noexcept {
        assert(m_object != nullptr);
        return *m_property;
    }

    const T* operator->() const noexcept {
        assert(m_object != nullptr);
        return m_property.get();
    }

    T* operator->() noexcept {
        assert(m_object != nullptr);
        return m_property.get();
    }

private:
    friend PropertyGuard<Amino::Ptr<T>> createPropGuard<Amino::Ptr<T>>(Bifrost::Object&,
                                                                       Amino::StringView);
    friend PropertyGuard<Amino::Ptr<T>> createPtrPropGuard<T>(Bifrost::Object&, Amino::StringView);

    PropertyGuard(Bifrost::Object& object, Amino::String propertyName)
        : m_object(&object), m_propertyName(std::move(propertyName)) {
        auto any = m_object->extractProperty(m_propertyName);
        auto constProp = Amino::any_cast<Amino::Ptr<T>>(std::move(any));
        m_property = constProp.toMutable();
    }

    Bifrost::Object* m_object = nullptr;
    Amino::String m_propertyName;
    Amino::MutablePtr<T> m_property;
};

} // namespace Bifrost

namespace Bifrost {
namespace Geometry {

// -----------------------------------------------------------------------------
template <typename T>
bool hasDataGeoProperty(const Bifrost::Object& geometry, Amino::StringView property) {
    // Check if the property exists and matches the Data geo property schema
    auto propObj = Bifrost::Geometry::getDataGeoProperty(geometry, property);
    if (!propObj) return false;

    // Check the data type matches
    auto dataArray = Bifrost::Geometry::getDataGeoPropValues<T>(geometry, property);
    return dataArray != nullptr;
}

// -----------------------------------------------------------------------------
/// \class DataGeoPropertyGuard GeoPropertyGuard.h
/// \brief This class is a RAII guard for a Data geo property.
/// \tparam T The data type of the geo property.
///
/// This class is used to extract, modify and then set back a Data geo property value within a
/// geometry object. This is the preferred method to modify the geo properties of a geometry since
/// extracting the geo property does not increase its reference count, and thus if there are no
/// other references to the value, it will be modified in-place and no copy-on-write will occur.
/// See Amino::Ptr for more details on reference counting.
///
/// Do not construct a DataGeoProperty guard directly. Use Bifrost::Geometry::createDataGeoPropGuard
/// instead.
///
/// \code
/// {
///     // Extract the point positions from the mesh.
///     auto pointPositions = Bifrost::Geometry::createDataGeoPropGuard<Bifrost::Math::float3>(
///         mesh, Bifrost::Geometry::sPointPosition);
///
///     // Translate the points along the y-axis by one unit.
///     std::transform(pointPositions.data().begin(), pointPositions.data().end(),
///         [](auto& pos) { return pos.y += 1.0f; });
///
/// } // At this point the guard is destroyed and the positions are set back into the mesh.
/// \endcode
template <typename T>
class DataGeoPropertyGuard
{
public:
    /// \brief Constructor.
    DataGeoPropertyGuard() = default;

    /// \brief Returns true if the guard has acquired a geo property.
    explicit operator bool() const noexcept { return static_cast<bool>(m_property); }

    /// \brief Returns the data array of the geo property.
    /// \pre This guard has already acquired a geo property.
    const Amino::Array<T>& data() const noexcept { return *m_data; }

    /// \copydoc Bifrost::Geometry::DataGeoPropertyGuard::data() const
    Amino::Array<T>& data() noexcept { return *m_data; }

    /// \brief Returns the target of the geo property.
    /// \pre This guard has already acquired a geo property.
    const Amino::String& target() const noexcept { return *m_target; }

    /// \copydoc Bifrost::Geometry::DataGeoPropertyGuard::target() const
    Amino::String& target() noexcept { return *m_target; }

    /// \brief Returns the value of the depends_on field in the geo property.
    /// \pre This guard has already acquired a geo property.
    const Amino::Array<Amino::String>& dependsOn() const noexcept { return *m_dependsOn; }

    /// \copydoc Bifrost::Geometry::DataGeoPropertyGuard::dependsOn() const
    Amino::Array<Amino::String>& dependsOn() noexcept { return *m_dependsOn; }

    /// \brief Returns the default value of the geo property.
    /// \pre This guard has already acquired a geo property.
    const T& defaultValue() const noexcept { return *m_defaultValue; }

    /// \copydoc Bifrost::Geometry::DataGeoPropertyGuard::defaultValue() const
    T& defaultValue() noexcept { return *m_defaultValue; }

    /// \brief Returns the interpolation_mode field in the geo property.
    /// \pre This guard has already acquired a geo property.
    const Bifrost::Geometry::Common::DataInterpolationMode& interpolationMode() const noexcept {
        return *m_interp;
    }

    /// \copydoc Bifrost::Geometry::DataGeoPropertyGuard::interpolationMode() const
    Bifrost::Geometry::Common::DataInterpolationMode& interpolationMode() noexcept {
        return *m_interp;
    }

private:
    friend DataGeoPropertyGuard<T> createDataGeoPropGuard<T>(Bifrost::Object&, Amino::StringView);

    DataGeoPropertyGuard(Bifrost::Object& object, Amino::StringView propertyName)
        : m_property(createPtrPropGuard<Bifrost::Object>(object, propertyName)),
          m_data(createPtrPropGuard<Amino::Array<T>>(*m_property, Bifrost::Geometry::sData)),
          m_target(createPropGuard<Amino::String>(*m_property, Bifrost::Geometry::sTarget)),
          m_dependsOn(createPtrPropGuard<Amino::Array<Amino::String>>(
              *m_property, Bifrost::Geometry::sDependsOn)),
          m_defaultValue(createPropGuard<T>(*m_property, Bifrost::Geometry::sDefault)),
          m_interp(createPropGuard<Bifrost::Geometry::Common::DataInterpolationMode>(
              *m_property, Bifrost::Geometry::sInterp)) {}

    PropertyGuard<Amino::Ptr<Bifrost::Object>> m_property;
    PropertyGuard<Amino::Ptr<Amino::Array<T>>> m_data;
    PropertyGuard<Amino::String> m_target;
    PropertyGuard<Amino::Ptr<Amino::Array<Amino::String>>> m_dependsOn;
    PropertyGuard<T> m_defaultValue;
    PropertyGuard<Bifrost::Geometry::Common::DataInterpolationMode> m_interp;
};

// -----------------------------------------------------------------------------
template <typename T>
DataGeoPropertyGuard<T> createDataGeoPropGuard(Bifrost::Object&  geometry,
                                               Amino::StringView propertyName) {
    return hasDataGeoProperty<T>(geometry, propertyName)
               ? DataGeoPropertyGuard<T>(geometry, propertyName)
               : DataGeoPropertyGuard<T>{};
}

// -----------------------------------------------------------------------------
/// \class RangeGeoPropertyGuard GeoPropertyGuard.h
/// \brief This class is a RAII guard for a Range geo property.
///
/// This class is used to extract, modify and then set back a Range geo property value within a
/// geometry object. This is the preferred method to modify the geo properties of a geometry since
/// extracting the geo property does not increase its reference count, and thus if there are no
/// other references to the value, it will be modified in-place and no copy-on-write will occur.
/// See Amino::Ptr for more details on reference counting.
///
/// Do not construct a RangeGeoProperty guard directly. Use
/// Bifrost::Geometry::createRangeGeoPropGuard instead.
///
/// \code
/// {
///     // Extract the point positions from the mesh.
///     auto uvIndices = Bifrost::Geometry::createRangeGeoPropGuard(mesh, "face_vertex_uv_index");
///
///     // As a trivial modification, swap the first and last indices.
///     std::swap(uvIndices.indices().front(), uvIndices.indices().back());
///
/// } // At this point the guard is destroyed and the uvIndices are set back into the mesh.
/// \endcode
class RangeGeoPropertyGuard {
public:
    /// \brief Constructor.
    RangeGeoPropertyGuard() = default;

    /// \brief Returns true if the guard has acquired a geo property.
    explicit operator bool() const noexcept { return static_cast<bool>(m_property); }

    /// \brief Returns the index array of the geo property.
    /// \pre This guard has already acquired a geo property.
    const Amino::Array<Bifrost::Geometry::Index>& indices() const noexcept { return *m_indices; }

    /// \copydoc RangeGeoPropertyGuard::indices() const
    Amino::Array<Bifrost::Geometry::Index>& indices() noexcept { return *m_indices; }

    /// \brief Returns the target of the geo property.
    /// \pre This guard has already acquired a geo property.
    const Amino::String& target() const noexcept { return *m_target; }

    /// \copydoc RangeGeoPropertyGuard::target() const
    Amino::String& target() noexcept { return *m_target; }

    /// \brief Returns the value of the depends_on field in the geo property.
    /// \pre This guard has already acquired a geo property.
    const Amino::Array<Amino::String>& dependsOn() const noexcept { return *m_dependsOn; }

    /// \copydoc RangeGeoPropertyGuard::dependsOn() const
    Amino::Array<Amino::String>& dependsOn() noexcept { return *m_dependsOn; }

private:
    /// \cond
    friend BIFROST_GEOMETRY_DECL RangeGeoPropertyGuard createRangeGeoPropGuard(Bifrost::Object&,
                                                                               Amino::StringView);
    /// \endcond

    RangeGeoPropertyGuard(Bifrost::Object& object, Amino::StringView propertyName)
        : m_property(createPtrPropGuard<Bifrost::Object>(object, propertyName)),
          m_indices(createPtrPropGuard<Amino::Array<Bifrost::Geometry::Index>>(
              *m_property, Bifrost::Geometry::sIndices)),
          m_target(createPropGuard<Amino::String>(*m_property, Bifrost::Geometry::sTarget)),
          m_dependsOn(createPtrPropGuard<Amino::Array<Amino::String>>(
              *m_property, Bifrost::Geometry::sDependsOn)) {}

    PropertyGuard<Amino::Ptr<Bifrost::Object>>                        m_property;
    PropertyGuard<Amino::Ptr<Amino::Array<Bifrost::Geometry::Index>>> m_indices;
    PropertyGuard<Amino::String>                                      m_target;
    PropertyGuard<Amino::Ptr<Amino::Array<Amino::String>>>            m_dependsOn;
};

} // namespace Geometry
} // namespace Bifrost

#endif // BIFROST_GEOMETRY_GEO_PROPERTY_GUARD_H

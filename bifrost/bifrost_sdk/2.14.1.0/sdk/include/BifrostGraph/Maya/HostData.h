//-
//**************************************************************************/
// Copyright 2023 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk
// license agreement provided at the time of installation or download,
// or which otherwise accompanies this software in either electronic
// or hard copy form.
//**************************************************************************/
//+

/// \file HostData.h
/// \brief Bifrost to and from Maya data conversion support.
/// \note The contents of this file belong to a feature that is still
/// under development, and they may change in subsequent versions.

#ifndef MAYA_HOST_DATA_H_
#define MAYA_HOST_DATA_H_

#include "MayaExport.h"

#include <maya/MDagModifier.h>
#include <maya/MDataBlock.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MTypeId.h>

#include <Amino/Core/Ptr.h>

#include <BifrostGraph/Executor/TypeTranslation.h>

namespace Amino {
class MetadataItem;
class Value;
} // namespace Amino

namespace BifrostGraph {
namespace MayaTranslation {

/// \brief Translation data used to pass Maya data between compute node and
/// converter.
/// \note This will be created by Maya and send to converter.
/// \see BifrostGraph::Executor::TypeTranslation::convertValueFromHost()
/// \see BifrostGraph::Executor::TypeTranslation::convertValueToHost()
/// \note This class belongs to a feature that is still
/// under development and may change in subsequent versions.
class MAYA_HOST_DATA_SHARED_DECL ValueData final
    : public BifrostGraph::Executor::TypeTranslation::ValueData {
public:
    /// \brief Constructor always called by maya.
    /// User should not create the object itself.
    /// \param plug The plug attribute for which data should be read/written.
    /// \param block Data block of the node holding the plug
    /// \param extraHandle RESERVED FOR INTERNAL USE
    /// \param cachedValue RESERVED FOR INTERNAL USE
    /// \param inputPathOpts Input by path option.
    ValueData(MPlug const&                  plug,
              MDataBlock&                   block,
              void*&                        extraHandle,
              Amino::Ptr<Amino::Any> const& cachedValue,
              Amino::MetadataItem const*    inputPathOpts = nullptr)
        : BifrostGraph::Executor::TypeTranslation::ValueData(),
          m_plug(plug),
          m_block(block),
          m_inputPathOpts(inputPathOpts),
          m_extraHandle(extraHandle),
          m_cachedValue(cachedValue) {}

    /// \brief Destructor always called by maya.
    /// User should not destroy the object itself.
    ~ValueData() final;

    /// \brief Enforce the correct usage of this object by disallowing
    // copy constructor and assignment operator
    /// \{
    ValueData& operator=(const ValueData&) = delete;
    ValueData(const ValueData&)            = delete;
    /// \}

    /// \return The plug attribute for which data should be read/written.
    inline const MPlug& getPlug() const { return m_plug; }

    /// \return Data block of the node holding the plug.
    /// \note: We need to store and return a non-const MDataBlock reference
    /// because the class MDataBlock has no const methods.
    inline MDataBlock& getDataBlock() const { return m_block; }

    /// \return The input path options.
    inline const Amino::MetadataItem* getInputPathOptions() const { return m_inputPathOpts; }

    /// \internal RESERVED FOR INTERNAL USE
    inline void*& getExtraHandle() const { return m_extraHandle; }

    /// \internal RESERVED FOR INTERNAL USE
    inline const Amino::Ptr<Amino::Any>& getCachedValue() const { return m_cachedValue; }

private:
    MPlug const& m_plug;  ///< Plug which data should be read/written
    MDataBlock&  m_block; ///< Data block holding plugs data

    const Amino::MetadataItem* m_inputPathOpts; //!< Input path options

    /// \internal RESERVED FOR INTERNAL USE
    void*& m_extraHandle;

    /// \internal RESERVED FOR INTERNAL USE
    Amino::Ptr<Amino::Any> const& m_cachedValue;
};

/// \brief Translation data used to create the Maya attribute when a
/// graph I/O (top level compound) is added.
/// \see BifrostGraph::Executor::TypeTranslation::portAdded
/// \note This also apply to auto-created job ports.
/// \note This class belongs to a feature that is still
/// under development and may change in subsequent versions.
class MAYA_HOST_DATA_SHARED_DECL PortData
    : public BifrostGraph::Executor::TypeTranslation::PortData {
public:
    /// \brief Constructor always called by maya.
    /// User should not create the object itself.
    /// \param object The maya dependency node.
    /// \param id The MTypeId of the object.
    PortData(MObject const& object, MTypeId const& id)
        : BifrostGraph::Executor::TypeTranslation::PortData(), m_object(object), m_id(id) {}

    /// \brief Copy constructor.
    /// \param other The PortData to copy into this one.
    PortData(PortData const& other)
        : BifrostGraph::Executor::TypeTranslation::PortData(),
          m_object(other.m_object),
          m_id(other.m_id) {}

    /// \brief Destructor always called by maya.
    /// User should not destroy the object itself.
    ~PortData() override;

private:
    PortData& operator=(const PortData&) = delete;

public:
    /// \brief The maya dependency node.
    MObject const m_object;

    /// \brief The MTypeId of m_object.
    MTypeId const m_id;
};

/// \brief Translation data used to create Maya ports.
/// This will be created by Maya.
/// \see BifrostGraph::Executor::TypeTranslation::portAdded
/// \note This class belongs to a feature that is still
/// under development and may change in subsequent versions.
class MAYA_HOST_DATA_SHARED_DECL PortCreationData final : public PortData {
public:
    /// \brief Mode to know if we are converting and to what
    enum class ConversionMode {
        kNone,              ///< Not converting node to anything
        kConversionToShape, ///< Converting to a bifrostGraphShape node
        kConversionToBoard  ///< Converting to a bifrostBoard node
    };

    /// \brief To know if we are converting and to what
    struct ConversionData {
        ConversionMode m_conversionMode{ConversionMode::kNone};
        Amino::String  m_convertFromNodeName{""};
        Amino::String  m_convertFromNodeUUID{""};
    };

public:
    /// \brief Constructor always called by maya.
    /// User should not create the object itself.
    /// \param translationData Translation data used to convert values from/to Maya.
    /// \param modifier The Maya modifier to use to do DG operations.
    /// \param conversionData The conversion data involving the port creation.
    PortCreationData(PortData const&       translationData,
                     MDGModifier&          modifier,
                     ConversionData const& conversionData)
        : PortData(translationData), m_modifier(modifier), m_conversionData(conversionData) {}

    /// \brief Destructor always called by maya.
    /// User should not destroy the object itself.
    ~PortCreationData() final;

private:
    PortCreationData& operator=(const PortCreationData&) = delete;

public:
    /// \brief The modifier to use to do DG operations, so they can be undo and
    /// redone.
    MDGModifier& m_modifier;
    /// \brief The conversion data involving the port creation.
    ConversionData const& m_conversionData;
};

/// \brief Data used to initialize translation tables against the plugin.
/// This will be created by Maya.
/// \see BifrostGraph::Executor::TypeTranslation::registerHostPlugins
/// \see BifrostGraph::Executor::TypeTranslation::unregisterHostPlugins
/// \note This class belongs to a feature that is still
/// under development and may change in subsequent versions.
class MAYA_HOST_DATA_SHARED_DECL PluginHostData final
    : public BifrostGraph::Executor::TypeTranslation::PluginHostData {
public:
    /// \brief Constructor always called by maya.
    /// User should not create the object itself.
    /// \param object The MObject representing the maya plugin.
    explicit PluginHostData(MObject& object)
        : BifrostGraph::Executor::TypeTranslation::PluginHostData(),
          m_object(object) {}

    /// \brief Destructor always called by maya.
    /// User should not destroy the object itself.
    ~PluginHostData() final;

public:
    /// \brief The MObject representing the maya plugin.
    /// This can be use with MFnPlugin.
    MObject const m_object;
};

} // namespace MayaTranslation
} // namespace BifrostGraph

#endif

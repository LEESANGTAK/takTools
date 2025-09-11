//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file TypeTranslation.h
/// \brief BifrostGraph Executor TypeTranslation.
/// \note The contents of this file belong to a feature that is still
/// under development, and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_TYPE_TRANSLATION_H
#define BIFROSTGRAPH_EXECUTOR_TYPE_TRANSLATION_H

#include <BifrostGraph/Executor/internal/ExecutorExport.h>

#include <BifrostGraph/Executor/Types.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/String.h>

namespace Amino {
class Any;
class Library;
class Metadata;
class Type;
class Value;

template <typename E>
class EntityIndexedList;

typedef EntityIndexedList<const Type> TypeConstIndexedList;
} // namespace Amino

namespace BifrostGraph {
namespace Executor {

/// \ingroup BifrostGraphExecutor

/// \brief BifrostGraph Executor TypeTranslation
///
/// TypeTranslation can be used to perform conversions from specific host data types to Amino
/// types, and vice-versa.
///
/// A TypeTranslation should be allocated on the heap, not on the stack.
/// The \ref Workspace will manage its lifetime and delete it by calling
/// \ref TypeTranslation::deleteThis when the Workspace gets unloaded.
///
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL TypeTranslation {
public:
    using String      = Amino::String;
    using StringArray = Amino::Array<String>;

    /// \brief The host data for translating values from/to host/Amino.
    /// \note This class belongs to a feature that is still
    /// under development and may change in subsequent versions.
    class BIFROSTGRAPH_EXECUTOR_SHARED_DECL ValueData {
    public:
        ValueData() noexcept;
        virtual ~ValueData() noexcept;
    };

    /// \brief The host data for creating host ports.
    /// \note This class belongs to a feature that is still
    /// under development and may change in subsequent versions.
    class BIFROSTGRAPH_EXECUTOR_SHARED_DECL PortData {
    public:
        PortData() noexcept;
        virtual ~PortData() noexcept;
    };

    /// \brief The host data for registering TypeTranslation to host plugin.
    /// \note This class belongs to a feature that is still
    /// under development and may change in subsequent versions.
    class BIFROSTGRAPH_EXECUTOR_SHARED_DECL PluginHostData {
    public:
        PluginHostData() noexcept;
        virtual ~PluginHostData() noexcept;
    };

public:
    /// \brief Constructor
    /// \param [in] name The name of this TypeTranslation for logging purposes.
    explicit TypeTranslation(String name) noexcept;

    /// \brief Destructor.
    virtual ~TypeTranslation() noexcept;

    /// \brief Get the name of this TypeTranslation for logging purposes.
    /// \return The name of this TypeTranslation
    String getName() const noexcept;

    /// \brief The signature of the function used to create the TypeTranslation.
    using CreateFunc = TypeTranslation* (*)();

    /// \brief Get the name of the function used to create a new TypeTranslation from
    /// a shared library.
    ///
    /// This function is the C entry point used to register a TypeTranslation
    /// with Bifrost. The client code must declare and define the entry point.
    /// This function must have the CreateFunc signature.
    ///
    /// Note that `BIFROSTGRAPH_EXECUTOR_SHARED_DECL` is for symbol visiblity,
    /// see ExecutorExport.h file.
    ///
    /// \code {.cpp}
    /// extern "C" {
    /// BIFROSTGRAPH_EXECUTOR_SHARED_DECL BifrostGraph::Executor::TypeTranslation*
    /// createBifrostTypeTranslation(void);
    ///
    /// BIFROSTGRAPH_EXECUTOR_SHARED_DECL BifrostGraph::Executor::TypeTranslation*
    /// createBifrostTypeTranslation(void) {
    ///     // Return a pointer to my class that implements
    ///     // BifrostGraph::Executor::TypeTranslation interface.
    ///     return new MyTypeTranslation();
    /// }
    /// \endcode
    ///
    /// The TypeTranslation shared library is exposed to Bifrost via
    /// a config file. The JSON config file will need a `typesTranslationlibs`
    /// section. Note that, to be portable and depending on the platform,
    /// Bifrost config file parsing will automatically add the prefix "lib" and
    /// suffix  "dll", "so", or "dylib".
    ///
    /// \code{.json}
    /// {
    ///     "AminoConfigurations": [
    ///         {
    ///             "vendorName": "MyCompany",
    ///             "libraryVersion": "0.0.1",
    ///             "libraryName": "MyPackName",
    ///             "typesTranslationlibs": [
    ///                 {
    ///                     "path": "Directory containing the shared lib",
    ///                     "files": [
    ///                         "MyTypeTranslation"
    ///                     ]
    ///                 }
    ///             ]
    ///         }
    ///     ]
    /// }
    /// \endcode
    ///
    /// \return "createBifrostTypeTranslation"
    static const char* createFuncName() noexcept;

    /// \brief Instruct the TypeTranslation to delete itself.
    virtual void deleteThis() noexcept = 0;

    /// \brief Get the list of the types handled by this TypeTranslation.
    ///
    /// \details The Workspace will call this method and \ref getSupportedTypeNames, in this order,
    /// to build the complete list of types handled by this TypeTranslation.
    /// The default implementation of this method adds no type to \p types.
    /// The deriving class may override this default implementation to list the types it handles,
    /// and it may complement these types by listing extra ones in its implementation of
    /// \ref getSupportedTypeNames.
    /// If the same type is listed by both this method and by \ref getSupportedTypeNames, the
    /// duplicate listed by \ref getSupportedTypeNames is ignored.
    ///
    /// \param [in]  amLibrary The Amino Library
    /// \param [out] types The types handled by this TypeTranslation.
    virtual void getSupportedTypes(const Amino::Library&        amLibrary,
                                   Amino::TypeConstIndexedList& types) const noexcept;

    /// \brief Get the fully qualified names of the types handled by the TypeTranslation.
    ///
    /// \details The Workspace will call \ref getSupportedTypes and this method, in this order,
    /// to build the complete list of types handled by this TypeTranslation.
    /// The default implementation of this method adds no type name to \p names.
    /// The deriving class may override this default implementation to list the fully qualified
    /// names of the types it handles, in addition to the types it may have listed in its
    /// implementation of \ref getSupportedTypes.
    /// If the same type name is listed more than once by this method, or if a type name listed by
    /// this method was already listed by \ref getSupportedTypes, these duplicates are ignored.
    ///
    /// \param [out] names The fully qualified names of the types handled by this
    /// TypeTranslation.
    virtual void getSupportedTypeNames(StringArray& names) const noexcept;

    /// \brief Convert a host value to an Amino::Any.
    /// \note Default implementation does nothing and returns false.
    ///
    /// \param [in]  type       The Amino value type.
    /// \param [out] any        The destination Amino::Any.
    /// \param [in]  valueData  A pointer to a ValueData instance, used to access the host value.
    /// \return true if the value was successfully converted.
    virtual bool convertValueFromHost(const Amino::Type& type,
                                      Amino::Any&        any,
                                      const ValueData*   valueData) const noexcept;

    /// \brief Convert an Amino::Any to a host value.
    /// \note Default implementation does nothing and returns false.
    ///
    /// \param [in]     any         The source Amino::Any.
    /// \param [in,out] valueData   A pointer to a ValueData instance, used to access the host value.
    /// \return true if the value was successfully converted.
    virtual bool convertValueToHost(const Amino::Any& any, ValueData* valueData) const noexcept;

    /// \brief Notification method called when a port is created/added.
    /// \note Default implementation does nothing and returns true.
    ///
    /// \param [in] name      The name of the port.
    /// \param [in] direction The direction of the port (undefined, input or output).
    /// \param [in] type      The type of the port.
    /// \param [in] portClass The class of the port (regular, terminal or job port).
    /// \param [in] metadata  Metadata for the port.
    /// \param [in] portData  A pointer to a PortData instance, used to create the host port.
    /// \return true if the host port was successfully created.
    virtual bool portAdded(const String&          name,
                           PortDirection          direction,
                           const Amino::Type&     type,
                           const Amino::Metadata& metadata,
                           PortClass              portClass,
                           PortData*              portData) const noexcept;

    /// \brief Notification method called when a port is removed.
    /// \note Default implementation does nothing and returns true.
    ///
    /// \param [in] name  The name of the port to be removed.
    /// \param [in] graphName  The name of the graph that has this port.
    /// \return true if the host port was successfully removed.
    virtual bool portRemoved(const String& name, const String& graphName) const noexcept;

    /// \brief Notification method called when a port is renamed.
    /// \note Default implementation does nothing and returns true.
    ///
    /// \param [in] prevName  The previous name of the port.
    /// \param [in] name      The new name of the port.
    /// \param [in] graphName  The name of the graph that has this port.
    /// \return true if the host port was successfully renamed.
    virtual bool portRenamed(const String& prevName,
                             const String& name,
                             const String& graphName) const noexcept;

    /// \brief Register any plugins or data types needed.
    /// \note Default implementation does nothing and returns true.
    ///
    /// \param [in] pluginData The host data.
    /// \return true on success, false otherwise.
    virtual bool registerHostPlugins(const PluginHostData* pluginData) const noexcept;

    /// \brief Unregister any previously registered plugins or data types.
    /// \note Default implementation does nothing and returns true.
    ///
    /// \param [in] pluginData The host data.
    /// \return true on success, false otherwise.
    virtual bool unregisterHostPlugins(const PluginHostData* pluginData) const noexcept;

private:
    /// Disabled
    /// \{
    TypeTranslation(const TypeTranslation&)             = delete;
    TypeTranslation(TypeTranslation&&)                  = delete;
    TypeTranslation& operator=(const TypeTranslation&)  = delete;
    TypeTranslation& operator=(TypeTranslation&&)       = delete;
    /// \}

    /// The name of this TypeTranslation for logging purposes.
    String m_name;
};

} // namespace Executor
} // namespace BifrostGraph
#endif

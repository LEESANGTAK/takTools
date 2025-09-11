//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file Watchpoint.h
/// \brief BifrostGraph Executor Watchpoint.
/// \note The contents of this file belong to a feature that is still
/// under development, and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_WATCHPOINT_H
#define BIFROSTGRAPH_EXECUTOR_WATCHPOINT_H

#include <BifrostGraph/Executor/internal/ExecutorExport.h>

#include <Amino/Core/Any.h>
#include <Amino/Core/Array.h>
#include <Amino/Core/BuiltInTypes.h>
#include <Amino/Core/String.h>
#include <Amino/Core/TypeId.h>

#if defined(_MSC_VER)
/// \note The deprecation warning is disabled on MSC because it leads to an
///       error being reported which causes the entire build to fail. This is
///       due to the presence of the "warning as errors (/WX)" flag. There
///       doesn't seem to be a way to turn off the warning as errors for a
///       single specific warning.
#define WATCHPOINT_DEPRECATED(REASON)
#elif defined(__clang__)
#define WATCHPOINT_DEPRECATED(REASON) [[deprecated(REASON)]]
#elif defined(__GNUC__)
#define WATCHPOINT_DEPRECATED(REASON) __attribute__((deprecated))
#else
#define WATCHPOINT_DEPRECATED(REASON)
#endif

namespace Amino {
class Any;
class Type;
class WatchPoint;
} // namespace Amino

namespace BifrostGraph {
namespace Executor {

class WatchpointLayoutFactory;
class WatchpointLayoutPath;
class WatchpointLayoutPtr;

/// \ingroup BifrostGraphExecutor

/// \brief BifrostGraph Executor Watchpoint
///
/// Watchpoint can be used to handle watchpoint callback and data for specific data types.
/// If the Watchpoint is enabled when executing the Bifrost graph, the callback function
/// of the Watchpoint will be called when transferring the value of an incoming connection
/// to the port to which this Watchpoint belongs.
///
/// A Watchpoint should be allocated on the heap, not on the stack.
/// The \ref Workspace will manage its lifetime and delete it by calling
/// \ref Watchpoint::deleteThis when the Workspace gets unloaded.
///
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL Watchpoint {
public:
    using String      = Amino::String;
    using StringArray = Amino::Array<String>;
    using TypeIdArray = Amino::Array<Amino::TypeId>;

    /// \brief Constructor
    /// \param [in] name The name of this Watchpoint for logging purposes.
    explicit Watchpoint(String name) noexcept;

    /// \brief Destructor.
    virtual ~Watchpoint() noexcept;

    /// \brief Get the name of this Watchpoint for logging purposes.
    /// \return The name of this Watchpoint
    String getName() const noexcept;

    /// \brief The signature of the function used to create the Watchpoint.
    using CreateFunc = BifrostGraph::Executor::Watchpoint* (*)();

    /// \brief Get the name of the function used to create a new Watchpoint from a shared library.
    ///
    /// This function is the C entry point used to register watchpoints
    /// with Bifrost. The client code must declare and define the entry point.
    /// This function must have the CreateFunc signature.
    ///
    /// Note that `BIFROSTGRAPH_EXECUTOR_SHARED_DECL` is for symbol visiblity,
    /// see ExecutorExport.h file.
    ///
    /// \code {.cpp}
    /// extern "C" {
    /// BIFROSTGRAPH_EXECUTOR_SHARED_DECL BifrostGraph::Executor::Watchpoint*
    /// createBifrostWatchpoint(void)
    ///
    /// BIFROSTGRAPH_EXECUTOR_SHARED_DECL BifrostGraph::Executor::Watchpoint*
    /// createBifrostWatchpoint(void) {
    ///     // Return a pointer to my class that implements
    ///     // BifrostGraph::Executor::Watchpoint interface.
    ///     return new MyWatchpoints();
    /// }
    /// \endcode
    ///
    /// The Watchpoint shared library is exposed to Bifrost via
    /// a config file. The JSON config file will need a
    /// `watchPointsTranslationLibs` section. Note that, to be portable and
    /// depending on the platform, Bifrost config file parsing will
    /// automatically add the prefix "lib" and suffix  "dll", "so", or "dylib".
    ///
    /// \code{.json}
    /// {
    ///     "AminoConfigurations": [
    ///         {
    ///             "vendorName": "MyCompany",
    ///             "libraryVersion": "0.0.1",
    ///             "libraryName": "MyPackName",
    ///             "watchPointsTranslationLibs" : [
    ///                 {
    ///                     "path": "Directory containing the shared lib",
    ///                     "files": [
    ///                         "MyWatchpoint"
    ///                     ]
    ///                 }
    ///             ]
    ///         }
    ///     ]
    /// }
    /// \endcode
    ///
    /// \return "createBifrostWatchpoint"
    static const char* createFuncName() noexcept;

    /// \brief Instruct the Watchpoint to delete itself.
    virtual void deleteThis() noexcept = 0;

    /// \brief Get the fully qualified names of the types handled by the Watchpoint.
    /// \deprecated Use \ref getSupportedTypeIds instead.
    ///
    /// \details The Library will call this method  to build the list of types handled by this
    /// Watchpoint.
    /// The default implementation of this method adds no type name to \p names.
    /// The deriving class may override this default implementation to list the fully qualified
    /// names of the types it handles.
    ///
    /// \param [out] names The fully qualified names of the types handled by this Watchpoint.
    ///
    /// \note The default implementation leaves the output list \p names unchanged.
    WATCHPOINT_DEPRECATED("Use getSupportedTypeIds() instead.")
    virtual void getSupportedTypeNames(StringArray& names) const noexcept;

    /// \brief Get the list of the typeIds handled by this Watchpoint.
    ///
    /// \details The Library will call this method to build the list of typeIds handled by this
    /// Watchpoint.
    /// The default implementation of this method adds no typeId to \p typeIds.
    /// The deriving class may override this default implementation to list the typeIds it handles
    ///
    /// \param [out] typeIds The typeIds handled by this Watchpoint.
    virtual void getSupportedTypeIds(TypeIdArray& typeIds) const noexcept = 0;

    /// \brief Callback function signature.
    using CallBack = void (*)(const void*    clientData,
                              Amino::ulong_t locationID,
                              const void*    valueData);

    /// \brief Get the callback function for the given typeId.
    ///
    /// \param [in] typeId The typeId.
    /// \return The callback function or nullptr if typeId is not supported.
    virtual CallBack getCallBackFunction(const Amino::TypeId& typeId) const noexcept = 0;

    /// \brief Get the callback function for the given type.
    ///
    /// \param [in] type The Amino type.
    /// \return The callback function or nullptr if type is not supported.
    WATCHPOINT_DEPRECATED("Use getCallBackFunction(TypeId) instead.")
    virtual CallBack getCallBackFunction(const Amino::Type& type) const noexcept;

    /// \brief The interface to get the watchpoint layout and value.
    class BIFROSTGRAPH_EXECUTOR_SHARED_DECL Watcher {
    public:
        enum class Flags : unsigned { kNone = 0, kWithinALoop = 1 };

        Watcher() noexcept;
        virtual ~Watcher() noexcept;

        /// \brief Instruct the watcher to delete itself.
        virtual void deleteThis() noexcept = 0;

        /// \brief Get the layout for watched value.
        /// \param factory The layout factory, used to get/create nested layouts.
        /// \return A layout if current watched value in valid.
        virtual WatchpointLayoutPtr getLayout(WatchpointLayoutFactory& factory) const noexcept = 0;

        /// \brief Get the string representation of given element
        /// \param factory The layout factory, used to get value from nested layouts
        /// \param path The path to the element. Can be empty if watched value is a POD.
        /// \param [out] out_value The string representation
        /// \note The path is consumed (pop_front) until the final layout element is reached.
        /// \return The true if the path was valid, false otherwise.
        virtual bool getValue(WatchpointLayoutFactory const& factory,
                              WatchpointLayoutPath&          path,
                              Amino::String&                 out_value) const noexcept = 0;

    private:
        /// Disabled
        /// \{
        Watcher(Watcher const&)            = delete;
        Watcher(Watcher&&)                 = delete;
        Watcher& operator=(Watcher const&) = delete;
        Watcher& operator=(Watcher&&)      = delete;
        /// \}
    };

    /// \brief Get the watcher for given type.
    /// \param typeId The typeId of data flowing through the watchpoint.
    /// \param flags The watcher flags.
    /// \return A pointer to the watcher, or nullptr if type is not supported.
    virtual Watcher* createWatcher(Amino::TypeId const& typeId,
                                   Watcher::Flags flags = Watcher::Flags::kNone) const noexcept = 0;

    /// \brief Get the watcher for given type.
    /// \param type The type of data flowing through the watchpoint.
    /// \param flags The watcher flags.
    /// \return A pointer to the watcher, or nullptr if type is not supported.
    virtual Watcher* createWatcher(Amino::Type const& type,
                                   Watcher::Flags     flags = Watcher::Flags::kNone) const noexcept;

    /// \brief Create a custom layout for a value of one of the supported types.
    /// \param factory The layout factory, used to get/create nested layouts.
    /// \param any The value to create the layout for.
    /// \return The layout of value on success, or nullptr otherwise.
    virtual WatchpointLayoutPtr createLayout(WatchpointLayoutFactory const& factory,
                                             Amino::Any const&              any) const noexcept;

    /// \brief Get the string representation of an element of a given value.
    /// \param factory The layout factory, used to get value from nested layouts
    /// \param any The value
    /// \param path The path to the element
    /// \param [out] out_value The string representation
    /// \note The path is consumed (pop_front) until the final layout element is reached.
    /// \return The true if the path was valid, false otherwise.
    virtual bool getValue(WatchpointLayoutFactory const& factory,
                          Amino::Any const&              any,
                          WatchpointLayoutPath&          path,
                          Amino::String&                 out_value) const noexcept;

    /// \brief Get the list of watchable parameters for a given type.
    /// \deprecated Use \ref createWatcher instead.
    ///
    /// \param [in] type The Amino type.
    /// \param [out] parameters The list where to return the parameters.
    /// \return true if any parameter is available, false otherwise.
    ///
    /// \note The default implementation leaves the output list \p parameters unchanged and
    /// returns false.
    WATCHPOINT_DEPRECATED("Use createWatcher instead.")
    virtual bool getAvailableParameters(const Amino::Type& type,
                                        StringArray&       parameters) const noexcept;

    /// \brief Get details on the watchable parameter for a given type.
    /// \deprecated Use \ref createWatcher instead.
    ///
    /// \param [in] type The Amino type.
    /// \param [in] parameter The parameter.
    /// \param [out] description The description of the parameter.
    /// \param [out] values The values that can be assigned to the
    /// parameter. Can be used as a way to configure the parameter.
    /// \param [out] descriptions The descriptions of each values.
    /// \return true if parameter is valid, false otherwise.
    ///
    /// \note The default implementation leaves all output parameters unchanged and returns false.
    WATCHPOINT_DEPRECATED("Use createWatcher instead.")
    virtual bool getParameterDetails(const Amino::Type& type,
                                     const String&      parameter,
                                     String&            description,
                                     StringArray&       values,
                                     StringArray&       descriptions) const noexcept;

    /// \brief An interface for the watchpoints to manage recorded values.
    /// \deprecated Use \ref Watcher instead.
    /// \note This class belongs to a feature that is still
    /// under development and may change in subsequent versions.
    class WATCHPOINT_DEPRECATED("Use Watcher instead.") BIFROSTGRAPH_EXECUTOR_SHARED_DECL Records {
    public:
        using String      = Watchpoint::String;
        using StringArray = Watchpoint::StringArray;

        explicit Records(const Amino::WatchPoint& watchpoint) noexcept;
        virtual ~Records() noexcept;

        /// \brief Query the value currently assigned to a given parameter.
        /// see Watchpoint::getParameterDetails
        /// \param [in] parameter The parameter.
        /// \param [out] value The parameter's value.
        /// \return true if parameter is valid, false otherwise.
        bool getSetting(const String& parameter, String& value) const noexcept;

        /// \brief Remove all stored values.
        virtual void clear() noexcept = 0;

        /// \brief Remove stored values for the given parameter.
        /// \param [in] parameter The parameter.
        virtual void erase(const String& parameter) noexcept = 0;

        /// \brief Set (replace) recorded value for given parameter.
        /// \param [in] parameter The parameter.
        /// \param [in] value The value.
        virtual void set(const String& parameter, const String& value) noexcept = 0;

        /// \brief Set (replace) recorded values for given parameter.
        /// \param [in] parameter The parameter.
        /// \param [in] values The values.
        virtual void set(const String& parameter, const StringArray& values) noexcept = 0;

        /// \brief Add (append) recorded value for given parameter.
        /// \param [in] parameter The parameter.
        /// \param [in] value The value.
        virtual void add(const String& parameter, const String& value) noexcept = 0;

        /// \brief Add (append) recorded values for given parameter.
        /// \param [in] parameter The parameter.
        /// \param [in] values The values.
        virtual void add(const String& parameter, const StringArray& values) noexcept = 0;

    private:
        class Impl;
        Impl* m_pImpl = nullptr;
    };

    /// \brief Create a new Watchpoint client data.
    /// \deprecated Use \ref createWatcher instead.
    ///
    /// \param [in] type        The type of data flowing through the Watchpoint.
    /// \param [in,out] records A reference to a Records object, to query settings and store new
    /// values for the parameters.
    /// \return An opaque pointer to the new client data.
    ///
    /// \note The default implementation ignores input parameters and returns nullptr.
    WATCHPOINT_DEPRECATED("Use createWatcher instead.")
    virtual const void* createClientData(const Amino::Type& type, Records& records) const noexcept;

    /// \brief Release a Watchpoint client data.
    /// \deprecated Use \ref createWatcher instead.
    ///
    /// \param [in] type The type of data flowing through the Watchpoint.
    /// \param [in] clientData An opaque pointer to the client data allocated by createClientData.
    /// \return true if operation was successful, false otherwise.
    ///
    /// \note The default implementation ignores input parameters and returns false.
    WATCHPOINT_DEPRECATED("Use createWatcher instead.")
    virtual bool releaseClientData(const Amino::Type& type, const void* clientData) const noexcept;

    /// \brief Field enumerants for indices sorter and filters
    enum class Field : char { eIndex, eValue, eElement };

    /// \brief Structure that holds the sorting settings for \ref getIndices
    struct Sorter {
        enum class Order : char { eAscending, eDescending };

        Sorter() : m_order(Order::eAscending), m_field(Field::eIndex) {}
        explicit Sorter(Order order) : m_order(order), m_field(Field::eIndex) {}
        explicit Sorter(Order order, Field field) : m_order(order), m_field(field) {}
        explicit Sorter(Order order, Amino::String elementName)
            : m_order(order), m_field(Field::eElement), m_elementName(std::move(elementName)) {}

        Order         m_order;
        Field         m_field;
        Amino::String m_elementName;
    };

    /// \brief Structure that holds the filtering settings for \ref getIndices
    struct Filter {
        using Filters = Amino::Array<Filter>;

        enum class Conjunction : char { eAnd, eOr };
        enum class Operation : char {
            eLess,
            eLessOrEqual,
            eEqual,
            eNotEqual,
            eGreaterOrEqual,
            eGreater,
            eIsInfinite,
            eIsNotANumber,
            eSubFilters
        };

        explicit Filter(Conjunction conjunction, Operation operation, Amino::Any value)
            : m_conjunction(conjunction),
              m_operation(operation),
              m_field(Field::eValue),
              m_value(std::move(value)),
              m_elementName() {}
        explicit Filter(Conjunction   conjunction,
                        Operation     operation,
                        Amino::String elementName,
                        Amino::Any    elementValue)
            : m_conjunction(conjunction),
              m_operation(operation),
              m_field(Field::eElement),
              m_value(std::move(elementValue)),
              m_elementName(std::move(elementName)) {}
        explicit Filter(Conjunction conjunction, Operation operation, Field field, Amino::Any value)
            : m_conjunction(conjunction),
              m_operation(operation),
              m_field(field),
              m_value(std::move(value)),
              m_elementName() {}

        explicit Filter(Conjunction conjunction, Filters subFilters)
            : m_conjunction(conjunction),
              m_operation{Operation::eSubFilters},
              m_subFilters(std::move(subFilters)) {}

        explicit Filter(Operation operation, Amino::Any value)
            : Filter(Conjunction::eAnd, operation, std::move(value)) {}
        explicit Filter(Operation operation, Amino::String elementName, Amino::Any elementValue)
            : Filter(
                  Conjunction::eAnd, operation, std::move(elementName), std::move(elementValue)) {}
        explicit Filter(Operation operation, Field field, Amino::Any value)
            : Filter(Conjunction::eAnd, operation, field, std::move(value)) {}
        explicit Filter(Filters subFilters) : Filter(Conjunction::eAnd, std::move(subFilters)) {}

        Conjunction   m_conjunction;
        Operation     m_operation;
        Field         m_field;
        Amino::Any    m_value;
        Amino::String m_elementName;
        Filters       m_subFilters;
    };
    using Filters = Filter::Filters;
    using Indices = Amino::Array<std::size_t>;

    /// \brief Implemenation helper to return the indices of an array value for given filters and sorter settings.
    /// \param any The array value
    /// \param filters The list of filters
    /// \param sorter  The sorting settings
    /// \param out_indices  The filtered and sorted indices
    /// \return True on success, false otherwise.
    /// \note The default implementation does nothing and returns false.
    virtual bool getIndices(Amino::Any const& any,
                            Filters const&    filters,
                            Sorter const&     sorter,
                            Indices&          out_indices) const noexcept;

private:
    /// Disabled
    /// \{
    Watchpoint(const Watchpoint&)            = delete;
    Watchpoint(Watchpoint&&)                 = delete;
    Watchpoint& operator=(const Watchpoint&) = delete;
    Watchpoint& operator=(Watchpoint&&)      = delete;
    /// \}

    /// The name of this Watchpoint for logging purposes.
    String m_name;
};

} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_WATCHPOINT_H

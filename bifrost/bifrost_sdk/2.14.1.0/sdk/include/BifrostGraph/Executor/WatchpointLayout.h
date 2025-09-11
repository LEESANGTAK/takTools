//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file WatchpointLayout.h
/// \brief BifrostGraph Executor Watchpoint Layout.
/// \note The contents of this file belong to a feature that is still
/// under development, and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_WATCHPOINT_LAYOUT_H
#define BIFROSTGRAPH_EXECUTOR_WATCHPOINT_LAYOUT_H

#include <BifrostGraph/Executor/internal/ExecutorExport.h>

#include <BifrostGraph/Executor/Types.h>
#include <BifrostGraph/Executor/Watchpoint.h>

#include <Amino/Core/TypeId.h>

namespace Amino {
class Any;
class String;
class Type;
} // namespace Amino

namespace BifrostGraph {
namespace Executor {

class Workspace;
class WatchpointLayout;
class WatchpointLayoutFactory;
class WatchpointLayoutPath;

namespace Private {
class WorkspaceImpl;
}

///////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////

/// \brief A smart pointer on WatchpointLayout objects allowing them to be easily shared and
/// managed.
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL WatchpointLayoutPtr {
public:
    /// \brief Construct an empty pointer
    WatchpointLayoutPtr();

    /// \brief Construct a smart pointer that owns the layout object pointed by \p layout,
    /// \param layout A pointer to an WatchpointLayout object.
    /// \note The 'use count' of the layout is increased by one.
    explicit WatchpointLayoutPtr(WatchpointLayout* layout);

    /// \brief Copy constructor
    /// Construct a smart pointer on the same layout object as \p other and sharing ownership.
    /// \param other The pointer to be copied.
    /// \note The 'use count' of the layout is increased by one.
    WatchpointLayoutPtr(WatchpointLayoutPtr const& other);

    /// \brief Move constructor
    /// Construct a smart pointer on the same layout object as \p other and taking ownership.
    /// \param other The pointer to be moved.
    /// \note The 'use count' of the layout is unmodified.
    WatchpointLayoutPtr(WatchpointLayoutPtr&& other);

    /// \brief Destructor
    /// If the pointer owns a layout object, its 'use count' is decremented by one.
    /// If the 'use count' reaches zero, the layout object will be deleted by
    /// invoking WatchpointLayout::deleteThis.
    ~WatchpointLayoutPtr();

    /// \brief Assignment operators
    /// \{
    WatchpointLayoutPtr& operator=(WatchpointLayoutPtr const&);
    WatchpointLayoutPtr& operator=(WatchpointLayoutPtr&&);
    /// /}

    /// \brief Returns whether the pointer is non-null
    explicit inline operator bool() const noexcept { return m_layout != nullptr; }

    /// \brief Comparison
    /// \return true if pointers are equal.
    inline bool operator==(WatchpointLayoutPtr const& other) const noexcept {
        return m_layout == other.m_layout;
    }

    /// \brief Comparison
    /// \return true if pointers are different.
    inline bool operator!=(WatchpointLayoutPtr const& other) const noexcept {
        return m_layout != other.m_layout;
    }

    /// \brief Indirection
    /// \return the pointer to the pointed layout.
    inline operator WatchpointLayout const*() const noexcept { return m_layout; } // NOLINT

    /// \brief Indirection
    /// \return the pointer to the pointed layout.
    inline WatchpointLayout const* operator->() const noexcept { return m_layout; }

    /// \brief Indirection
    /// \return the pointer to the pointed layout.
    inline WatchpointLayout* operator->() noexcept { return m_layout; }

    /// \brief Accessor
    /// \return the pointer to the pointed layout.
    inline WatchpointLayout* get() const noexcept { return m_layout; }

    /// \brief Check whether or not the pointed layout of type \p T.
    /// \tparam T The layout type.
    /// \return true if the pointed layout of type \p T.
    template <typename T>
    inline bool isA() const noexcept {
        return dynamic_cast<T*>(m_layout) != nullptr;
    }

    /// \brief Get the pointed layout casted as type \p T.
    /// \tparam T The layout type.
    /// \return the pointed layout casted as type \p T.
    template <typename T>
    inline T& getAs() const noexcept {
        return *static_cast<T*>(m_layout);
    }

private:
#ifndef DOXYGEN
    WatchpointLayout* m_layout = nullptr;
#endif
};

///////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////

/// \brief A basic layout
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL WatchpointLayout {
public:
    /// \brief Create a new WatchpointLayout.
    /// \param factory The layout factory.
    /// \param typeId the typeId of the layout
    /// \return a smart pointer to the new layout.
    static WatchpointLayoutPtr create(WatchpointLayoutFactory const& factory,
                                      Amino::TypeId const&           typeId);

    /// \brief Create a new WatchpointLayout.
    /// \param type the datamodel type of the layout
    /// \param typeId the typeId of the layout
    /// \return a smart pointer to the new layout.
    static WatchpointLayoutPtr create(Amino::Type const& type, Amino::TypeId const& typeId);

    /// \brief Destructor
    virtual ~WatchpointLayout();

    /// \brief Get the typeId the layout is based on.
    Amino::TypeId const& getTypeId() const;

    /// \brief Get the type the layout is based on.
    Amino::Type const& getType() const;

    /// \brief Get the fully qualified type name the layout is based on.
    Amino::String const& getTypeName() const;

    /// \brief Get the layout's kind name.
    /// \note This corresponds to the type's 'type_kind' metadata.
    Amino::String const& getTypeKind() const;

protected:
    /// \brief Internal constructor
    WatchpointLayout(Amino::Type const& type, Amino::TypeId const& typeId);

private:
    WatchpointLayout(WatchpointLayout&&)      = delete;
    WatchpointLayout(WatchpointLayout const&) = delete;

private:
    friend WatchpointLayoutPtr;
    /// \brief Function used by the smart pointer to destroy the instance.
    /// \see WatchpointLayoutPtr::~WatchpointLayoutPtr()
    virtual void deleteThis();

private:
    class Impl;
    Impl* m_impl;

    /// \brief Counter used by the smart pointer to manage the instance.
    std::size_t m_useCount = 0u;
};

///////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////

/// \brief A composite layout, that contains sub layouts
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL WatchpointLayoutComposite : public WatchpointLayout {
public:
    /// \brief Create a new WatchpointLayoutComposite.
    /// \param factory The layout factory.
    /// \param typeId the typeId of the layout
    /// \param placeHolder Whether or not this is a place holder for a custom layout.
    /// \return a smart pointer to the new layout.
    static WatchpointLayoutPtr create(WatchpointLayoutFactory const& factory,
                                      Amino::TypeId const&           typeId,
                                      bool                           placeHolder = false);

    /// \brief Create a new WatchpointLayoutComposite.
    /// \param type the datamodel type of the layout
    /// \param typeId the typeId of the layout
    /// \param placeHolder Whether or not this is a place holder for a custom layout.
    /// \return a smart pointer to the new layout.
    static WatchpointLayoutPtr create(Amino::Type const&   type,
                                      Amino::TypeId const& typeId,
                                      bool                 placeHolder = false);

    /// \brief Destructor
    ~WatchpointLayoutComposite() override;

    /// \brief Check whether or not the composite has a flattened string representation.
    /// \return True if composite has a flattened string representation, false otherwise.
    bool hasFlattenedRepresentation() const;

    /// \brief Get the template of the flattened string representation for the composite.
    /// \note This corresponds to the layout's type 'watchpoint_layout' metadata.
    /// \return The flattened string representation's template.
    Amino::String const& flattenedRepresentation() const;

    /// \brief Get the flattened string representation of the value based on the composite's
    /// custom layout.
    /// \param factory The layout factory.
    /// \param value The value.
    /// \param [out] out_value The flattened representation.
    /// \return The true if the layout has a flattened representation, false otherwise.
    /// \return The flattened string representation.
    bool flattenedRepresentation(WatchpointLayoutFactory const& factory,
                                 Amino::Any const&              value,
                                 Amino::String&                 out_value) const;

protected:
    /// \brief Internal constructor
    WatchpointLayoutComposite(Amino::Type const&   type,
                              Amino::TypeId const& typeId,
                              bool                 placeHolder);

private:
    WatchpointLayoutComposite(WatchpointLayoutComposite&&)      = delete;
    WatchpointLayoutComposite(WatchpointLayoutComposite const&) = delete;

public:
    /// \brief Forward iterator on the sub layouts.
    class BIFROSTGRAPH_EXECUTOR_SHARED_DECL Iterator {
        friend WatchpointLayoutComposite;
        class Impl;

    public:
        explicit Iterator(Impl* impl);
        ~Iterator();

        /// \brief Advance to the next iterator
        /// \return *this
        Iterator& operator++();

        /// \brief Comparison
        /// \return true if iterators are equal.
        bool operator==(const Iterator& other) const;

        /// \brief Comparison
        /// \return true if iterators are different.
        bool operator!=(const Iterator& other) const;

        class BIFROSTGRAPH_EXECUTOR_SHARED_DECL SubLayout {
        public:
            Amino::String const&       name() const;
            WatchpointLayoutPtr const& layout() const;
        };

        /// \brief Get the layout pointed by current iterator
        SubLayout const& operator*() const;

    private:
        Impl* m_impl;
    };

    /// \brief Return whether or not this is a place holder for a custom layout.
    /// \note A place holder should be excluded from an element path.
    bool placeHolder() const;

    /// \brief Return whether or not the composite has no sub layouts.
    bool empty() const;

    /// \brief Return the number of sub layouts.
    std::size_t size() const;

    /// \brief Return an iterator on the first sub layout.
    Iterator begin() const;

    /// \brief Return an iterator past the last sub layout.
    Iterator end() const;

    /// \brief Add a sub layout.
    /// \param name The name of the sub layout.
    /// \param layout The sub layout.
    /// \return The sub layout on success or an empty pointer otherwise.
    WatchpointLayoutPtr add(Amino::String const& name, WatchpointLayoutPtr const& layout);

    /// \brief Get the sub layout of given name.
    /// \param name The name of the sub layout.
    /// \return The layout or an empty pointer if not found.
    WatchpointLayoutPtr const get(Amino::String const& name) const;

private:
    class Impl;
    Impl* m_impl;
};

///////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////

/// \brief Array layout
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL WatchpointLayoutArray : public WatchpointLayout {
public:
    /// \brief Create a new WatchpointLayoutArray for value \p value.
    /// \param factory The layout factory.
    /// \param value The value.
    /// \return a smart pointer to the new layout.
    static WatchpointLayoutPtr create(WatchpointLayoutFactory const& factory,
                                      Amino::Any const&              value);

    /// \brief Create a new WatchpointLayoutArray for value \p value.
    /// \param factory The layout factory.
    /// \param type the datamodel type of the layout
    /// \param value The value.
    /// \return a smart pointer to the new layout.
    static WatchpointLayoutPtr create(WatchpointLayoutFactory const& factory,
                                      Amino::Type const&             type,
                                      Amino::Any const&              value);

    /// \brief Destructor
    ~WatchpointLayoutArray() override;

    /// \brief Get the element typeId of the layout array type.
    Amino::TypeId const& getElementTypeId() const;

    /// \brief Get the element type of the layout array type.
    Amino::Type const& getElementType() const;

    /// \brief Get the fully qualified element type name of the layout array type.
    Amino::String const& getElementTypeName() const;

    /// \brief Get the kind name of the element layout's.
    /// \note This corresponds to the element type's 'type_kind' metadata.
    Amino::String const& getElementTypeKind() const;

    /// \brief Helper to return the indices of the array for given filters and sorter settings.
    /// \param filters The list of filters
    /// \param sorter  The sorting settings
    /// \param out_indices  The filtered and sorted indices
    /// \return True on success, false otherwise.
    bool getIndices(Watchpoint::Filters const& filters,
                    Watchpoint::Sorter const&  sorter,
                    Watchpoint::Indices&       out_indices) const;

protected:
    /// \brief Internal constructor
    WatchpointLayoutArray(WatchpointLayoutFactory const& factory,
                          Amino::Type const&             type,
                          Amino::Any const&              value);

private:
    WatchpointLayoutArray(WatchpointLayoutArray&&)      = delete;
    WatchpointLayoutArray(WatchpointLayoutArray const&) = delete;

public:
    /// \brief Return the number of elements.
    std::size_t size() const;

    /// \brief Get the layout of the element at given index.
    /// \param index The index of the element.
    /// \return The element layout on success or an empty pointer otherwise.
    WatchpointLayoutPtr layout(std::size_t index) const;

private:
    class Impl;
    Impl* m_impl;
};

///////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////

/// \brief Layout factory to build layouts for types and/or values.
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL WatchpointLayoutFactory {
private:
    /// \brief Constructor
    /// If an error occurs during the construction of this WatchpointLayoutFactory,
    /// then \ref WatchpointLayoutFactory::isValid will return false and
    /// all future operations on this WatchpointLayoutFactory will fail.
    WatchpointLayoutFactory() noexcept;

    /// \brief Constructor that leaves the WatchpointLayoutFactory in an uninitialized state.
    /// \ref WatchpointLayoutFactory::isValid will return false.
    explicit WatchpointLayoutFactory(Uninitialized uninitialized) noexcept;

    /// \brief Set the Workspace object this factory belongs to.
    /// \param workspace Reference to the \ref Workspace object.
    void setWorkspace(Workspace const& workspace) noexcept;

    /// \brief Allow the WorkspaceImpl object to access the private constructors and
    /// setWorkspace.
    friend class BifrostGraph::Executor::Private::WorkspaceImpl;

public:
    /// \brief Get a statically allocated factory that is uninitialized and invalid.
    /// Any operation on this instance will always fail and \ref WatchpointLayoutFactory::isValid
    /// will return false.
    static WatchpointLayoutFactory& getInvalid() noexcept;

    /// \brief Destructor
    ~WatchpointLayoutFactory() noexcept;

    /// \brief Check if this WatchpointLayoutFactory has been successfully initialized.
    bool isValid() const noexcept;

    /// \brief Get the Workspace object this factory belongs to.
    Workspace const& getWorkspace() const;

    /// \brief Get the Type corresponding to given fully qualified type name.
    /// \param typeName The fully qualified type name.
    /// \return The corresponding type.
    Amino::Type getType(Amino::String const& typeName) const;

    /// \brief Register a fixed layout for given type.
    /// \param layout The layout
    /// \return The added layout on success, or nullptr on failure.
    /// \note This will fail the layout is nullptr or another layout was already registered
    /// for layout's type.
    WatchpointLayoutPtr add(WatchpointLayoutPtr const& layout);

    /// \brief Query if a layout is registered for given type.
    /// \param typeId The typeId
    /// \return True if a layout is registered, false otherwise.
    bool exists(Amino::TypeId const& typeId) const;

    /// \brief Get the layout for given type.
    /// \param typeId The typeId.
    /// \return The layout if it existed or was successfuly created, nullptr otherwise.
    WatchpointLayoutPtr get(Amino::TypeId const& typeId) const;

    /// \brief Get the layout for given value.
    /// \param any The value
    /// \return The layout of value on success, or nullptr otherwise.
    WatchpointLayoutPtr get(Amino::Any const& any) const;

    /// \brief Get the layout for given value.
    /// \param type The datamodel type of the value
    /// \param any The value
    /// \return The layout of value on success, or nullptr otherwise.
    WatchpointLayoutPtr get(Amino::Type const& type, Amino::Any const& any) const;

    /// \brief Get the string representation of an element of a given value.
    /// \param any The value
    /// \param path The path to the element
    /// \param [out] out_value The string representation
    /// \note The path is consumed (pop_front) until the final layout element is reached.
    /// \return The true if the path was valid, false otherwise.
    bool getValue(Amino::Any const&     any,
                  WatchpointLayoutPath& path,
                  Amino::String&        out_value) const;

    /// \brief Get the string representation of an element of a given value.
    /// \param type The datamodel type of the value
    /// \param any The value
    /// \param path The path to the element
    /// \param [out] out_value The string representation
    /// \note The path is consumed (pop_front) until the final layout element is reached.
    /// \return The true if the path was valid, false otherwise.
    bool getValue(Amino::Type const&    type,
                  Amino::Any const&     any,
                  WatchpointLayoutPath& path,
                  Amino::String&        out_value) const;

private:
    class Impl;
    Impl* m_impl;
};

/// \brief Path to an element in a layout.
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL WatchpointLayoutPath {
public:
    /// \brief Constructors
    /// \{
    WatchpointLayoutPath();
    explicit WatchpointLayoutPath(Amino::String const& path);
    WatchpointLayoutPath(WatchpointLayoutPath const&);
    WatchpointLayoutPath(WatchpointLayoutPath&&);
    /// /}

    /// \brief Destructor
    ~WatchpointLayoutPath();

    /// \brief Assignment operators
    /// \{
    WatchpointLayoutPath& operator=(WatchpointLayoutPath const&);
    WatchpointLayoutPath& operator=(WatchpointLayoutPath&&);
    /// /}

    /// \brief Check if path is empty
    bool empty() const;

    /// \brief Prepend an element
    /// \param element The element's name
    void push_front(Amino::String const& element);

    /// \brief Prepend an array index
    /// \param index The array index
    void push_front(std::size_t index);

    /// \brief Get the first element of the path
    Amino::String const& front() const;
    /// \brief Check if first item of path is an array index
    bool frontIsIndex() const;
    /// \brief Get the first element of the path as an array index
    std::size_t frontAsIndex() const;

    /// \brief Remove fist element
    /// \return self
    WatchpointLayoutPath& pop_front();

    /// \brief Append an element
    /// \param element The element's name
    void push_back(Amino::String const& element);

    /// \brief Append an array index
    /// \param index The array index
    void push_back(std::size_t index);

    /// \brief Get the last element of the path
    Amino::String const& back() const;
    /// \brief Check if last item of path is an array index
    bool backIsIndex() const;
    /// \brief Get the last element of the path as an array index
    std::size_t backAsIndex() const;

    /// \brief Remove last element
    /// \return self
    WatchpointLayoutPath& pop_back();

private:
#ifndef DOXYGEN
    class Impl;
    Impl* m_impl;
#endif
};

} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_WATCHPOINT_LAYOUT_H

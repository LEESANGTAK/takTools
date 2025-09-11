//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "PeriodicTableElement.h"

#include <Amino/Core/Any.h>
#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Core/String.h>
#include <Amino/Core/TypeId.h>

#include <BifrostGraph/Executor/Utility.h>
#include <BifrostGraph/Executor/Watchpoint.h>
#include <BifrostGraph/Executor/WatchpointLayout.h>

#include <mutex>
#include <string>

using CallBackFunc = BifrostGraph::Executor::Watchpoint::CallBack;

namespace {

// Properties to watch
Amino::String const kElementName       = "name";
Amino::String const kElementMass       = "mass";
Amino::String const kElementNumber     = "number";
Amino::String const kElementSymbol     = "symbol";

using PTEPtr      = Amino::Ptr<Examples::SDK::PeriodicTableElement>;
using PTEArrayPtr = Amino::Ptr<Amino::Array<PTEPtr>>;

///-------------------------------------------------------------------------
/// \brief Get the string representation of element of given path
bool getElementValue(BifrostGraph::Executor::WatchpointLayoutFactory const& /*factory*/,
    PTEPtr const& pteValue, BifrostGraph::Executor::WatchpointLayoutPath& path, Amino::String& out_value) {
    if (pteValue) {
        if (path.empty()) {
            out_value = Amino::String{"("} + pteValue->getSymbol() + ", " + std::to_string(pteValue->getNumber()).c_str() + ")";
            return true;
        } else {
            auto const& element = path.front();
            if (element == kElementName) {
                out_value = pteValue->getName();
                path.pop_front();
                return true;
            } else if (element == kElementMass) {
                out_value = std::to_string(pteValue->getMass()).c_str();
                path.pop_front();
                return true;
            } else if (element == kElementNumber) {
                out_value = std::to_string(pteValue->getNumber()).c_str();
                path.pop_front();
                return true;
            } else if (element == kElementSymbol) {
                out_value = pteValue->getSymbol();
                path.pop_front();
                return true;
            }
        }
    }
    return false;
}

///-------------------------------------------------------------------------
/// \brief Get the string representation of element of given path
bool getArrayElementValue(BifrostGraph::Executor::WatchpointLayoutFactory const& factory,
    PTEArrayPtr const& pteValues, BifrostGraph::Executor::WatchpointLayoutPath& path, Amino::String& out_value) {
    if (pteValues && !path.empty() && path.frontIsIndex()) {
        auto const idx = path.frontAsIndex();
        if (idx < pteValues->size()) {
            path.pop_front();
            return getElementValue(factory, pteValues->at(idx), path, out_value);
        }
    }
    return false;
}

///-------------------------------------------------------------------------
/// \brief Create the layout for a Periodic Table Element
BifrostGraph::Executor::WatchpointLayoutPtr createPeriodicTableElementLayout(
        BifrostGraph::Executor::WatchpointLayoutFactory const& factory) noexcept {
    try {
        auto layout = BifrostGraph::Executor::WatchpointLayoutComposite::create(factory, Amino::getTypeId<PTEPtr>());
        auto& composite = layout.template getAs<BifrostGraph::Executor::WatchpointLayoutComposite>();
        composite.add(kElementName,   factory.get(Amino::getTypeId<Amino::String>()));
        composite.add(kElementMass,   factory.get(Amino::getTypeId<Amino::float_t>()));
        composite.add(kElementNumber, factory.get(Amino::getTypeId<Amino::uint_t>()));
        composite.add(kElementSymbol, factory.get(Amino::getTypeId<Amino::String>()));
        return layout;
    } catch(...) {}
    return {};
}

///-------------------------------------------------------------------------
/// \brief The Periodic table element watchpoint watcher
template <typename T>
class PeriodicTableElementWatcher : public BifrostGraph::Executor::Watchpoint::Watcher {
public:
    PeriodicTableElementWatcher() {}
    virtual ~PeriodicTableElementWatcher() = default;

    PeriodicTableElementWatcher(PeriodicTableElementWatcher const&) = delete;
    PeriodicTableElementWatcher(PeriodicTableElementWatcher&&)      = delete;

    void deleteThis() noexcept override { delete this; }

    BifrostGraph::Executor::WatchpointLayoutPtr getLayout(
        BifrostGraph::Executor::WatchpointLayoutFactory& factory) const noexcept override;

    bool getValue(
        BifrostGraph::Executor::WatchpointLayoutFactory const& factory,
        BifrostGraph::Executor::WatchpointLayoutPath&          path,
        Amino::String&                                         out_value) const noexcept override;

    void record(T const& value);

private:
    T                                                   m_value;
    mutable BifrostGraph::Executor::WatchpointLayoutPtr m_layout;
};

///-------------------------------------------------------------------------
/// \brief Get the layout of watcher value: either composite or array
template <typename T>
BifrostGraph::Executor::WatchpointLayoutPtr PeriodicTableElementWatcher<T>::getLayout(
        BifrostGraph::Executor::WatchpointLayoutFactory& factory) const noexcept {
    try {
        if (!m_layout && m_value) {
            if constexpr (std::is_same<T, PTEPtr>::value) {
                m_layout = createPeriodicTableElementLayout(factory);
            } else if constexpr (std::is_same<T, PTEArrayPtr>::value) {
                m_layout = BifrostGraph::Executor::WatchpointLayoutArray::create(factory, Amino::Any{m_value});
            }
        }
    } catch(...) {}
    return m_layout;
}

///-------------------------------------------------------------------------
/// \brief Get the string representation of element of given path
template <typename T>
bool PeriodicTableElementWatcher<T>::getValue(
        BifrostGraph::Executor::WatchpointLayoutFactory const& factory,
        BifrostGraph::Executor::WatchpointLayoutPath&   path,
        Amino::String&                 out_value) const noexcept {
    try {
        if constexpr (std::is_same<T, PTEPtr>::value) {
            return getElementValue(factory, m_value, path, out_value);
        } else if constexpr (std::is_same<T, PTEArrayPtr>::value) {
            return getArrayElementValue(factory, m_value, path, out_value);
        }
    } catch(...) {}
    return false;
}

///-------------------------------------------------------------------------
/// \brief Record the value into the watcher
template <typename T>
void PeriodicTableElementWatcher<T>::record(T const& value) {
    m_value = value;
    if constexpr (std::is_same<T, PTEArrayPtr>::value) {
        m_layout = {}; // array value has changed reset layout
    }
}

///-------------------------------------------------------------------------
/// \brief The callback function to dispatch to the watchpoint code
template <typename T>
void wpCallBack(void const* data, Amino::ulong_t, void const* value) {
    if (data == nullptr || value == nullptr) return;

    static std::mutex           s_mutex;
    std::lock_guard<std::mutex> lock(s_mutex);

    auto* watcher = reinterpret_cast<PeriodicTableElementWatcher<T>*>(
        const_cast<void*>(data));
    auto const* typedValue = reinterpret_cast<T const*>(value);
    watcher->record(*typedValue);
}

} // namespace

///-------------------------------------------------------------------------
/// \brief The contract to implement for watchpoint (see base class)
class PeriodicTableElementWatchpoint : public BifrostGraph::Executor::Watchpoint {
public:
    PeriodicTableElementWatchpoint();
    ~PeriodicTableElementWatchpoint() override;

    void deleteThis() noexcept override;

    void getSupportedTypeIds(TypeIdArray& out_typeIds) const noexcept override;

    CallBackFunc getCallBackFunction(Amino::TypeId const& typeId) const noexcept override;

    Watcher* createWatcher(Amino::TypeId const& typeId, Watcher::Flags flags) const noexcept override;

    bool getValue(BifrostGraph::Executor::WatchpointLayoutFactory const& factory,
                  Amino::Any const&                                      any,
                  BifrostGraph::Executor::WatchpointLayoutPath&          path,
                  Amino::String&                                         out_value) const noexcept override;

    BifrostGraph::Executor::WatchpointLayoutPtr createLayout(
        BifrostGraph::Executor::WatchpointLayoutFactory const& factory,
        Amino::Any const& any) const noexcept override;
};

// Implementation of contract for watchpoints

///-------------------------------------------------------------------------
/// \brief Creation
PeriodicTableElementWatchpoint::PeriodicTableElementWatchpoint()
    : BifrostGraph::Executor::Watchpoint("Periodic Table Element Watchpoint") {}

///-------------------------------------------------------------------------
/// \brief Destruction
PeriodicTableElementWatchpoint::~PeriodicTableElementWatchpoint() = default;

void PeriodicTableElementWatchpoint::deleteThis() noexcept { delete this; }

///-------------------------------------------------------------------------
/// \brief The supported typeIds of the watchpoint
void PeriodicTableElementWatchpoint::getSupportedTypeIds(TypeIdArray& out_typeIds) const noexcept {
    try {
        out_typeIds.push_back(Amino::getTypeId<PTEPtr>());
        out_typeIds.push_back(Amino::getTypeId<PTEArrayPtr>());
    } catch(...) {
    }
}

///-------------------------------------------------------------------------
/// \brief Return the proper callback function
CallBackFunc PeriodicTableElementWatchpoint::getCallBackFunction(Amino::TypeId const& typeId) const noexcept {
    if (typeId == Amino::getTypeId<PTEArrayPtr>()) {
        return &wpCallBack<PTEArrayPtr>;
    }
    assert(typeId == Amino::getTypeId<PTEPtr>());
    return &wpCallBack<PTEPtr>;
}

///-------------------------------------------------------------------------
/// \brief The creation of a watcher
BifrostGraph::Executor::Watchpoint::Watcher* PeriodicTableElementWatchpoint::createWatcher(
        Amino::TypeId const& typeId, Watcher::Flags) const noexcept {
    if (typeId == Amino::getTypeId<PTEArrayPtr>()) {
        return new(std::nothrow) PeriodicTableElementWatcher<PTEArrayPtr>();
    }
    assert(typeId == Amino::getTypeId<PTEPtr>());
    return new(std::nothrow) PeriodicTableElementWatcher<PTEPtr>();
}

///-------------------------------------------------------------------------
/// \brief Get the string representation of an element of a given value.
bool PeriodicTableElementWatchpoint::getValue(
        BifrostGraph::Executor::WatchpointLayoutFactory const& factory,
        Amino::Any const&                                      any,
        BifrostGraph::Executor::WatchpointLayoutPath&          path,
        Amino::String&                                         out_value) const noexcept {
    if (any.type() == Amino::getTypeId<PTEArrayPtr>()) {
        return getArrayElementValue(factory, Amino::any_cast<PTEArrayPtr>(any), path, out_value);
    } else if (any.type() == Amino::getTypeId<PTEPtr>()) {
        return getElementValue(factory, Amino::any_cast<PTEPtr>(any), path, out_value);
    }
    return false;
}

//-------------------------------------------------------------------------------------------------
/// \brief Create the layout for corresponding any value.
/// This is mainly used to query the layout of an array in the Data Browser
BifrostGraph::Executor::WatchpointLayoutPtr PeriodicTableElementWatchpoint::createLayout(
    BifrostGraph::Executor::WatchpointLayoutFactory const& factory,
    Amino::Any const& any) const noexcept {
    try {
        if (any.type() == Amino::getTypeId<PTEArrayPtr>()) {
            return BifrostGraph::Executor::WatchpointLayoutArray::create(factory, any);
        } else if (any.type() == Amino::getTypeId<PTEPtr>()) {
            return createPeriodicTableElementLayout(factory);
        }
    } catch(...) {}
    return {};
}

///-------------------------------------------------------------------------
/// \brief The entry point used by Bifrost to register watchpoints
extern "C" {
EXECUTOR_WATCHPOINT_DECL BifrostGraph::Executor::Watchpoint* createBifrostWatchpoint(void);

EXECUTOR_WATCHPOINT_DECL BifrostGraph::Executor::Watchpoint* createBifrostWatchpoint(void) {
    return new PeriodicTableElementWatchpoint();
}
}

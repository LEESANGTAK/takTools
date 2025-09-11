//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_STOP_CALLBACK_DETAILS_H
#define AMINO_CORE_INTERNAL_STOP_CALLBACK_DETAILS_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file StopCallbackDetails.h

#include <Amino/Core/CoreExport.h>

#include <Amino/Core/internal/PImpl.h>

#include <utility>

namespace Amino {
class StopToken;

namespace Internal {

//==============================================================================
// CLASS StopCallbackTyped<Callback>
//==============================================================================

/// \brief The typed part of a \ref Amino::StopCallback.
template <typename Callback>
class StopCallbackTyped {
protected:
    /// \brief Contructor.
    template <typename C>
    explicit StopCallbackTyped(C&& cb) : m_callback{std::forward<C>(cb)} {}

    /// \brief Invoke the captured callback.
    void invoke_callback() { m_callback(); }

private:
    /// \brief The captured callback to call when the stop is requested.
    Callback m_callback;
};

//==============================================================================
// CLASS StopCallbackUntyped
//==============================================================================

/// \brief The untyped part of a \ref Amino::StopCallback.
class StopCallbackUntyped {
public:
    /// \brief The type-erased callback.
    using CallbackFn = void (*)(StopCallbackUntyped* self);

protected:
    /// \brief Constructor.
    /// \{
    AMINO_CORE_SHARED_DECL StopCallbackUntyped(
        StopToken const& token, CallbackFn callback);
    AMINO_CORE_SHARED_DECL StopCallbackUntyped(
        StopToken&& token, CallbackFn callback);
    /// \}

    /// \brief \ref StopCallbackUntyped is not copyable nor movable.
    /// \{
    StopCallbackUntyped(StopCallbackUntyped const&)            = delete;
    StopCallbackUntyped(StopCallbackUntyped&&)                 = delete;
    StopCallbackUntyped& operator=(StopCallbackUntyped const&) = delete;
    StopCallbackUntyped& operator=(StopCallbackUntyped&&)      = delete;
    /// \}

    /// \brief Destructor.
    AMINO_CORE_SHARED_DECL ~StopCallbackUntyped();

private:
    /// \brief Private implementation.
    Internal::PImpl<StopCallbackUntyped, 8> m_impl;
};

//==============================================================================
// CLASS StopCallbackImpl<Callback>
//==============================================================================

/// \brief The private base implementation of \ref Amino::StopCallback.
template <typename Callback>
class StopCallbackImpl : StopCallbackTyped<Callback>, StopCallbackUntyped {
protected:
    /// \brief Constructor.
    ///
    /// First construct the typed part, then the untyped part. This order is
    /// important because the callback may be called immediately (if stop was
    /// already requested) and therefore the typed part must be fully
    /// initialized.
    template <typename StopToken, typename C>
    StopCallbackImpl(StopToken&& token, C&& cb)
        : StopCallbackTyped<Callback>{std::forward<C>(cb)},
          StopCallbackUntyped{std::forward<StopToken>(token), &callback} {}

private:
    /// \brief The type-erased callback function pointer.
    // LCOV_EXCL_BR_START
    static void callback(StopCallbackUntyped* self) {
        static_cast<StopCallbackImpl*>(self)->invoke_callback();
    }
    // LCOV_EXCL_BR_STOP
};

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

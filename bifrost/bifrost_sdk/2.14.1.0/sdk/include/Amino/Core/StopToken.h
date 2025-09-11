//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

/// \file StopToken.h

#ifndef AMINO_CORE_STOP_TOKEN_H
#define AMINO_CORE_STOP_TOKEN_H

#include <Amino/Core/CoreExport.h>

#include <Amino/Core/StopTokenFwd.h>

#include <Amino/Core/internal/PImpl.h>
#include <Amino/Core/internal/StopCallbackDetails.h>

#define AMINO_API AMINO_CORE_SHARED_DECL
namespace Amino {

//=============================================================================
// CLASS NoStopState_t
//=============================================================================

/// \brief A tag type to indicate that a \ref StopSource should be created
/// without a valid state (such \ref StopSource can't be used to request a
/// stop).
struct NoStopState_t {
    explicit NoStopState_t() = default;
};

//=============================================================================
// CLASS StopToken
//=============================================================================

/// \brief A token that can be used to check if a stop has been requested.
///
/// \note Essentially the same as `std::stop_token`.
class StopToken {
public:
    /// \brief Default constructor (constructs an invalid \ref StopToken that
    /// can't be stopped).
    ///
    /// \post \ref stopPossible() will return `false`.
    AMINO_API StopToken() noexcept;

    /// \brief Move constructor.
    AMINO_API StopToken(StopToken&& o) noexcept;

    /// \brief Copy constructor.
    AMINO_API StopToken(StopToken const& o);

    /// \brief Destructor.
    AMINO_API ~StopToken();

    /// \brief Move assignment operator.
    AMINO_API StopToken& operator=(StopToken&& o) noexcept;

    /// \brief Copy assignment operator.
    AMINO_API StopToken& operator=(StopToken const& o);

    /// \brief Equality operators
    /// \{
    friend bool operator==(StopToken const& lhs, StopToken const& rhs) {
        return lhs.internal_equals(rhs);
    }
    friend bool operator!=(StopToken const& lhs, StopToken const& rhs) {
        return !lhs.internal_equals(rhs);
    }
    /// \}

    /// \brief Check if a stop has been requested on the \ref StopSource that
    /// was used to create this \ref StopToken.
    AMINO_API bool stopRequested() const;

    /// \brief Check if a stop can be requested on the \ref StopSource that was
    /// used to create this \ref StopToken.
    ///
    /// See \ref StopSource::stopPossible() for more information.
    AMINO_API bool stopPossible() const;

private:
    /// \cond AMINO_INTERNAL_DOCS

    /// \brief Internal equality comparison implementation.
    AMINO_API bool internal_equals(StopToken const& o) const;

    /// \brief Private implementation.
    Internal::PImpl<StopToken, 1> m_impl;

    /// \endcond
};

//=============================================================================
// CLASS StopSource
//=============================================================================

/// \brief A source that can be used to request a stop.
///
/// \note Essentially the same as `std::stop_source`.
class StopSource {
public:
    /// \brief Default constructor (constructs a valid \ref StopSource).
    AMINO_API StopSource();

    /// \brief Construct a non-stoppable \ref StopSource.
    ///
    /// \post \ref stopPossible() will return `false`.
    AMINO_API explicit StopSource(NoStopState_t) noexcept;

    /// \brief Move constructor.
    AMINO_API StopSource(StopSource&& o) noexcept;

    /// \brief Copy constructor.
    AMINO_API StopSource(StopSource const& o);

    /// \brief Destructor.
    AMINO_API ~StopSource();

    /// \brief Move assignment operator.
    AMINO_API StopSource& operator=(StopSource&& o) noexcept;

    /// \brief Copy assignment operator.
    AMINO_API StopSource& operator=(StopSource const& o);

    /// \brief Equality operators
    /// \{
    friend bool operator==(StopSource const& lhs, StopSource const& rhs) {
        return lhs.internal_equals(rhs);
    }
    friend bool operator!=(StopSource const& lhs, StopSource const& rhs) {
        return !lhs.internal_equals(rhs);
    }
    /// \}

    /// \brief Get a \ref StopToken that can be used to check if a stop has been
    /// requested from this \ref StopSource.
    AMINO_API StopToken getToken() const noexcept;

    /// \brief Request a stop.
    ///
    /// \post All \ref StopToken instances created from this \ref StopSource
    /// will report that a stop has been requested.
    AMINO_API void requestStop() noexcept;

    /// \brief Check if a stop has been requested for this \ref StopSource.
    AMINO_API bool stopRequested() const;

    /// \brief Check if a stop can be requested for this \ref StopSource.
    ///
    /// Returns `false` if the \ref StopSource was constructed with a
    /// \ref NoStopState_t, `true` otherwise.
    AMINO_API bool stopPossible() const;

private:
    /// \cond AMINO_INTERNAL_DOCS

    /// \brief Internal equality comparison implementation.
    AMINO_API bool internal_equals(StopSource const& o) const;

    /// \brief Private implementation.
    Internal::PImpl<StopSource, 1> m_impl;

    /// \endcond
};

//==============================================================================
// CLASS StopCallback
//==============================================================================

/// \brief A callback that can be attached to a \ref StopToken.
///
/// \note Essentially the same as `std::stop_callback`.
template <typename Callback>
class StopCallback : private Internal::StopCallbackImpl<Callback> {
public:
    /// \brief Constructor.
    /// \{
    template <typename C>
    StopCallback(StopToken const& token, C&& cb)
        : Internal::StopCallbackImpl<Callback>{token, std::forward<C>(cb)} {}

    template <typename C>
    StopCallback(StopToken&& token, C&& cb)
        : Internal::StopCallbackImpl<Callback>{
              std::move(token), std::forward<C>(cb)} {}
    /// \}

    /// \brief \ref StopCallback is not copyable nor movable.
    /// \{
    StopCallback(StopCallback const&)                = delete;
    StopCallback(StopCallback&&) noexcept            = delete;
    StopCallback& operator=(StopCallback const&)     = delete;
    StopCallback& operator=(StopCallback&&) noexcept = delete;
    /// \}

    /// \brief Destructor.
    ~StopCallback() = default;
};

//------------------------------------------------------------------------------
//
/// \brief Deduction guides for \ref StopCallback.
/// \{
template <typename Callback>
StopCallback(StopToken const&, Callback) -> StopCallback<Callback>;
template <typename Callback>
StopCallback(StopToken&&, Callback) -> StopCallback<Callback>;
/// \}

} // namespace Amino
#undef AMINO_API

#endif

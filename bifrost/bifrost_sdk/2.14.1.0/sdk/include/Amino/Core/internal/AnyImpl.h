//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_ANY_IMPL_H
#define AMINO_CORE_INTERNAL_ANY_IMPL_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  AnyImpl.h
/// \brief Internal implementation details for \ref Amino::Any.

#include <Amino/Core/AnyFwd.h>

#include <Amino/Core/TypeId.h>

#include "ConfigMacros.h"
#include "TypeTraits.h"

#include <cassert>
#include <cstdlib>
#include <new>
#include <utility>

//==============================================================================
// NAMESPACE Amino::Internal
//==============================================================================

namespace Amino {
namespace Internal {

// Forward declarations
class RuntimeAny;
class AnyCast;
class AnyTraits;

//------------------------------------------------------------------------------
//
/// \brief Private implementation details for \ref Amino::Any.
class AnyImpl {
private:
    /*----- friend declarations -----*/

    friend ::Amino::Any; // To derive from AnyUntyped (its private impl)
    friend RuntimeAny;   // Implements "runtime" created Anys
    friend AnyCast;      // To upcast Any -> AnyUntyped (below)
    friend AnyTraits;    // For enable_ifs and static_asserts

    /*----- forward declarations -----*/

    class AnyRep;     // Any's data representation (without payload handling)
    class AnyUntyped; // Any's private impl (with type-erased payload handling)

    /*----- static data members -----*/

    /// \brief Control the size, in multiples of sizeof(void *), where Small
    /// Buffer Optimization (SBO) kicks in for \ref Any.
    ///
    /// This should be 1 less than a power of two. Values of 3 or 7 are
    /// recommended (and have been tested). Values larger than 7 will likely be
    /// very wasteful of space and performance. A value of 3 equates to
    /// \ref Any using 32 bytes, and a value of 7 equates to 64 bytes.
    ///
    /// \warning Do not change this value or the internal layout of \ref Any
    /// without recompiling the entire Amino system and libraries, including the
    /// Amino graph compiler, as it needs to know the size and binary layout of
    /// \ref Any, along with the ABI to the \ref Action handlers that move, copy
    /// and destroy \ref Any instances.
    static constexpr std::size_t sBufferSize = 3 * sizeof(void*);

    /// \brief The alignment requirement for the small data buffer in bytes.
    ///
    /// In practice, we use 8-bytes alignments on all platforms.
    ///
    /// \note It used to be 16-bytes on Unix platforms and 8-bytes on Windows.
    /// An alignment value of 16 bytes would have ensured that small arrays such
    /// as float4 (that would be 16-bytes aligned) are aligned suitably for
    /// efficient SSE operations. But differences in alignments on different
    /// platforms would also have implied that 16-byte aligned SSE data types
    /// would be stored in large buffers by \ref Any on Windows, instead of
    /// more efficient small buffers on Unix. This is unfortunate but somewhat
    /// unavoidable unless we force all of our clients with to compile with
    /// _ENABLE_EXTENDED_ALIGNED_STORAGE. The issue happens when \ref Any
    /// objects are constructed inside memory managed by the aligned buffer
    /// (which could be used as internal for any data structure). Also note,
    /// that it is unsafe to try to use _DISABLE_EXTENDED_ALIGNED_STORAGE as a
    /// workaround as it only causes the aligned storage to ignore the 16-byte
    /// alignment.
    /// \see
    /// https://devblogs.microsoft.com/cppblog/stl-features-and-fixes-in-vs-2017-15-8
    ///
    /// \note, The size of an object in C++ must be a non 0 multiple of its
    /// alignment. If you apply a more restrictive (larger) alignment, the size
    /// will be adjusted up (with padding) by the compiler to satisfy this
    /// constraint. To avoid potential lost of bytes (padding), we set the
    /// alignment constraint on the \ref Any, rather than its buffer type. In
    /// this case, it doesn't make a difference since 24-bytes is a multiple of
    /// 8-bytes, but it would if we wanted to force the buffer to be 16-bytes
    /// aligned for example.
    static constexpr std::size_t sBufferAlign = alignof(void*);

    /*----- types -----*/

    //==========================================================================
    // STRUCT Action
    //==========================================================================

    /// \brief Base class for all "virtual" action performed on an \ref Any.
    ///
    /// See \ref VirtualActions for details.
    struct Action {
    protected:
        Action() = default;
    };

    //==========================================================================
    // TYPEDEF VTablePtr
    //==========================================================================

    /// \brief Function pointer to the function that knows how to handle the
    /// \ref Any, given the payload it manages.
    using VTablePtr = void (*)(Action& action);

    //==========================================================================
    // STRUCT IsAny
    //==========================================================================

    /// \brief Whether the given type `T` is an \ref AnyRep or not.
    template <typename T>
    struct IsAny : public std::is_base_of<AnyRep, std::decay_t<T>> {};

    //==========================================================================
    // STRUCT Buffer
    //==========================================================================

    /// \brief \ref Any's payload small buffer (used to store the payload
    /// in-place when possible, see \ref IsSmall).
    ///
    /// \note Note that we use `alignas(VTablePtr)` here, rather than
    /// `alignas(sBufferAlign)`. See \ref sBufferAlign for details.
    struct alignas(VTablePtr) Buffer {
        // NOLINTNEXTLINE(cppcoreguidelines-avoid-c-arrays,modernize-avoid-c-arrays)
        unsigned char m_buffer[sBufferSize];
    };
    static_assert(sizeof(Buffer) == sBufferSize, "Bad Buffer size.");
    static_assert(alignof(Buffer) == alignof(void*), "Bad Buffer align.");

    //==========================================================================
    // CLASS VTable
    //==========================================================================

    /// \brief "Virtual" table used to perform different actions (destroy, copy,
    /// move, get payload, get TypeId, etc.) on an \ref Any.
    ///
    /// When a \ref Any is constructed/assigned to contain a specific payload,
    /// this \ref Any will also capture a function pointer associated with that
    /// payload type that knows how to handle the payload type. This \ref VTable
    /// class is the semantic wrapper around this handler function.
    class VTable {
    public:
        /*----- member functions -----*/

        /// \brief Default constructor.
        ///
        /// The default constructed \ref VTable manages no payload type. It's
        /// the \ref VTable used for \ref Amino::Any that contain no payload.
        constexpr VTable() noexcept : m_impl(nullptr) {}

        /// \brief Construct a \ref VTable with the pointer to its
        /// implementation.
        constexpr explicit VTable(VTablePtr impl) noexcept : m_impl(impl) {}

        /// \brief Nullify this \ref VTable.
        ///
        /// Used when an \ref Any no longer manages a payload.
        VTable& operator=(std::nullptr_t) noexcept {
            m_impl = nullptr;
            return *this;
        }

        /// \brief Equality operators.
        /// \{
        bool operator==(VTable const& o) const { return m_impl == o.m_impl; }
        bool operator!=(VTable const& o) const { return !(*this == o); }
        bool operator==(std::nullptr_t) const { return m_impl == nullptr; }
        bool operator!=(std::nullptr_t) const { return !(*this == nullptr); }
        /// \}

        /// \brief Destroys the \ref AnyRep managed by this \ref VTable
        void destroy(AnyRep& self) const;

        /// \brief Copy constructs the \ref AnyRep managed by this \ref VTable
        void copy_construct(AnyRep const& self, AnyRep& dst) const;

        /// \brief Move constructs the \ref AnyRep managed by this \ref VTable
        void move_construct(AnyRep&& self, AnyRep& dst) const;

        /// \brief Get the payload of the managed \ref AnyRep managed by this
        /// \ref VTable if its payload type matches the given \ref TypeId, or
        /// nullptr otherwise.
        void const* getPayload(AnyRep const& self, TypeId typeId) const;

        /// \brief Get the payload of the \ref AnyRep managed by this \ref
        /// VTable.
        void const* getPayload(AnyRep const& self) const;

        /// \brief Get the \ref TypeId of the payload of the \ref AnyRep managed
        /// by this \ref VTable.
        TypeId getTypeId(AnyRep const& self) const;

        /// \brief Get the \ref VTable address.
        ///
        /// \warning This should only be used by the Amino backend linker.
        VTablePtr getAddressForLinker() const { return m_impl; }

    private:
        /// \brief Calls the handler function with the given \ref Action.
        template <typename ActionType>
        decltype(auto) invoke(ActionType action) const;

        /*----- data members -----*/

        /// \brief Function pointer to the implementation.
        VTablePtr m_impl;
    };
    static_assert(sizeof(VTable) == sizeof(void*), "Bad VTable size");
    static_assert(alignof(VTable) == alignof(void*), "Base VTable align");

    //==========================================================================
    // CLASS AnyRep
    //==========================================================================

    /// \brief \ref Any's internal representation (\ref Buffer + \ref VTable).
    class alignas(sBufferAlign) AnyRep {
    public:
        /// \brief AnyRep's copy/move constructor/assignement must be defined by
        /// its derived classes (\ref AnyTyped and \ref AnyUntyped).
        /// \{
        AnyRep(AnyRep const& o)                = delete;
        AnyRep(AnyRep&& o) noexcept            = delete;
        AnyRep& operator=(AnyRep const& o)     = delete;
        AnyRep& operator=(AnyRep&& o) noexcept = delete;
        /// \}

        /// \brief Whether this \ref AnyRep has a value (a payload) or not.
        bool has_value() const { return m_vtable != nullptr; }

        /// \brief Returns the \ref VTable used to manage the payload of this
        /// \ref AnyRep.
        VTable getVTable() const { return m_vtable; }

    protected:
        /// \brief \ref AnyRep is not directly constructible / destructible.
        /// Only its derived classes are.
        /// \{
        AnyRep() noexcept  = default;
        ~AnyRep() noexcept = default;
        /// \}

        /// \brief The payload for \ref Any
        ///
        /// \details Either the data itself for small payloads, or a pointer to
        /// the payload for large payloads.
        ///
        /// \note Putting the data storage first allows aligning the data more
        /// strictly than the alignment of void * without adding padding to the
        /// structure.
        Buffer m_buffer{}; // 24 bytes +

        /// \brief Pointer to the action handler function
        /// \details Used to perform delete, copy, move and query operations.
        VTable m_vtable{}; // 8 bytes = 32 bytes
    };
    static_assert(
        sizeof(AnyRep) == sizeof(Buffer) + sizeof(VTable),
        "There should be no padding in AnyRep.");
    static_assert(sizeof(AnyRep) == 32, "Bad AnyRep size");
    static_assert(alignof(AnyRep) == 8, "Bad AnyRep align");

    //==========================================================================
    // CLASS AnyUntyped
    //==========================================================================

    /// \brief Internal implementation of \ref Any.
    class AnyUntyped : public AnyRep {
        friend AnyCast;

        /// \brief Helper to enable the explicit constructor of \ref AnyUntyped
        /// to contruct it with `T` as its payload.
        template <typename T>
        using enable_if_payload = std::enable_if_t<!IsAny<T>::value>;

    public:
        /// \copydoc Any::Any()
        AnyUntyped() noexcept = default;

        /// \copydoc Any::Any(ValueType&&)
        template <typename ValueType, typename = enable_if_payload<ValueType>>
        explicit AnyUntyped(ValueType&& v) {
            construct<ValueType>(*this, std::forward<ValueType>(v));
        }

        /// \copydoc Any::Any(Any const&)
        AnyUntyped(AnyUntyped const& other) {
            other.m_vtable.copy_construct(other, *this);
        }

        /// \copydoc Any::Any(Any&&)
        AnyUntyped(AnyUntyped&& other) noexcept {
            other.m_vtable.move_construct(std::move(other), *this);
        }

        /// \copydoc Any::operator=(Any const& rhs)
        AnyUntyped& operator=(AnyUntyped const& rhs) {
            reset();
            rhs.m_vtable.copy_construct(rhs, *this);
            return *this;
        }

        /// \copydoc Any::operator=(Any&& rhs)
        AnyUntyped& operator=(AnyUntyped&& rhs) noexcept {
            reset();
            rhs.m_vtable.move_construct(std::move(rhs), *this);
            return *this;
        }

        /// \copydoc Any::~Any
        ~AnyUntyped() { reset(); }

        /// \copydoc Any::emplace
        template <typename T, typename... Args>
        void emplace(Args&&... args) {
            reset();
            construct<T>(*this, std::forward<Args>(args)...);
        }

        /// \copydoc Any::reset
        void reset() { m_vtable.destroy(*this); }

        /// \copydoc Any::type
        TypeId type() const { return m_vtable.getTypeId(*this); }

        /// \copydoc Any::swap
        static void swap(AnyUntyped& lhs, AnyUntyped& rhs) noexcept {
            // do no-op if it is a self swap.
            if (&lhs == &rhs) return;
            if (lhs.has_value() && rhs.has_value()) {
                AnyUntyped tmp{std::move(rhs)};
                rhs = std::move(lhs);
                lhs = std::move(tmp);
            } else if (lhs.has_value()) {
                rhs = std::move(lhs);
            } else if (rhs.has_value()) {
                lhs = std::move(rhs);
            }
        }
    };
    static_assert(sizeof(AnyUntyped) == sizeof(AnyRep), "Bad size");
    static_assert(alignof(AnyUntyped) == alignof(AnyRep), "Bad align");

    //==========================================================================
    // CLASS AnyTyped<BufferType>
    //==========================================================================

    /// \brief \ref Any's internal when interpreted as containing a specific
    /// buffer type.
    ///
    /// \details This "typed" representation of the \ref Any is used in the
    /// implementation of the \ref VTable for the given buffer type.
    template <typename BufferType>
    class AnyTyped final : public AnyRep {
    public:
        // The buffer type must fit in the small buffer of the Any and have the
        // same alignment as the small buffer of the Any.
        static_assert(
            sizeof(BufferType) <= sBufferSize,
            "BufferType is too large to fit in Buffer");
        static_assert(
            alignof(BufferType) <= sBufferAlign,
            "Buffer has stricter alignment requirements");

        /// \brief Constructor.
        template <typename... Args>
        explicit AnyTyped(VTable vtable, Args&&... args) {
            new (&m_buffer) BufferType(std::forward<Args>(args)...);
            m_vtable = vtable;
            assert(isa<AnyTyped>(*this));
        }

        /// \brief Copy constructor.
        AnyTyped(AnyTyped const& o) : AnyTyped(o.m_vtable, o.getBuffer()) {}

        /// \brief Move constructor.
        AnyTyped(AnyTyped&& o) noexcept
            : AnyTyped(o.m_vtable, std::move(o.getBuffer())) {
            o.m_vtable = nullptr;
        }

        /// \brief Default constructor and assignments are not needed by the
        /// \ref VTable implementations.
        ///
        /// Using them would likely indicate a programming error.
        /// \{
        AnyTyped()                             = delete;
        AnyTyped& operator=(AnyTyped const& o) = delete;
        AnyTyped& operator=(AnyTyped&& o)      = delete;
        /// \}

        /// \brief Destructor.
        ~AnyTyped() {
            getBuffer().~BufferType();
            m_vtable = nullptr;
        }

        /// \brief Get the payload of this \ref AnyTyped.
        auto const* getPayload() const& {
            assert(getBuffer().getPayload());
            return getBuffer().getPayload();
        }

        /// \brief Get the payload of this \ref AnyTyped if its type \ref TypeId
        /// matches the given \ref TypeId.
        auto const* getPayload(TypeId typeId) const& {
            return getTypeId() == typeId ? getPayload() : nullptr;
        }

        /// \copydoc AnyUntyped::type
        TypeId getTypeId() const { return getBuffer().getTypeId(); }

        /// \brief Get the interpreted buffer of this \ref AnyTyped.
        BufferType const& getBuffer() const& {
            assert(isa<AnyTyped>(*this)); // make sure we can cast!
            return *reinterpret_cast<BufferType const*>(&m_buffer);
        }

    private:
        friend BufferType;

        /// \brief Get the interpreted buffer of this \ref AnyTyped.
        BufferType& getBuffer() & {
            auto const& cthis = *this;
            return const_cast<BufferType&>(cthis.getBuffer());
        }
    };

    //==========================================================================
    // STRUCT IsSmall<T>
    //==========================================================================

    /// \brief Traits to know if a payload of type `T` can be stored directly
    /// in the \ref Any's buffer (can use SBO) or not.
    template <typename T>
    struct IsSmall final {
        static_assert(
            std::is_same<T, std::decay_t<T>>::value,
            "T should have been decayed already.");
        static constexpr bool value =
            (sizeof(T) <= sBufferSize) &&
            (std::alignment_of<T>::value <= sBufferAlign) &&
            std::is_standard_layout<T>::value &&
            std::is_move_constructible<T>::value;
    };

    //==========================================================================
    // CLASS SmallBuffer<T>
    //==========================================================================

    /// \brief Buffer interpretation for the buffer of an \ref Any that
    /// contains a payload of type `T` that satisfies requirements to be
    /// constructed directly in that buffer.
    ///
    /// Such payload do not require heap allocations, as they leverage this
    /// Small Buffer Optimization (SBO).
    template <typename T>
    class SmallBuffer {
        static_assert(IsSmall<T>::value, "Should have used a LargeBuffer!");

    public:
        /// \brief Constructs the payload `T` in the SmallBuffer with the given
        /// arguments.
        template <typename... Args>
        explicit SmallBuffer(Args&&... args)
            : m_payload(std::forward<Args>(args)...) {}

        /// \brief Copy constructor (copy constructs the payload)
        SmallBuffer(SmallBuffer const& o) = default;

        /// \brief Move constructor (move constructs the payload)
        SmallBuffer(SmallBuffer&& o) noexcept = default;

        /// \brief Destructor (destroys the payload)
        ~SmallBuffer() = default;

        /// \copydoc AnyTyped::AnyTyped()
        /// \{
        SmallBuffer()                                    = delete;
        SmallBuffer& operator=(SmallBuffer const& o)     = delete;
        SmallBuffer& operator=(SmallBuffer&& o) noexcept = delete;
        /// \}

        /// \copydoc AnyTyped::getPayload
        /// \{
        T const* getPayload() const& { return &m_payload; }
        T*       getPayload() & { return &m_payload; }
        /// \}

        /// \copydoc AnyTyped::getTypeId
        TypeId getTypeId() const { return ::Amino::getTypeId<T>(); }

        /// \brief Implementation function of the \ref VTable for SmallBuffer<T>
        static void apply_action(Action& action) {
            VirtualActions::apply_action<AnyTyped<SmallBuffer>>(action);
        }

    private:
        /// \brief The payload value, constructed in this small buffer.
        T m_payload;
    };

    //==========================================================================
    // CLASS LargeBuffer<T>
    //==========================================================================

    /// \brief Buffer interpretation for the buffer of an \ref Any that
    /// contains a payload of type `T` that DOES NOT satisfy requirements to be
    /// constructed directly in that buffer.
    ///
    /// Such payloads are allocated on heap, and the buffer only contains a
    /// pointer to that heap-allocated payload.
    template <typename T>
    class alignas(Buffer) LargeBuffer {
        static_assert(!IsSmall<T>::value, "Should have used a SmallBuffer!");

    public:
        /// \brief Constructs the payload `T` on heap, and keep a pointer to it
        /// in the buffer.
        template <typename... Args>
        explicit LargeBuffer(Args&&... args)
            : m_payload(new T(std::forward<Args>(args)...)) {}

        /// \brief Copy constructor (copy constructs the payload on heap)
        LargeBuffer(LargeBuffer const& o) : m_payload(new T(*o.m_payload)) {}

        /// \brief Move constructor (steals the pointer to the payload on heap)
        LargeBuffer(LargeBuffer&& o) noexcept : m_payload(o.m_payload) {
            o.m_payload = nullptr;
        }

        /// \brief Destructor (deletes the payload)
        ~LargeBuffer() { delete m_payload; }

        /// \copydoc AnyTyped::AnyTyped()
        /// \{
        LargeBuffer()                                    = delete;
        LargeBuffer& operator=(LargeBuffer const& o)     = delete;
        LargeBuffer& operator=(LargeBuffer&& o) noexcept = delete;
        /// \}

        /// \copydoc AnyTyped::getPayload
        /// \{
        T const* getPayload() const& { return m_payload; }
        T*       getPayload() & { return m_payload; }
        /// \}

        /// \copydoc AnyTyped::getTypeId
        TypeId getTypeId() const { return ::Amino::getTypeId<T>(); }

        /// \brief Implementation function of the \ref VTable for LargeBuffer<T>
        static void apply_action(Action& action) {
            VirtualActions::apply_action<AnyTyped<LargeBuffer>>(action);
        }

    private:
        /// \brief The payload value, allocated on heap.
        T* m_payload;
    };

    //==========================================================================
    // CLASS DeadBeefBuffer
    //==========================================================================

    /// \brief Buffer used in debug builds to assign "deadbeef" memory in the
    /// \ref Any's small buffer, in order to try to detect undefined behavior
    /// from accessing a destroyed buffer/payload.
    class alignas(Buffer) DeadBeefBuffer {
    public:
        /// \brief Assigns "deadbeef" values in the small buffer of the \ref
        /// Any.
        static void clear(AnyRep& AMINO_INTERNAL_ASSERT_CODE(any)) {
            AMINO_INTERNAL_ASSERT_BLOCK({
                assert(!any.has_value());
                auto& buffer = cast<AnyTyped<DeadBeefBuffer>>(any).getBuffer();
                buffer       = DeadBeefBuffer();
            });
        }
        static constexpr std::nullptr_t apply_action = nullptr;

        size_t db1 = 0xDEADBEEFBEEFCAFE;
        size_t db2 = 0xDEADBEEFBEEFCAFE;
        size_t db3 = 0xDEADBEEFBEEFCAFE;
    };
    static_assert(
        sizeof(DeadBeefBuffer) == sizeof(Buffer),
        "DeadBeefBuffer should take the full Buffer space.");
    static_assert(
        alignof(DeadBeefBuffer) == alignof(Buffer),
        "DeadBeefBuffer should have same alignment as Buffer");

    //==========================================================================
    // CLASS VirtualActions
    //==========================================================================

    /// \brief Class that defines all actions that can be applied on an \ref
    /// Any and that provides the templated implementation to apply such actions
    /// on an \ref AnyTyped.
    class VirtualActions {
        friend VTable;
        friend RuntimeAny;

    public:
        /// \brief Applies the given \ref Action on the \ref Any for which it
        /// was created.
        template <typename AnyTyped>
        static void apply_action(Action& action) {
            visit(ApplyActionFor<AnyTyped>{}, action);
        }

    private:
        /*----- types -----*/

        /// \brief The Action kind, used to "dynamic_cast" the \ref Action to
        /// its derived action type.
        enum class ActionKind {
            eDestroy,
            eCopy,
            eMove,
            eGet,
            eGetVoid,
            eGetTypeId
        };

        /// \brief Base class of all derived actions.
        struct ActionImpl : public Action {
            explicit ActionImpl(ActionKind kind) : m_kind(kind) {}

            template <typename ActionType>
            bool is() const {
                return m_kind == ActionType::s_kind;
            }
            template <typename ActionType>
            ActionType const& as() const& {
                assert(is<ActionType>());
                return static_cast<ActionType const&>(*this);
            }
            template <typename ActionType>
            ActionType& as() & {
                assert(is<ActionType>());
                return static_cast<ActionType&>(*this);
            }
            ActionKind const m_kind;
        };

        /// \brief Base \ref ActionKind templated class for all derived actions.
        template <ActionKind Kind>
        struct ActionT : public ActionImpl {
            static constexpr auto s_kind = Kind;
            ActionT() : ActionImpl{Kind} {}
        };

        /// \brief Destroy action (used to destroys the given \ref AnyRep).
        struct Destroy : ActionT<ActionKind::eDestroy> {
            explicit Destroy(AnyRep& self) : m_self(self) {}
            void    result() const {}
            AnyRep& m_self;
        };

        /// \brief Copy action (used to copy construct the given \ref AnyRep).
        struct Copy : ActionT<ActionKind::eCopy> {
            explicit Copy(AnyRep const& self, AnyRep& dst)
                : m_self(self), m_dst(dst) {}
            void          result() const {}
            AnyRep const& m_self;
            AnyRep&       m_dst;
        };

        /// \brief Move action (used to move construct the given \ref AnyRep).
        struct Move : ActionT<ActionKind::eMove> {
            explicit Move(AnyRep&& src, AnyRep& dst)
                : m_self(std::move(src)), m_dst(dst) {}
            void     result() const {}
            AnyRep&& m_self;
            AnyRep&  m_dst;
        };

        /// \brief Get action (used to get the address of the payload the given
        /// \ref AnyRep if it matches the given \ref TypeId).
        struct Get : ActionT<ActionKind::eGet> {
            explicit Get(AnyRep const& src, TypeId typeId)
                : m_self(src), m_typeId(typeId), m_result(nullptr) {}
            void const*   result() const { return m_result; }
            AnyRep const& m_self;
            TypeId        m_typeId;
            void const*   m_result;
        };

        /// \brief GetVoid action (used to get the address of the payload the
        /// given \ref AnyRep).
        struct GetVoid : ActionT<ActionKind::eGetVoid> {
            explicit GetVoid(AnyRep const& src)
                : m_self(src), m_result(nullptr) {}
            void const*   result() const { return m_result; }
            AnyRep const& m_self;
            void const*   m_result;
        };

        /// \brief GetTypeId action (used to get the \ref TypeId of the given
        /// \ref AnyRep).
        struct GetTypeId : ActionT<ActionKind::eGetTypeId> {
            explicit GetTypeId(AnyRep const& self)
                : m_self(self), m_result(Amino::getTypeId<NullTypeInfo>()) {}
            TypeId        result() const { return m_result; }
            AnyRep const& m_self;
            TypeId        m_result;
        };

        /// \brief Visitor used to apply an \ref Action for a \ref AnyRep,
        /// interpreting it as the given \ref AnyTyped.
        template <typename AnyTyped>
        struct ApplyActionFor {
            static_assert(IsAny<AnyTyped>::value, "Not an Any");
            static_assert(sizeof(AnyTyped) == sizeof(AnyRep), "Bad size");
            static_assert(alignof(AnyTyped) == alignof(AnyRep), "Bad align");

            /*----- member functions -----*/

            void operator()(Destroy& ac) const {
                cast<AnyTyped>(ac.m_self).~AnyTyped();
                DeadBeefBuffer::clear(ac.m_self);
            }
            void operator()(Copy& ac) const {
                new (&ac.m_dst) AnyTyped{cast<AnyTyped>(ac.m_self)};
            }
            void operator()(Move& ac) const {
                new (&ac.m_dst) AnyTyped{std::move(cast<AnyTyped>(ac.m_self))};
                DeadBeefBuffer::clear(ac.m_self);
            }
            void operator()(Get& ac) const {
                ac.m_result = cast<AnyTyped>(ac.m_self).getPayload(ac.m_typeId);
            }
            void operator()(GetVoid& ac) const {
                ac.m_result = cast<AnyTyped>(ac.m_self).getPayload();
            }
            void operator()(GetTypeId& ac) const {
                ac.m_result = cast<AnyTyped>(ac.m_self).getTypeId();
            }
        };

        /*----- static member function -----*/

        ///  \brief Visit the action with the given visitor.
        template <typename Visitor, typename Action>
        static decltype(auto) visit(Visitor&& v, Action& action) {
            using Impl = std::conditional_t< //
                std::is_const<Action>::value, ActionImpl const, ActionImpl>;
            auto& ac   = static_cast<Impl&>(action);
            using K    = ActionKind;
            switch (static_cast<ActionImpl const&>(ac).m_kind) {
                case K::eDestroy: return v(ac.template as<Destroy>());
                case K::eCopy: return v(ac.template as<Copy>());
                case K::eMove: return v(ac.template as<Move>());
                case K::eGet: return v(ac.template as<Get>());
                case K::eGetVoid: return v(ac.template as<GetVoid>());
                case K::eGetTypeId: return v(ac.template as<GetTypeId>());
            }
            AMINO_INTERNAL_UNREACHABLE("All cases return");
        }
    };

    //==========================================================================
    // STRUCT GetBufferType<AnyTyped>
    //==========================================================================

    /// \brief Traits to get the buffer type of an \ref AnyTyped.
    /// \{
    template <typename AnyTyped>
    struct GetBufferType;
    template <typename BufferType>
    struct GetBufferType<AnyTyped<BufferType>> final {
        using type = BufferType;
    };
    template <typename AnyTyped>
    using BufferType_t = typename GetBufferType<AnyTyped>::type;
    /// \}

    /*----- static member functions -----*/

    /// \brief Whether the given \ref AnyRep can be interpreted as an \ref
    /// AnyTyped or not.
    template <typename AnyTyped>
    static bool isa(AnyRep const& any) noexcept {
        return any.getVTable() == VTable{BufferType_t<AnyTyped>::apply_action};
    }

    /// \brief Casts the given \ref AnyRep as the given \ref AnyTyped.
    /// \{
    template <typename AnyTyped>
    static AnyTyped const& cast(AnyRep const& any) noexcept {
        assert(isa<AnyTyped>(any));
        return static_cast<AnyTyped const&>(any);
    }
    template <typename AnyTyped>
    static AnyTyped& cast(AnyRep& any) noexcept {
        assert(isa<AnyTyped>(any));
        return static_cast<AnyTyped&>(any);
    }
    /// \}

    /// \brief Casting an rvalue reference can be error prone, so we delete it.
    template <typename AnyTyped>
    static AnyTyped&& cast(AnyRep&& any) noexcept = delete;

    /// \brief Construct an \ref Any at the given destination address, with this
    /// given `PayloadType`, constructing the payload value from the given
    /// `Args`.
    ///
    /// \note Used by \ref Any to construct/assign payload to itself.
    template <typename ValueType, typename... Args>
    static void construct(AnyRep& dst, Args&&... args) {
        static_assert(!IsAny<ValueType>::value, "Should be a payload");
        assert(!dst.has_value()); // dst should not already have a payload!

        // The payload type to store in the Any.
        using PayloadType = std::decay_t<ValueType>;

        // The buffer type used to store this payload type.
        using BufferType = std::conditional_t< //
            IsSmall<PayloadType>::value,       // Can payload use small buffer?
            SmallBuffer<PayloadType>,          //     if yes, use SBO
            LargeBuffer<PayloadType>>;         //     if no, use heap alloc

        // The Any interpretation to use when to perform concrete operations it.
        using AnyT = AnyTyped<BufferType>;

        auto vtable = VTable{BufferType::apply_action};
        new (&dst) AnyT(vtable, std::forward<Args>(args)...);
    }

    /// \brief AnyImpl is not constructible.
    /// \{
    AnyImpl()  = delete;
    ~AnyImpl() = delete;
    /// \}
};

//==============================================================================
// CLASS AnyImpl::VTable
//==============================================================================

template <typename ActionType>
inline decltype(auto) AnyImpl::VTable::invoke(ActionType action) const {
    static_assert(
        std::is_base_of<VirtualActions::ActionImpl, ActionType>::value,
        "ActionType should be a concrete derived Action!");
    assert(m_impl);
    m_impl(action);
    return action.result();
}

//------------------------------------------------------------------------------
//
inline void AnyImpl::VTable::destroy(AnyRep& self) const {
    assert(*this == self.getVTable());
    if (!m_impl) return; // Nothing to destroy!
    invoke(VirtualActions::Destroy{self});
    assert(!self.has_value()); // Should be empty after destruction
}

//------------------------------------------------------------------------------
//
inline void AnyImpl::VTable::copy_construct(
    AnyRep const& self, AnyRep& dst) const {
    assert(*this == self.getVTable());
    assert(!dst.has_value()); // dst should be empty!
    if (!m_impl) return;      // Nothing to copy!
    return invoke(VirtualActions::Copy{self, dst});
}

//------------------------------------------------------------------------------
//
inline void AnyImpl::VTable::move_construct(AnyRep&& self, AnyRep& dst) const {
    assert(*this == self.getVTable());
    assert(!dst.has_value()); // dst should be empty!
    if (!m_impl) return;      // Nothing to move!
    return invoke(VirtualActions::Move{std::move(self), dst});
}

//------------------------------------------------------------------------------
//
inline void const* AnyImpl::VTable::getPayload(
    AnyRep const& self, TypeId typeId) const {
    assert(*this == self.getVTable());
    if (!m_impl) return nullptr; // No payload!
    return invoke(VirtualActions::Get{self, typeId});
}

//------------------------------------------------------------------------------
//
inline void const* AnyImpl::VTable::getPayload(AnyRep const& self) const {
    assert(*this == self.getVTable());
    if (!m_impl) return nullptr; // No payload!
    return invoke(VirtualActions::GetVoid{self});
}

//------------------------------------------------------------------------------
//
inline TypeId AnyImpl::VTable::getTypeId(AnyRep const& self) const {
    assert(*this == self.getVTable());
    if (!m_impl) return Amino::getTypeId<void>(); // No payload!
    return invoke(VirtualActions::GetTypeId{self});
}

//==============================================================================
// CLASS AnyCast
//==============================================================================

/// \brief Implementation of \ref Amino::any_cast.
class AnyCast final {
public:
    /*----- static member functions -----*/

    /// \brief Get the payload of the \ref Any if its payload type is a `T`.
    template <typename T, typename Any>
    static auto* cast(Any* any) {
        static_assert(IsAny<Any>::value, "Should be an Amino::Any only");
        assert(any);
        return cast_impl(*any, ID<T>{});
    }

    /// \brief Get the payload of the \ref Any if its payload has the given
    /// \ref TypeId.
    template <typename Any>
    static auto* cast(Any* any, TypeId typeId) {
        static_assert(IsAny<Any>::value, "Should be an Amino::Any only");
        assert(any);
        return cast_impl(*any, typeId);
    }

    /// \brief AnyCast is not constructible.
    /// \{
    AnyCast()  = delete;
    ~AnyCast() = delete;
    /// \}

private:
    /*----- types -----*/

    using AnyUntyped = AnyImpl::AnyUntyped;

    /// \brief Helper struct to create overloads.
    template <typename T>
    struct ID {};

    template <typename T>
    using IsAny = std::is_same<std::remove_const_t<T>, Amino::Any>;

    /*----- static member functions -----*/

    /// \brief Get the payload of the \ref Any if its payload has the given
    /// \ref TypeId.
    static void const* cast_impl(AnyUntyped const& any, TypeId typeId) {
        return any.m_vtable.getPayload(any, typeId);
    }

    /// \brief Get the payload of the \ref Any if its payload type is a `T`.
    template <typename T>
    static T const* cast_impl(AnyUntyped const& any, ID<T>) {
        static_assert(!IsAny<T>::value, "Should be a payload");
        return static_cast<T const*>(cast_impl(any, getTypeId<T>()));
    }

    /// \brief Get the pointer to the payload of the given \ref Any.
    static void const* cast_impl(AnyUntyped const& any, ID<void>) {
        return any.m_vtable.getPayload(any);
    }

    /// \brief Get the pointer to the payload of the given \ref Any.
    static void* cast_impl(AnyUntyped& any, ID<void>) {
        return const_cast<void*>(any.m_vtable.getPayload(any));
    }

    /// \brief Get a non-const pointer the payload of the given \ref Any.
    template <typename Arg>
    static auto cast_impl(AnyUntyped& any, Arg const& arg) {
        auto* addr = cast_impl(static_cast<AnyUntyped const&>(any), arg);
        using T    = std::remove_pointer_t<decltype(addr)>;
        static_assert(
            std::is_const<T>::value,
            "Should have called the const version of this cast_impl!");
        return const_cast<std::remove_const_t<T>*>(addr);
    }
};

//------------------------------------------------------------------------------
//
template <typename T, typename Any>
decltype(auto) any_cast(Any* any) {
    return AnyCast::cast<T>(any);
}

//==============================================================================
// CLASS AnyTraits
//==============================================================================

/// \brief Expose some traits about \ref Any and payload types.
class AnyTraits final {
public:
    /// \brief Size (in bytes) of the small buffer in the \ref Any.
    ///
    /// \warning This is only exposed for tests.
    static constexpr auto sBufferSize = AnyImpl::sBufferSize;

    /// \brief Alignment of the \ref Any.
    ///
    /// \warning This is only exposed for tests.
    static constexpr auto sBufferAlign = AnyImpl::sBufferAlign;

    /// \brief Traits to know if a payload of type T can be stored in the small
    /// buffer of the \ref Any.
    ///
    /// \warning This is only exposed for tests.
    template <typename T>
    using IsSmall = AnyImpl::IsSmall<T>;
};

//------------------------------------------------------------------------------
//
template <>
struct GetTypeCategory<Any> {
    static constexpr auto value = TypeCategory::eAny;
};
} // namespace Internal
} // namespace Amino
/// \endcond

#endif

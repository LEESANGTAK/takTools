//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

#ifndef AMINO_PTR_REP_H
#define AMINO_PTR_REP_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  PtrRep.h
/// \brief Amino::PtrInternal::PtrRep: Internal representation of Amino::Ptr
/// \see   Amino::PtrInternal::PtrRep

#include "ConfigMacros.h"

#include "DefaultClassDeclare.h"
#include "StaticAnalysis.h"
#include "TypeTraits.h"

#include <atomic>
#include <cassert>
#include <cstdint>
#include <type_traits>
#include <utility>

namespace Amino {

//==============================================================================
// CLASS PointeeManager
//==============================================================================

/// \brief Struct used to restrain access to "new" and "delete" operators of
/// classes.
///
/// One can make "new" and "delete" operators non public within class
/// declarations to prevent erroneous uses of them. By making only the \ref
/// PointeeManager a friend, pointee will ever only be newed and deleted through
/// Amino::Ptr.
///
/// For example:
///
/// \code{.cpp}
/// class MyClass
/// {
/// protected:
///     friend PointeeManager;
///     ~MyClass();
/// };
/// \endcode
///
///
/// \warning The class is declared in the "Amino" namespace to allow a shorter
/// friendship declaration that does not include internal namespaces (i.e.
/// `friend Amino::PointeeManager;` instead of `friend
/// Amino::PtrInternal::PointeeManager;`). That being said, PointeeManager
/// internals are an internal implementation details and its member functions
/// should never be called (except for Amino itself).
///
struct PointeeManager {
    /// \brief PointeeManager is not constructible. It only has static
    /// functions.
    PointeeManager() = delete;

    /// \brief is_copy_constructible function checker: true_type case
    ///
    /// \note: Before a template struct was used.
    ///        It did not work with GCC on Linux.
    ///        devtoolset-8 and 9
    ///
    /// \todo BIFROST-6530 Include "delete" in template resolution.
    template <typename T>
    static constexpr std::true_type is_copy_constructible_fcn(
        decltype(new T(std::declval<T const&>())));

    /// \brief is_copy_constructible function checker: false_type case
    template <typename T>
    static constexpr std::false_type is_copy_constructible_fcn(...);

    /// \brief Returns whether the type T is copy constructible.
    ///
    /// Note: We need to define our own version of copy_constructible, instead
    /// of using std::is_copy_constructible<T>::value because the std version
    /// fails if the destructor is not public.
    ///
    /// Note:This template must be defined in PointeeManager because the SFINAE
    /// trick bellow must be resolved in a context where the pointer type can
    /// be newed and deleted.
    template <typename T>
    struct is_copy_constructible
        : decltype(is_copy_constructible_fcn<T>(nullptr)) {};

    /// \brief Allocates an object of type \p T and returns it.
    ///
    /// The factory function Amino::newClass<T>() allocates an object of type
    /// \p T.
    ///
    /// \warning The pointee should be managed by an \ref Amino::Ptr or
    /// \ref Amino::MutablePtr immediately after this call.
    ///
    /// \tparam     T     the type of object to allocate
    /// \tparam     Args  the types of the constructor arguments
    /// \param [in] args  the arguments to pass to the constructor of the object
    /// \return           a pointer to the allocated object
    template <typename T, typename... Args>
    inline static T* newClass(Args&&... args);

    /// \brief Implicit deleter for Amino::Ptr
    ///
    /// Amino::Ptr invokes the function PointeeManager::checkedDelete<T>(obj)
    /// when disposing of no longer referenced object, assuming that an explicit
    /// deleter has been specified. The expression
    /// `PointeeManager::checkedDelete(p)` simply invokes `delete p`.
    ///
    /// The `PointeeManager::checkedDelete(p)` entry point provides two
    /// advantages over the raw `delete p` expression.
    ///
    ///    - First, it will fail to compile of \p T is refereeing to an
    ///      incomplete class. This avoids issues when the destructor is
    ///      actually declared virtual, because in this case, `delete p` would
    ///      not perform a virtual function call unless the definition of the
    ///      class is in scope.
    ///    - Secondly, the destructor of the object's class to be declared
    ///      protected or private instead of public. This prevents the object
    ///      being deleted by mistake. This requires a friendship declaration,
    ///      as mentioned in the PointeeManager's documentation.
    ///
    /// \tparam     T     the type of object to deallocate
    /// \param [in] obj   the object to deallocate
    template <typename T>
    inline static void checkedDelete(T* obj);
};
} // namespace Amino

//==============================================================================
// FORWARD DECLARATIONS
//==============================================================================

namespace Amino {

template <typename T>
class Array;

namespace PtrInternal {

struct PtrRepUntyped;
class PtrCntrlBlk;
template <class P>
class PtrCntrlBlkPtr;

} // namespace PtrInternal
} // namespace Amino

namespace Amino {
namespace PtrInternal {

//==============================================================================
// class DefaultPtrTraits
//==============================================================================

class DefaultPtrTraits {
private:
    /// \brief SFINAE helper to know if the entry point to get the default value
    /// is provided for the given type.
    ///
    /// (see \ref AMINO_DECLARE_DEFAULT_CLASS and
    ///      \ref AMINO_DEFINE_DEFAULT_CLASS).
    /// \{
    template <typename T>
    static constexpr std::true_type has_default_class_fcn(
        decltype(Internal::getDefaultClass<T>()));
    template <typename T>
    static constexpr std::false_type has_default_class_fcn(...);
    /// \}

public:
    /// \brief Helper to know if the type T is an Amino::Array type.
    /// \{
    template <typename T>
    struct is_array : public std::false_type {};
    template <typename T>
    struct is_array<Array<T>> : public std::true_type {};
    /// \}

    /// \brief Returns whether the type T can provide a default value
    /// (provided by specializing \ref Amino::Internal::getDefaultClass for
    /// opaque user classes).
    ///
    /// Note that for user classes that must flow in Amino graph, having such
    /// function is MANDATORY (see \ref AMINO_DECLARE_DEFAULT_CLASS and
    /// \ref AMINO_DEFINE_DEFAULT_CLASS).
    template <typename T>
    struct has_default_class
        : public std::integral_constant< //
              bool,
              decltype(has_default_class_fcn<T>(nullptr))::value> {};

    /// \copydoc PointeeTraits::is_defaultable
    template <typename T>
    struct is_defaultable
        : public std::integral_constant< //
              bool,
              has_default_class<T>::value || is_array<T>::value> {};
};

//==============================================================================
// ENUM Uninitialized
//==============================================================================

/// \brief Tag for explicitly specifying the that the constructor
///        should not initialized any data members.
///
/// This is useful because in a number of cases a different
/// mechanism than the base class constructor is used to
/// initialized the data members.
enum Uninitialized { kUninitialized };

//==============================================================================
// STRUCT PtrRepUntyped
//==============================================================================

/// \brief Untyped representation of shared pointers.
///
/// The internal representation of an Amino::Ptr. This
/// representation is accessed by the code generated by the Amino
/// C++ backend. It is exposed an non-templated class to make that
/// integration possible.

struct PtrRepUntyped {
    /// \brief Uninitializing constructor
    ///
    /// This constructor leaves all the data members of the Amino
    /// pointer representation uninitialized. This is useful for
    /// implementing the constructor of derived classes where the
    /// necessary objects are allocated in the constructor body
    /// (mainly for exception safety reason).
    ///
    /// \warning Use with care.
    // NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init)
    explicit PtrRepUntyped(Uninitialized) noexcept {}

    /// \brief Initializing constructor
    ///
    /// Initializes the fields of the Amino pointer representation.
    ///
    /// \param [in] p    The raw bit-wise value of the pointer to the pointee.
    /// \param [in] cblk The shared control block used to manage the
    ///                  life-scope of the owned object.
    constexpr PtrRepUntyped(void* p, PtrCntrlBlk* cblk) noexcept
        : m_pointee(p), m_cntrlBlk(cblk) {}

    /// \brief Return the control block
    ///
    /// \return the control block
    PtrCntrlBlk* getCntrlBlk() const noexcept {
        // m_cntrlBlk is deliberately left uninitialized, so skip
        // clang analyzer check about undefined or garbage values.
        return reinterpret_cast<PtrCntrlBlk*>(m_cntrlBlk); // NOLINT
    }

    /// The owned object
    void* m_pointee;

    /// The control block corresponding to the owned object. This must be of
    /// type PtrCntrlBlk*, but it is store a void* to make it easier to
    /// interface with the LLVM generated code.
    void* m_cntrlBlk;
};

//==============================================================================
// CLASS PtrCntrlBlk
//==============================================================================

/// \brief Base class for the Amino::Ptr control block
///
/// The control block manages the life-scope of the object owned by
/// Amino::Ptr. The class PtrCntrlBlk contains a use count. The use
/// count represents the number of Amino::Ptr referencing the owned
/// object. It is up-to the Amino::Ptr (and PtrRep) to properly
/// invoke the incUseCount() and decUseCount() member function to
/// maintain the accuracy of the use count at all times. The use count
/// is thread-safe.
///
/// When the use count reaches zero, the dispose() virtual member
/// function is invoked. Derived classes must implement the dispose()
/// member function to properly release the owned object and the
/// control block using any proper mechanism. Derive classes must

/// capture all the information necessary by dispose() at the control
/// block construction time. It can't rely on the pointer stored
/// inside the Amino::Ptr as it can legally point to a sub-object of
/// the owned object when the dispose() member function is finally
/// invoked.
class PtrCntrlBlk {
public:
    /*----- types -----*/

    /// The integral type of the use count.
    using use_count_type = std::intptr_t;

    /// \brief A home grown virtual function table.
    ///
    /// We specify the exact layout of our own virtual function
    /// table. I.e. we *DO NOT* want to use the compiler provided
    /// mechanisms for that. The reason is that the virtual function
    /// call might be performed by either MSVC or Clang compiled code
    /// and they do not agree of the format of that table and/or the
    /// calling conventions for virtual member functions!
    struct Vtbl {
        /// \brief Clone the stored object
        ///
        /// This clones the pointee and creates a new pointer control block for
        /// it. The copy is performed using the copy constructor of the object
        /// and allocations are performed using any specified allocators.
        ///
        /// \param [in] oldPointee The previous pointer to a sub-object of the
        ///                        stored pointer.
        ///
        /// \return An untyped pointer representation initialized with the
        /// cloned control block and object. The pointee points to the
        /// corresponding sub-object in the cloned object.
        using ClonePointee =
            PtrRepUntyped (*)(PtrCntrlBlk const* self, void const* oldPointee);

        /// \brief Invoked to dispose of the owned object.
        ///
        /// Invoked when the use count reaches zero. Derived classes must
        /// implement the dispose() member function to properly release
        /// the owned object and the control block using any proper
        /// mechanism.
        using Dispose = void (*)(PtrCntrlBlk* self);

        ClonePointee m_clonePointee;
        Dispose      m_dispose;
    };

    /*----- member functions -----*/

    /// \brief PtrCntrlBlk are not default constructible.
    PtrCntrlBlk() = delete;

    /// \brief PtrCntrlBlk are not copiable nor movable.
    /// \{
    PtrCntrlBlk(PtrCntrlBlk const&)            = delete;
    PtrCntrlBlk(PtrCntrlBlk&&)                 = delete;
    PtrCntrlBlk& operator=(PtrCntrlBlk const&) = delete;
    PtrCntrlBlk& operator=(PtrCntrlBlk&&)      = delete;
    /// \}

    /// \brief Return the value of the use count.
    ///
    /// \note This return a snapshot of the current value. In a
    /// multi-threaded environment, the use count might change at any
    /// time.
    ///
    /// \return the current value of the use count
    use_count_type use_count() const noexcept { return m_useCount; }

    /// \brief Clone the stored object
    ///
    /// This clones the pointee and creates a new pointer control block for
    /// it. The copy is performed using the copy constructor of the object and
    /// allocations are performed using any specified allocators.
    ///
    /// \param [in] oldPointee The previous pointer to a sub-object of the
    ///                        stored pointer.
    /// \return An untyped pointer representation initialized with the cloned
    ///         control block and object. The pointee points to the
    ///         corresponding sub-object in the cloned object.
    PtrRepUntyped clonePointee(void* oldPointee) {
        return m_vtbl->m_clonePointee(this, oldPointee);
    }

protected:
    /*----- static member functions -----*/

    /// \brief Adjust a pointer to point to one of its parent classes.
    ///
    /// Amino::Ptr may have been upcasted to a parent class. When an Amino::Ptr
    /// is cloned, it is the originally captured type that is cloned, but an
    /// Amino::Ptr of the parent class is returned (if it was upcasted). We must
    /// offset the pointee such that it points to the start of that parent
    /// data within the cloned object. This is necessary in the case of multiple
    /// inheritance.
    template <class P>
    static void* adjustUpcastedPointee(
        P* newObject, P const* oldObject, void const* oldUpcastedObject) {
        // Double check that oldUpcastedObject is correctly pointing inside
        // oldObject. Use the offset from the oldUpcastedObject from the
        // oldObject to offset the newObject to point to the newUpcastedObject.
        const auto oldUpcastedObjectAddr =
            reinterpret_cast<std::uintptr_t>(oldUpcastedObject);
        const auto oldObjectAddr = reinterpret_cast<std::uintptr_t>(oldObject);
        assert(oldUpcastedObjectAddr >= oldObjectAddr);
        assert(oldUpcastedObjectAddr < oldObjectAddr + sizeof(P));

        // Compute the offset of the sub-object within the object.
        const std::uintptr_t offset = oldUpcastedObjectAddr - oldObjectAddr;

        void* newSubObject = reinterpret_cast<void*>(
            reinterpret_cast<std::uintptr_t>(newObject) + offset);

        return newSubObject;
    }

    /*----- member functions -----*/

    /// \brief Constructor.
    ///
    /// Initializes the use count to one.
    explicit PtrCntrlBlk(Vtbl const* vtbl) noexcept
        : m_vtbl(vtbl), m_useCount(1) {
        assert(vtbl);
        assert(vtbl->m_clonePointee);
        assert(vtbl->m_dispose);
    }

    /// \brief Destructor.
    ///
    /// Empty.
    ~PtrCntrlBlk() { assert(m_useCount == 0); }

    /// \brief Invoked to dispose of the owned object.
    ///
    /// Invoked when the use count reaches zero. Derived classes must
    /// implement the dispose() member function to properly release
    /// the owned object and the control block using any proper
    /// mechanism.
    void dispose() { m_vtbl->m_dispose(this); }

private:
    /*----- friendship -----*/

    /// Control who can actually modify the reference count
    /// \{
    template <class T>
    friend class PtrRep;
    friend class PtrCntrlBlkPrivate;
    /// \}

    /*----- member functions -----*/

    /// \brief Increment the use count
    ///
    /// The use count is incremented atomically.
    ///
    /// \return the value of the use count after the increment
    use_count_type incUseCount() noexcept { return ++m_useCount; }

    /// \brief Increment the use count by `n`
    ///
    /// The use count is incremented atomically.
    ///
    /// \return the value of the use count after the increment by `n`
    use_count_type multiIncUseCount(uint64_t n) noexcept {
        return m_useCount.fetch_add(n);
    }

    /// \brief Decrement the use count
    ///
    /// The use count is decremented atomically. The virtual member
    /// function dispose() is invoked if the use count reaches zero.
    ///
    /// \return the value of the use count after the decrement
    use_count_type decUseCount() noexcept {
        use_count_type remaining = --m_useCount;
        assert(m_useCount != -1);
        if (remaining == 0) dispose();
        return remaining;
    }

    /*----- data members -----*/

    /// The home-grown vtbl for this object.
    Vtbl const* const m_vtbl;

    /// The atomic use count.
    std::atomic<use_count_type> m_useCount;
};

//==============================================================================
// CLASS PtrCntrlBlkPtr
//==============================================================================

/// \brief Control block for Amino::Ptr with a default deleter
///
/// This control block disposes of the owned pointer using a 'delete p'
/// expression.
///
/// \tparam P the type of the owned object
template <class P>
class PtrCntrlBlkPtr : public PtrCntrlBlk {
public:
    // NOLINTNEXTLINE(modernize-unary-static-assert)
    static_assert(PointeeManager::is_copy_constructible<P>::value, "");

    /*----- member functions -----*/

    /// \brief Constructor
    ///
    /// Takes a snapshot of the pointer to the owned object. The owned object
    /// will be disposed using a 'delete p' expression, even if the
    /// Amino::Ptr is changed to point to a sub-object afterward.
    ///
    /// \param [in] p a pointer to the owned object
    // NOLINTNEXTLINE(google-explicit-constructor)
    PtrCntrlBlkPtr(P* p) noexcept : PtrCntrlBlk(&m_the_vtbl), m_pointee(p) {}

    /// \brief Clones the pointee and creates a Ptr with a control block of this
    /// class.
    ///
    /// This is used by the \ref clonePointee implementation of this class and
    /// the \ref PtrCntrlBlkPtrDel<P,D>::clonePointee.
    static PtrRepUntyped clone(
        P const* oldPointee, void const* oldUpcastedPointee) {
        auto* newPointee = PointeeManager::newClass<P>(*oldPointee);
        // NOLINTNEXTLINE(cppcoreguidelines-owning-memory)
        auto* newCntrlBlk        = new PtrCntrlBlkPtr<P>(newPointee);
        auto* newUpcastedPointee = PtrCntrlBlk::adjustUpcastedPointee(
            newPointee, oldPointee, oldUpcastedPointee);
        return PtrRepUntyped(newUpcastedPointee, newCntrlBlk);
    }

private:
    /*----- static member functions -----*/

    /// \brief Clone the stored object.
    static PtrRepUntyped clonePointee(
        PtrCntrlBlk const* self, void const* oldPointee) {
        auto realSelf = static_cast<PtrCntrlBlkPtr<P> const*>(self);
        return clone(realSelf->m_pointee, oldPointee);
    }

    /// \brief Dispose of the own object and control block.
    ///
    /// Invokes 'delete p' and deletes this control block.
    static void dispose(PtrCntrlBlk* self) {
        auto realSelf = static_cast<PtrCntrlBlkPtr<P>*>(self);

        PointeeManager::checkedDelete(realSelf->m_pointee);
        // NOLINTNEXTLINE(cppcoreguidelines-owning-memory)
        delete realSelf;
    }

    /*----- static data members -----*/

    /// The statically compiled vtbl for all objects of this class.
    static Vtbl const m_the_vtbl;

    /*----- data members -----*/

    /// A pointer to the owned object
    P* const m_pointee;
};

template <class P>
PtrCntrlBlk::Vtbl const PtrCntrlBlkPtr<P>::m_the_vtbl = {
    &PtrCntrlBlkPtr<P>::clonePointee, &PtrCntrlBlkPtr<P>::dispose};

//==============================================================================
// CLASS PtrCntrlBlkPtrDel
//==============================================================================

/// \brief Control block for Amino::Ptr with a custom deleter
///
/// This control block disposes of the owned pointer using a 'd(p)'
/// expression where \p d is a custom deleter.
///
/// \tparam P the type of the owned object
/// \tparam D the type of the deleter. Must be \p CopyConstructible.
template <class P, class D>
class PtrCntrlBlkPtrDel : public PtrCntrlBlk {
public:
    // NOLINTNEXTLINE(modernize-unary-static-assert)
    static_assert(PointeeManager::is_copy_constructible<P>::value, "");

    /*----- member functions -----*/

    /// \brief Constructor
    ///
    /// Takes a snapshot of the pointer to the owned object and the deleter \p
    /// d. The owned object will be disposed using a 'd(p)' expression, even if
    /// the Amino::Ptr is changed to point to a sub-object afterward.
    ///
    /// \param [in] p a pointer to the owned object
    /// \param [in] d the deleter that will be used to dispose of the owned
    /// object
    PtrCntrlBlkPtrDel(P* p, D d) noexcept
        : PtrCntrlBlk(&m_the_vtbl), m_pointee(p), m_deleter(d) {}

private:
    /*----- static member functions -----*/

    /// \brief Clone the stored object.
    static PtrRepUntyped clonePointee(
        PtrCntrlBlk const* self, void const* oldPointee) {
        // the cloned object gets a regular control block.
        auto const* realSelf = static_cast<PtrCntrlBlkPtrDel const*>(self);
        return PtrCntrlBlkPtr<P>::clone(realSelf->m_pointee, oldPointee);
    }

    /// \brief Dispose of the own object and control block.
    ///
    /// Invokes 'd(p)' and deletes this control block.
    static void dispose(PtrCntrlBlk* self) {
        auto realSelf = static_cast<PtrCntrlBlkPtrDel<P, D>*>(self);

        realSelf->m_deleter(realSelf->m_pointee);
        // NOLINTNEXTLINE(cppcoreguidelines-owning-memory)
        delete realSelf;
    }

private:
    /*----- static data members -----*/

    /// The statically compiled vtbl for all objects of this class.
    static Vtbl const m_the_vtbl;

    /*----- data members -----*/

    /// A pointer to the owned object
    P* const m_pointee;

    /// The deleter that will be used to dispose of the owned object
    D m_deleter;
};

template <class P, class D>
PtrCntrlBlk::Vtbl const PtrCntrlBlkPtrDel<P, D>::m_the_vtbl = {
    &PtrCntrlBlkPtrDel<P, D>::clonePointee, &PtrCntrlBlkPtrDel<P, D>::dispose};

//==============================================================================
// CLASS PtrRep
//==============================================================================

/// \brief Typed representation of Amino::Ptr pointers.
///
/// Wraps the extern "C" representation of Amino Ptr adding a layer of type
/// safety. It provides the basic block necessary to implement the
/// Amino::Ptr. One of its main duties is to correctly perform the cast
/// back-and-forth between the internally stored void* and T*.
///
/// \tparam T the element type
template <class T>
class PtrRep : private PtrRepUntyped {
public:
    /*----- member functions -----*/
    /// \brief Uninitializing default constructor
    /// \warning This constructor leaves the data members uninitialized. The
    ///          constructor body of the derived class must invoked init() to
    ///          initialized the data members.
    explicit PtrRep(Uninitialized) noexcept : PtrRepUntyped(kUninitialized) {}

    /// \brief Construct an empty pointer
    constexpr explicit PtrRep(std::nullptr_t) noexcept
        : PtrRepUntyped(nullptr, nullptr) {}

    /// \brief Initializing constructor
    ///
    /// Construct a PtrRep with the given value pointer \p and control block \p
    /// cblk.
    ///
    /// \param [in] p     the value of the stored pointer
    /// \param [in] cblk  the block controlling the life-scope of the owned
    /// object
    PtrRep(T const* p, PtrCntrlBlk* cblk) noexcept
        : PtrRepUntyped(
              static_cast<void*>(
                  const_cast<typename std::remove_cv<T>::type*>(p)),
              cblk) {}

    /// \brief Move constructor
    ///
    /// \param [in] rhs the pointer to be copied
    PtrRep(PtrRep&& rhs) noexcept
        : PtrRepUntyped(rhs.m_pointee, rhs.getCntrlBlk()) {
        rhs.m_pointee  = nullptr;
        rhs.m_cntrlBlk = nullptr;
    }

    /// \brief Assignment operator
    ///
    /// Assign the pointer \p rhs to *this. This is equivalent to
    /// `PtrRep(rhs).swap(*this)`.
    ///
    /// \param [in] rhs the source of the assignment
    /// \return `*this`
    PtrRep& operator=(PtrRep const& rhs) noexcept {
        if (m_pointee != rhs.m_pointee) {
            auto oldCntrlBlk = getCntrlBlk();

            m_pointee  = rhs.m_pointee;
            m_cntrlBlk = rhs.m_cntrlBlk;

            auto newCntrlBlk = getCntrlBlk();

            // Must do the incUseCount() before the decUseCount() as the
            // lifescope of the new pointee might transitively depend on the
            // life-scope of the old.
            if (newCntrlBlk != nullptr) newCntrlBlk->incUseCount();
            if (oldCntrlBlk != nullptr) oldCntrlBlk->decUseCount();
        }

        return *this;
    }

    /// \brief Move assignment operator
    ///
    /// Move assign the pointer \p rhs to *this.
    ///
    /// \param [in] rhs the source of the assignment
    /// \return `*this`
    PtrRep& operator=(PtrRep&& rhs) noexcept {
        if (this != &rhs) {
            auto oldCntrlBlk = getCntrlBlk();

            m_pointee  = rhs.m_pointee;
            m_cntrlBlk = rhs.m_cntrlBlk;

            rhs.m_pointee  = nullptr;
            rhs.m_cntrlBlk = nullptr;

            if (oldCntrlBlk != nullptr) oldCntrlBlk->decUseCount();
        }

        return *this;
    }

    /// \brief Initializes the pointer representation
    ///
    /// Initializes the PtrRep with the given value pointer \p and control
    /// block \p cblk.
    ///
    /// \warning This function assumes that the stored pointer and control
    ///          block are uninitialized. In particular, it won't free-up any
    ///          previously initialized control block.
    ///
    /// \param [in] p     the value of the stored pointer
    /// \param [in] cblk  the block controlling the life-scope of the owned
    /// object
    void init(T* p, PtrCntrlBlk* cblk) noexcept {
        m_pointee = static_cast<void*>(
            const_cast<typename std::remove_cv<T>::type*>(p));
        m_cntrlBlk = cblk;
    }

    /// \brief Initializes the pointer representation
    ///
    /// Initializes the PtrRep with the given value pointer \p and an
    /// allocated control block.
    ///
    /// \warning This function assumes that the stored pointer and control
    ///          block are uninitialized. In particular, it won't free-up any
    ///          previously initialized control block.
    ///
    /// \param [in] p   the value of the stored pointer
    ///
    template <class Y>
    void init_dispatch(Y* p) noexcept {
        // NOLINTNEXTLINE(cppcoreguidelines-owning-memory)
        init(p, new PtrCntrlBlkPtr<Y>(p));

        // Tell the static analyzer that m_cntrlBlk can't leak!
        Internal::escapeFromClangStaticAnalysis(m_cntrlBlk);
    }

    /// \brief Destructor
    ///
    /// Decrements the use count if non-empty; no-op if empty. The operation is
    /// atomic.
    ~PtrRep() noexcept {
        AMINO_INTERNAL_WARNING_PUSH
        // clang-format off
        AMINO_INTERNAL_WARNING_DISABLE_GCC(-Wmaybe-uninitialized)
        // clang-format on

        if (m_cntrlBlk != nullptr) getCntrlBlk()->decUseCount();

#ifndef NDEBUG
        // For easier debugging...
        m_pointee  = reinterpret_cast<void*>(0xDEADBEEFBEEFCAFE);
        m_cntrlBlk = reinterpret_cast<Amino::PtrInternal::PtrCntrlBlk*>(
            0xDEADCAFEBEEFBEEF);
#endif
        AMINO_INTERNAL_WARNING_POP
    }

    /// \brief Increments the use count
    ///
    /// The operation is atomic.
    void incUseCount() noexcept {
        if (m_cntrlBlk) getCntrlBlk()->incUseCount();
    }

    /// \brief Return the stored object
    ///
    /// \return the stored object
    T* getPointee() const noexcept { return reinterpret_cast<T*>(m_pointee); }

    /// \brief Return the control block
    ///
    /// \return the control block
    PtrCntrlBlk* getCntrlBlk() const noexcept {
        return PtrRepUntyped::getCntrlBlk();
    }

    /// \brief Swap the pointer representation
    ///
    /// Exchanges the content of the two pointers.
    ///
    /// \param [in] rhs the other pointer to be swapped
    void swap(PtrRep& rhs) noexcept {
        std::swap(m_pointee, rhs.m_pointee);
        std::swap(m_cntrlBlk, rhs.m_cntrlBlk);
    }
};

//==============================================================================
// TRAITS DECLARATIONS
//==============================================================================

template <typename T>
struct isPtr {
    static constexpr bool value =
        std::is_base_of<PtrInternal::PtrRepUntyped, T>::value;
};

template <typename, typename = void>
struct isTypeComplete : public std::false_type {};

template <typename... Ts>
struct make_void {
    using type = void;
};
template <typename... Ts>
using void_t = typename make_void<Ts...>::type;

template <typename T>
struct isTypeComplete<T, void_t<decltype(sizeof(T))>> : public std::true_type {
};

} // namespace PtrInternal

//==============================================================================
// CLASS PointeeManager
//==============================================================================

//------------------------------------------------------------------------------
//
template <typename T, typename... Args>
T* PointeeManager::newClass(Args&&... args) {
    // NOLINTNEXTLINE(cppcoreguidelines-owning-memory)
    return new T(std::forward<Args>(args)...);
}

//------------------------------------------------------------------------------
//
template <class T>
void PointeeManager::checkedDelete(T* obj) {
    static_assert(
        PtrInternal::isTypeComplete<T>::value,
        "Attempting to delete an incomplete type");

    // For a Amino::Ptr, it is not required that the destructor of
    // the owned object be virtual since the information necessary to
    // delete the owned object is captured when the smart pointer is
    // constructed. At that time, the information required to destruct
    // the owned is entirely known as long as a pointer to the object
    // concrete type is passed.
    AMINO_INTERNAL_WARNING_PUSH
    // clang-format off
    AMINO_INTERNAL_WARNING_DISABLE_CLANG(-Wdelete-non-virtual-dtor)
    AMINO_INTERNAL_WARNING_DISABLE_GCC(-Wdelete-non-virtual-dtor)
    // clang-format on
    // NOLINTNEXTLINE(cppcoreguidelines-owning-memory)
    delete obj;
    AMINO_INTERNAL_WARNING_POP
}

//------------------------------------------------------------------------------
//
template <typename T>
struct Internal::GetTypeCategory<Ptr<T>> {
    static constexpr auto value =
        PtrInternal::DefaultPtrTraits::is_defaultable<T>::value
            ? TypeCategory::eCtPtr
            : TypeCategory::eUninstantiable;
};

} // namespace Amino
/// \endcond

#endif

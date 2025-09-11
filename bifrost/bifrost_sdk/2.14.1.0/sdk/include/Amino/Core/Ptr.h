//-
// =============================================================================
// Copyright 2025 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file  Ptr.h
///
/// \brief Smart pointers used to allow custom user classes (opaque classes) to
/// be used within Amino graphs. They can also be used to implement persistent
/// copy-on-write data structures and types.
///
/// \see Amino::Ptr
/// \see Amino::MutablePtr

#ifndef AMINO_PTR_H
#define AMINO_PTR_H

#include "PtrFwd.h"

//==============================================================================
// EXTERNAL DECLARATIONS
//==============================================================================

#include "internal/PtrRep.h"

#include <functional>
#include <type_traits>

namespace Amino {

//==============================================================================
// Forward declarations
//==============================================================================

namespace Internal {
struct PtrCast;
} // namespace Internal

//==============================================================================
// Traits
//==============================================================================

/// \brief Traits about the to-be-pointee of an \ref Amino::Ptr<T> or \ref
/// Amino::MutablePtr<T> class.
///
/// This is used to check that a given type T can be wrapped in an \ref
/// Amino::Ptr or \ref Amino::MutablePtr. If not, an error will be emitted at
/// compile time.
struct PointeeTraits {
    /// \brief Whether a Ptr<T> or MutablePtr<T> can be instantiated.
    ///
    /// This is less strict than \ref is_compliant because it must be allowed to
    /// downcast (Ptr<Base>) or type erase (Ptr<void>) the pointee type.
    template <typename T>
    struct is_compliant_base
        : public std::integral_constant<
              bool,
              // The pointee must not be a pointer itself.
              (!std::is_pointer<T>::value &&

               // The pointee must not be a reference.
               !std::is_reference<T>::value &&

               // The type must not include "const" qualifiers.
               // By definition, Ptr<T> points to a const T.
               // By definition, MutablePtr<T> points to a non-const T.
               !std::is_const<T>::value &&

               // The type must not include "volatile" qualifiers.
               !std::is_volatile<T>::value &&

               // The type must not be an array (e.g. int[]).
               !std::is_array<T>::value)> {};

    /// \brief Whether the class of type T can be stored in an \ref
    /// Amino::Ptr<T> or an \ref Amino::MutablePtr<T>.
    template <typename T>
    struct is_compliant
        : public std::integral_constant<
              bool,
              (is_compliant_base<T>::value &&

               // Must be copy constructible to allow cloning the pointee.
               PointeeManager::is_copy_constructible<T>::value)> {};

    /// \brief Whether Ptr{\ref PtrDefaultFlag{}} or \ref
    /// Amino::makeDefaultPtr<T>() can be used for a pointee of type T.
    template <typename T>
    using is_defaultable = PtrInternal::DefaultPtrTraits::is_defaultable<T>;
};

//==============================================================================
// CLASS PtrDefaultFlag
//==============================================================================

/// \brief Flag that may be passed when creating a Ptr, to make it contain a
/// default value as its pointee.
///
/// This can be passed the \ref Ptr constructor to create a \ref Ptr to a
/// default value for its pointee. The \ref Ptr will therefore NOT be null when
/// constructed with this flag. For example:
///
/// \code{.cpp}
/// Amino::Ptr<MyClass> myClassPtr{Amino::PtrDefaultFlag{}};
/// // which is equivalent to:
/// Amino::Ptr<MyClass> myClassPtr{Amino::makeDefaultPtr<MyClass>()};
/// // Note that PtrDefaultFlag is convenient to avoid repetition of 'MyClass'
/// \endcode
///
/// \warning This can only be used on pointee types T that are "defaultable".
/// That is, the type T is either:
///  - a custom user class that has specified a default value
///    (using \ref AMINO_DECLARE_DEFAULT_CLASS and  \ref
///    AMINO_DEFINE_DEFAULT_CLASS (which is mandatory to use custom types in
///    Amino graphs)) or,
///  - a type that is default constructible and is allowed to flow in Amino
///    graph without providing the default value entry points) (for example
///    Amino::Array types).
struct PtrDefaultFlag {};

//==============================================================================
// CLASS Ptr
//==============================================================================

/// \brief  Smart pointers allowing custom user classes (opaque classes) to
/// be used within Amino graphs
///
/// \warning \ref Amino::Ptr is NOT replacements for standard smart pointers
/// (like std::shared_ptr). It is only meant to be used within Amino graphs.
/// Therefore, if a value never needs to flow directly into the graph, a
/// standard smart pointer (like std::shared_ptr) should be used instead.
///
/// This class is a smart pointer used to manage the life-scope of the pointee
/// objects and help implementing persistent data structures, respecting
/// value semantics.
///
/// In general, in Amino, a \ref Ptr pointer would be referring to objects of
/// following types:
///
///    - An Amino Class (custom user class (opaque)).
///    - An Amino Array
///
/// The \ref Ptr class stores a pointer to a dynamically allocated object. The
/// object is typically allocated using the C++ new operator. An optional
/// customizable deleter can be specified in case the object hasn't been
/// allocated with the C++ new operator.
///
/// \ref Ptr references are implemented using reference counting, and the
/// pointed object is automatically released when no remaining \ref Ptr is
/// referencing it.
///
/// Because the pointee of a \ref Ptr is always const, and the compiler checks
/// for constness, there is no possibility of cyclic references between objects.
///
/// Copying a \ref Ptr creates a new reference to the same object. This
/// operation is thread-safe. \ref Ptr can thus be safely passed to other
/// threads.
///
/// Accesses to the pointed object are not synchronized between threads. Other
/// means of protection must be used to insure the thread-safety of the
/// pointed object. This is unnecessary for immutable objects as these are
/// trivially thread-safe.
///
/// The pointed object of \ref Ptr is always const. This allows embedding of Ptr
/// in other const objects (structs, lists, arrays), giving a immutable overall
/// data structure as a result.
///
/// \warning In that respect, \ref Amino::Ptr is different than std::shared_ptr.
/// \ref Amino::Ptr since access to the pointee is always const, unlike
/// std::shared_ptr. This allows \ref Amino::Ptr to be safely used to implement
/// Persistent Data Structures. See \ref Amino::Ptr::toMutable() for details.
///
/// The \ref Ptr class meets the \p CopyConstructible, \p MoveConstructible, \p
/// CopyAssignable and \p MoveAssignable requirements of the C++ Standard
/// Library. Thus, \ref Ptr objects can be stored in standard library
/// containers. Comparison operators and a hash functor are supplied so that
/// \ref Ptr works with the standard library's associative containers.
///
/// \pre The dynamically allocated pointee class T must satisfy some criterion
/// to be allowed to be stored in a \ref Ptr. In particular, it must be copy
/// constructible, because this is required to allocate a copy, when calling
/// \ref Amino::Ptr::toMutable(). The complete list of requirements on the
/// pointee type T can be found in \ref Amino::PointeeTraits.
///
/// \warning The type T may not be the actual type of the dynamically
/// allocated object, since the Ptr could have been downcasted (Ptr<BaseClass>)
/// or type erased (Ptr<void>).
///
/// \note If a function returns an \ref Amino::Ptr then it
/// is up to calling code to keep it alive while the calling code accesses the
/// pointee.

/// \warning It is recommended to avoid type-erasure (Ptr<void>) as much a
/// possible. Static casting \ref Ptr from/to void to type can lead to very
/// subtle bugs, since potential "casters" must "agree" on the exact type T
/// to use when casting to void or casting to T. Otherwise, this could lead to
/// pointer misalignments (for example for classes with multiple inheritance),
/// which would in turn lead to undefined behavior.
///
/// \tparam T The type of objects referenced by the Ptr pointer.
template <class T>
class Ptr : private PtrInternal::PtrRep<T> {
private:
    // NOLINTNEXTLINE(modernize-unary-static-assert)
    static_assert(PointeeTraits::is_compliant_base<T>::value, "");

    /*----- types -----*/
    /// \brief Internal representation (and private implementations)
    using PtrRep = PtrInternal::PtrRep<T>;

    /// \brief Functor for enabling overloaded conversions.
    ///
    /// Meta-programming functor for selectively enabling some
    /// templated constructors and member functions only when the a \p
    /// Y* is implicitly convertible to a \p element_type*.
    ///
    /// \tparam Y The type of the pointed object to be converted to an
    /// \p element_type*.
    template <class Y>
    using if_convertible_from =
        typename std::enable_if<std::is_convertible<Y*, T*>::value>::type;

    /// \brief Functor for enabling overloaded conversions taking raw pointers
    ///
    /// The raw pointer must be compliant to be held in a Ptr and must be
    /// convertible to this Ptr's template type.
    template <class Y>
    using if_compliant_and_convertible_from = typename std::enable_if<
        std::is_convertible<Y*, T*>::value &&
        PointeeTraits::is_compliant<Y>::value>::type;

public:
    /*----- types -----*/

    /// \brief The type of objects referenced by the Ptr pointer.
    using element_type = T;

    /// A reference to a const element_type
    using element_const_reference_type =
        typename std::add_lvalue_reference<const element_type>::type;

    /// The integral type of the use count.
    using use_count_type = std::intptr_t;

    /*----- member functions -----*/

    /// \name Empty constructors

    /// \{
    /// \brief Construct an empty pointer
    ///
    /// \post `get() == nullptr`
    /// \post `use_count() == 0`
    constexpr Ptr() noexcept;
    // NOLINTNEXTLINE(google-explicit-constructor)
    constexpr Ptr(std::nullptr_t) noexcept;
    /// \}

    /// \brief Construct a Ptr with a default value pointee.
    /// \see PtrDefaultFlag
    explicit Ptr(PtrDefaultFlag);

    /// \name Constructors

    /// \{
    /// \brief Construct a pointer that owns the object pointed by \p p
    ///
    /// The object will be deleted using the expression
    /// `Amino::PointeeManager::checkedDelete(p)`. As such, \p must be of a
    /// complete type. The pointer \p p used for deletion is captured at
    /// construction time of the \ref Ptr.
    ///
    /// The constructor is only considered if a `Y*` can be implicitly
    /// converted to a `T*`.
    ///
    /// \post `get() == p`
    /// \post `use_count() == 1`
    ///
    /// \param [in] p a pointer to an object allocated via a C++ new expression
    /// or a null pointer.
    template <class Y, class = if_compliant_and_convertible_from<Y>>
    explicit Ptr(Y* p);

    /// \brief Construct a pointer that owns the object pointed by \p p
    ///
    /// The pointer deleter is set to \p d. The object will be destructed
    /// using the expression `d(p)`. The deleter is invoked in all cases
    /// even when the pointer is null. The pointer \p p used for deletion is
    /// captured at construction time of the \ref Ptr.
    ///
    /// The constructor is only considered if a `Y*` can be implicitly
    /// converted to a `T*`.
    ///
    /// \post `get() == p`
    /// \post `use_count() == 1`
    ///
    /// \param [in] p a pointer to an object to be owned by the pointer or a
    ///               null pointer.
    /// \param [in] d the deleter to invoke when the object is not longer
    ///               referenced by any Ptr.
    template <class Y, class D, class = if_compliant_and_convertible_from<Y>>
    Ptr(Y* p, D d);
    /// \}

    /// \name Templated null constructors

    /// \{
    /// \brief Construct a pointer to a null object with a specific deleter
    ///
    /// The pointer deleter is set to \p d. The null object will be destructed
    /// using the expression `d(nullptr)` when it is no longer referenced.
    ///
    /// \post `get() == nullptr`
    /// \post `use_count() == 1`
    ///
    /// \param [in] d the deleter to invoke when the object is not longer
    ///               referenced by any Ptr.
    template <class D>
    Ptr(std::nullptr_t, D d);
    /// \}

    /// \name Copy constructors

    /// \{
    /// \brief Copy constructor
    ///
    /// If \p rhs is empty, constructs an empty Ptr; otherwise, constructs a
    /// Ptr that shares ownership with \p rhs.
    ///
    /// \post `get() == rhs.get()`
    /// \post `use_count() == rhs.use_count()`
    ///
    /// \param [in] rhs the pointer to be copied
    Ptr(Ptr const& rhs) noexcept;

    /// \brief Conversion constructor
    ///
    /// If \p rhs is empty, constructs an empty Ptr; otherwise, constructs a Ptr
    /// that shares ownership with \p rhs. T
    ///
    /// The conversion constructor is only considered if a `Y*` can be
    /// implicitly converted to a `T*`.
    ///
    /// \post `get() == rhs.get()`
    /// \post `use_count() == rhs.use_count()`
    ///
    /// \param [in] rhs the pointer to be copied
    template <class Y, class = if_convertible_from<Y>>
    // NOLINTNEXTLINE(google-explicit-constructor)
    Ptr(Ptr<Y> const& rhs) noexcept;
    /// \}

    /// \name Move constructors

    /// \{
    /// \brief Move constructor
    ///
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    ///
    /// \param [in] rhs the pointer to be moved
    Ptr(Ptr&& rhs) noexcept;

    /// \brief Move conversion
    ///
    /// The conversion constructor is only considered if a `Y*` can be
    /// implicitly converted to a `T*`.
    ///
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    ///
    /// \param [in] rhs the pointer to be moved
    template <class Y, class = if_convertible_from<Y>>
    // NOLINTNEXTLINE(google-explicit-constructor)
    Ptr(Ptr<Y>&& rhs) noexcept;

    /// \brief Conversion constructor from a MutablePtr
    ///
    /// The conversion constructor is only considered if a `Y*` can be
    /// implicitly converted to a `T*`.
    ///
    /// \post `use_count() == 1` if \p rhs was not empty
    ///       `use_count() == 0` otherwise.`
    ///
    /// \param [in] rhs the MutablePtr to steal the pointee from.
    template <class Y, class = if_convertible_from<Y>>
    // NOLINTNEXTLINE(google-explicit-constructor)
    Ptr(MutablePtr<Y> rhs) noexcept;
    /// \}

    /// \name Destructor

    /// \{
    /// \brief Destructor
    ///
    /// If the pointer is empty, nothing occurs.
    ///
    /// If the pointer owns an object, the use_count of the pointers sharing
    /// ownership with the current pointer is decremented by one. If the
    /// use_count reaches zero, the expression
    /// `Amino::PointeeManager::checkedDelete(p)` or `d(p)` is invoked; where \p
    /// d is an optional deleter and \p p is the pointer specified when the
    /// first Ptr was constructed (i.e. the current value of the pointer is not
    /// used).
    ~Ptr();
    /// \}

    /// \name Assignment operators

    /// \{
    /// \brief Assignment operator
    ///
    /// Assign the pointer \p rhs to *this. Both pointers will point to the same
    /// object.
    ///
    /// \post `get() == rhs.get()`
    /// \post `use_count() == rhs.use_count()`
    ///
    /// \param [in] rhs the source of the assignment
    /// \return `*this`
    Ptr& operator=(Ptr const& rhs) noexcept;

    /// \brief Assignment conversion
    ///
    /// Assign the pointer \p rhs to *this. Both pointers will point to the same
    /// object, therefore increasing the use count by one.
    ///
    /// The assignment conversion is only considered if a `Y*` can be
    /// implicitly converted to a `T*`.
    ///
    /// \param [in] rhs the source of the assignment
    /// \return `*this`
    template <class Y, class = if_convertible_from<Y>>
    Ptr& operator=(Ptr<Y> const& rhs) noexcept;
    /// \}

    /// \name Move assignment operators

    /// \{
    /// \brief Move assignment operator
    ///
    /// Move assign the pointer \p rhs to *this.
    ///
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    ///
    /// \param [in] rhs the source of the assignment
    /// \return `*this`
    Ptr& operator=(Ptr&& rhs) noexcept;

    /// \brief Move assignment conversion
    ///
    /// Assign the pointer \p rhs to *this.
    ///
    /// The assignment conversion is only considered if a `Y*` can be
    /// implicitly converted to a `T*`.
    ///
    /// \post `*this` contains the old value of \p rhs
    /// \post \p rhs is empty
    ///
    /// \param [in] rhs the source of the assignment
    /// \return `*this`
    template <class Y, class = if_convertible_from<Y>>
    Ptr& operator=(Ptr<Y>&& rhs) noexcept;

    /// \brief Move assignment conversion from a MutablePtr
    ///
    /// The assignment conversion is only considered if a `Y*` can be
    /// implicitly converted to a `T*`.
    ///
    /// \post `use_count() == 1` if \p rhs was not empty
    ///       `use_count() == 0` otherwise.`
    ///
    /// \param [in] rhs the \ref MutablePtr to steal the pointee from.
    /// \return `*this`
    template <class Y, class = if_convertible_from<Y>>
    Ptr& operator=(MutablePtr<Y> rhs) noexcept;
    /// \}

    /// \name Modifiers
    /// \{

    /// \brief Swap two pointers
    ///
    /// Exchanges the contents of the two \ref Ptr.
    ///
    /// \param [in] rhs the pointer to swap with
    void swap(Ptr& rhs) noexcept;

    /// \brief Reset the pointer to an empty pointer
    ///
    /// This is equivalent to `*this = Ptr()`.
    ///
    /// \post `get() == nullptr`
    /// \post `use_count() == 0`
    void reset() noexcept;

    /// \brief Reset the content of the \ref Ptr to now manage the given pointer
    ///
    /// This is equivalent to `*this = Ptr(p)`.
    ///
    /// The member function is only considered if a `Y*` can be implicitly
    /// converted to a `T*`.
    ///
    /// \post `get() == p`
    /// \post `use_count() == 1`
    ///
    /// \param [in] p a pointer to an object to be owned by the pointer or a
    ///               null pointer.
    template <class Y, class = if_compliant_and_convertible_from<Y>>
    void reset(Y* p);

    /// \brief Reset the content of the \ref Ptr to now manage the given pointer
    ///
    /// This is equivalent to `*this = Ptr(p,d)`.
    ///
    /// The member function is only considered if a `Y*` can be implicitly
    /// converted to a `T*`.
    ///
    /// \post `get() == p`
    /// \post `use_count() == 1`
    ///
    /// \param [in] p a pointer to an object to be owned by the pointer or a
    ///               null pointer.
    /// \param [in] d the deleter to invoke when the object is not longer
    ///               referenced by any Ptr.
    template <class Y, class D, class = if_compliant_and_convertible_from<Y>>
    void reset(Y* p, D d);

    /// \brief Conversion to MutablePtr
    ///
    /// This member function allows one to convert a `Ptr<X>` to a
    /// `MutablePtr<X>`. The referenced object is cloned if necessary.
    ///
    /// This member function returns an empty MutablePtr if the \p *this pointer
    /// is empty.
    ///
    /// If the pointee object is not uniquely owned, a copy of the object
    /// is made and a MutablePtr to the mutable copied object is returned. The
    /// copy constructor of the dynamically allocated object that was captured
    /// upon creating the Ptr managing that object is used to make a copy of the
    /// object.
    ///
    /// If the pointee object is uniquely owned, the ownership of the pointee is
    /// simply transferred to the returned MutablePtr and the pointee object
    /// will not be copied.
    ///
    /// Regardless if the pointee is uniquely owned or not, the \p *this
    /// pointer will be reset after the call to \ref toMutable().
    ///
    /// \post `get() == nullptr`
    /// \post `use_count() == 0`
    ///
    /// \return a \ref MutablePtr to the uniquely owned object.
    MutablePtr<element_type> toMutable() noexcept;
    /// \}

    /// \name Special modifier
    /// \{
    /// \brief Short-hand to allow modifying the pointee held by this Ptr when
    /// its ownership is known to be unique (use_count() == 1).
    ///
    /// This can be useful in some scenario, but in general it is recommended to
    /// use a guard (see \ref Amino::PtrGuard and \ref Amino::createPtrGuard)
    /// to mutate the pointee.
    ///
    /// \param func A functor that takes a non-const pointee.
    ///
    /// \pre  unique() == true
    /// \post unique() == true
    ///
    /// \code{.cpp}
    /// Amino::Ptr<T> ptr = createMyPtr();
    ///
    /// // We know it's unique because it was just created.
    /// assert(ptr.unique());
    ///
    /// // Therefore it's safe to mutate.
    /// ptr.mutate([](T* ptee) {
    ///     ptee.modify();
    /// });
    /// \endcode
    template <typename Func>
    void mutate(Func&& func);
    /// \}

    /// \name Accessors

    /// \{
    /// \brief Indirection
    ///
    /// \pre    the pointer must not be null or empty
    /// \return the reference to the pointed object
    element_const_reference_type operator*() const noexcept;

    /// \brief Indirection
    ///
    /// \pre    the pointer must not be null
    /// \return the pointer to the pointed object
    element_type const* operator->() const noexcept;

    /// \brief Accessor
    ///
    /// \return the pointer to the pointed object
    element_type const* get() const noexcept;

    /// \brief Returns whether the object is uniquely owned by the pointer
    ///
    /// \return `use_count() == 1`
    bool unique() const noexcept;

    /// \brief Returns the use count of the pointed object
    ///
    /// \warning Use only for debugging and testing purposes, not for
    ///          production code. Consider using unique() instead.
    ///
    /// In a multi-threaded environment, use_count() will return you an
    /// instantaneous snapshot of its value. It's value might have already
    /// changed as soon as the function returns. The only reliable return
    /// value is the value "1" which implies that the only remaining reference
    /// is own the current thread (assuming that the Ptr object itself is
    /// local to the current thread).
    ///
    /// \return the number of Ptr referencing the pointed object
    use_count_type use_count() const noexcept;

    /// \brief Returns whether the pointer is non-null
    ///
    /// \return `get() != nullptr`
    explicit operator bool() const noexcept;

    /// \brief Owner-based ordering of Ptr.
    ///
    /// Compare two pointers and return whether one comes before the other one
    /// in some unspecified owner-based strict weak ordering. The order is
    /// such that two smart pointers compare equivalent only if they are both
    /// empty or if they share ownership, even if the values of the pointers
    /// obtained by get() are different (e.g. because they point at different
    /// sub-objects within the same object).
    ///
    /// \return true if \p *this comes before \p rhs in a the owner-based
    /// ordering; false otherwise.
    template <class Y>
    bool owner_before(Ptr<Y> const& rhs) const noexcept;
    /// \}

protected:
    /*----- member functions -----*/

    /// \name Constructors

    /// \{
    /// \cond AMINO_INTERNAL_DOCS
    /// \brief Construct a pointer that owns the object pointed by \p p
    ///
    /// The life-object of the object is managed by the specified control
    /// block. This constructor conditionally increments the reference count
    /// stored in the control block passed as a parameter. It is up-to to the
    /// caller of this private constructor to determine if a new reference is
    /// being created or if an existing one is being transferred.
    ///
    /// This construct is used by the implementation of toMutable.
    ///
    /// \post `get() == p`
    ///
    /// \param [in] p             a pointer to an object
    /// \param [in] cntrlBlk      the control block that controls th
    ///                           life-scope of the stored object
    /// \param [in] doIncUseCount should the reference count be incremented
    ///                           because a new reference is being created
    Ptr(T* p, PtrInternal::PtrCntrlBlk* cntrlBlk, bool doIncUseCount);
    /// \endcond
    /// \}

    using PtrRep::getPointee;

private:
    /// \brief Friendship to allow conversion between pointers of
    /// different types.
    template <class Y>
    friend class Ptr;

    /// \brief Friendship to allow access to getPointee, getCtrlBlck, and init.
    /// Used when the guard is created with the \ref Amino::PtrGuardUniqueFlag.
    template <class Y>
    friend class PtrGuard;

    /// \brief Friendship to allow access to getPointee, getCtrlBlck, init and
    /// protected constructor, to allow static/dynamic Ptr casts.
    friend struct Internal::PtrCast;
};

/// \brief Deduction guide for \ref Ptr.
template <typename T>
Ptr(MutablePtr<T>) -> Ptr<T>;

//==============================================================================
// CLASS MutablePtr
//==============================================================================

/// \brief Transient version of Amino::Ptr<T> which allows mutable access to the
/// pointee.
///
/// \warning \ref Amino::MutablePtr is NOT replacements for standard smart
/// pointers (like std::unique_ptr). It is only meant to be used within Amino
/// graphs. Therefore, if a value never needs to flow directly into the graph, a
/// standard smart pointer (like std::unique_tr) should be used instead.
///
/// This class is similar to a std::unique_ptr<T> in the sense that it has
/// unique ownership over the pointee. But it's different than
/// std::unique_ptr<T> because it still has a control block. It is meant to
/// be used as a TRANSIENT type. It is not meant to be stored in a class or
/// a struct. It is meant to be short-lived to allow mutation on the pointee,
/// but then giving ownership back to a Ptr. (The control block is kept to
/// avoid its unnecessary and inefficient deallocation/reallocation and to
/// ensure that information captured before type-erasure is preserved).
///
/// \code{.cpp}
/// Amino::Ptr<MyClass> ptr = getMyClass();
///
/// // Can't mutate the pointee from the Ptr.
/// // I.e. The following code would not compile:
/// // ptr->modifyYourself();
///
/// // Must instead get a mutable version of it.
/// Amino::MutablePtr<MyClass> mutablePtr = ptr.toMutable();
///
/// // The pointee will have been cloned if necessary, that is if it's
/// // `use_count() > 1`. This is why it it now safe to mutate it without
/// // side effects on other referents.
/// mutablePtr->modifyYourself();
///
/// // Calling toMutable() clears the Ptr, effectively transferring ownership
/// // of the pointee to the MutablePtr.
/// assert(!ptr);
///
/// // Assign back to the Ptr once we're done mutating it.
/// ptr = std::move(mutablePtr);
///
/// // Or equivalently:
/// // ptr = mutablePtr.toImmutable();
///
/// assert(ptr);
/// assert(ptr.unique());
/// \endcode
///
/// Equivalently, an \ref Amino::PtrGuard<T> can be used for more convenience
/// and safety.
///
/// Similarly to std::unique_ptr, \ref MutablePtr are not copy constructible nor
/// copy assignable. They are default constructible, move constructible and move
/// assignable.
///
/// \tparam T The type of objects referenced by the \ref MutablePtr pointer.
template <typename T>
class MutablePtr : private Ptr<T> {
private:
    // NOLINTNEXTLINE(modernize-unary-static-assert)
    static_assert(PointeeTraits::is_compliant_base<T>::value, "");

    /*----- types -----*/

    /// \brief Private parent class alias.
    using Base = Ptr<T>;

    /// \copydoc Ptr<T>::if_convertible_from
    template <class Y>
    using if_convertible_from =
        typename std::enable_if<std::is_convertible<Y*, T*>::value>::type;

public:
    /*----- types -----*/

    /// \copydoc Ptr<T>::element_type
    using element_type = typename Base::element_type;

    /*----- member functions -----*/

    /// \name Empty constructors

    /// \{
    /// \brief Construct an empty MutablePtr
    ///
    /// \post `get() == nullptr`
    constexpr MutablePtr() noexcept = default;
    // NOLINTNEXTLINE(google-explicit-constructor)
    constexpr MutablePtr(std::nullptr_t) noexcept;
    /// \}

    /// \brief Construct a mutable pointer that owns the object pointed by \p p
    // NOLINTNEXTLINE(google-explicit-constructor)
    MutablePtr(T* p);

    /// \brief Move constructor.
    MutablePtr(MutablePtr&&) noexcept = default;

    /// \brief MutablePtr are not copy constructible.
    MutablePtr(MutablePtr const&) noexcept = delete;

    /// \brief Move conversion construction from a MutablePtr of a compatible
    /// type Y.
    template <class Y, class = if_convertible_from<Y>>
    // NOLINTNEXTLINE(google-explicit-constructor)
    MutablePtr(MutablePtr<Y> rhs) noexcept;

    /// \brief Destructor.
    ~MutablePtr();

    /// \brief Move assignment.
    MutablePtr& operator=(MutablePtr&&) noexcept = default;

    /// \brief MutablePtr are not copy assignable.
    MutablePtr& operator=(MutablePtr const&) noexcept = delete;

    /// \brief Move conversion assignment from a MutablePtr of a compatible
    /// type Y.
    template <class Y, class = if_convertible_from<Y>>
    MutablePtr& operator=(MutablePtr<Y> rhs) noexcept;

    /// \name Accessors
    /// \{
    /// \copydoc Ptr<T>::operator*()
    // clang-format off
    T const& operator*() const noexcept { assert(get()); return *get(); }
    T&       operator*() noexcept { assert(get()); return *get(); }

    /// \copydoc Ptr<T>::operator->()
    T const* operator->() const noexcept { assert(get()); return get(); }
    T*       operator->() noexcept { assert(get()); return get(); }
    // clang-format on

    /// \copydoc Ptr<T>::get()
    T const* get() const noexcept { return Base::get(); }
    T*       get() noexcept { return Base::getPointee(); }
    /// \}

    /// \brief Returns whether the pointer is non-null
    ///
    /// \return `get() != 0`
    explicit operator bool() const { return Base::operator bool(); }

    /// \copydoc Ptr<T>::reset()
    void reset() { Base::reset(); }

    /// \copydoc Ptr<T>::swap()
    void swap(MutablePtr& rhs) noexcept;

    /// \brief Conversion to a Ptr (immutable)
    ///
    /// This member function allows one to convert a `MutablePtr<X>` to a
    /// `Ptr<X>`. This effectively only transfer ownership of the pointee to
    /// the Ptr. No copy of the pointee is made.
    ///
    /// \note This function can be useful to be explicit about the conversion,
    /// but it is effectively equivalent to creating a Ptr with a MutablePtr
    /// rvalue. In other words:
    ///
    /// \code{.cpp}
    /// Amino::MutablePtr<T> mutablePtr = getMyMutablePtr();
    ///
    /// // The following code:
    /// Amino::Ptr<T> ptr = mutablePtr.toImmutable();
    ///
    /// // Is equivalent to:
    /// Amino::Ptr<T> ptr = std::move(mutablePtr);
    /// \endcode
    ///
    /// \post `get() == nullptr`
    ///
    /// \return a Ptr to the object
    Ptr<T> toImmutable() noexcept;

private:
    /// \brief Construct a MutablePtr passing both the pointee and the
    /// control block.
    ///
    /// Only used by Ptr<T>::toMutable().
    MutablePtr(T* p, PtrInternal::PtrCntrlBlk* cntrlBlk)
        : Base(p, cntrlBlk, /*doIncUseCount=*/false) {
        assert(Base::unique());
    }

#ifndef NDEBUG
    /// \brief Helper to assert MutablePtr's invariants.
    bool unique_or_null() const { return !*this || Base::unique(); }
#endif

    /// \brief Friendship to allow Ptr to call private constructor passing the
    /// control block.
    template <typename Y>
    friend class Ptr;

    template <typename Y>
    friend class MutablePtr;

    template <typename Y>
    friend class PtrGuard;
};

//==============================================================================
// CLASS PtrGuardUniqueFlag
//==============================================================================

/// \brief Flag that may be passed when creating a PtrGuard.
///
/// This flag informs the PtrGuard that the \ref Ptr for which the guard is
/// created is known to be uniquely owned at compile time (i.e.
/// `ptr.unique() == true`). This can be useful to provide the functionality of
/// the \ref PtrGuard without paying the cost of checking uniqueness, when it is
/// known to be unique in a specific usage scenario. It will also assert if
/// the ownership is not unique, rather than "silently" making a copy of the
/// pointed object.
struct PtrGuardUniqueFlag {};

//==============================================================================
// CLASS PtrGuard
//==============================================================================

/// \brief Helper guard to allow mutation on a pointee for the lifescope of
/// the \ref PtrGuard<T> but then reassigning to the source Ptr upon its
/// destruction.
///
/// This effectively calls Amino::Ptr<T>::toMutable() upon construction and
/// Amino::MutablePtr<T>::toImmutable() upon destruction. It can be more
/// convenient and safer than transferring ownership manually since reassignment
/// in the original Ptr is guaranteed and may therefore avoid programmatic
/// errors (for example forgetting to assign back on an early return).
///
/// \code{.cpp}
/// {
///     Amino::PtrGuard<MyClass> guard{this->m_ptr};
///
///     // The m_ptr member ownership was transferred to the guard.
///     assert(!this->m_ptr);
///
///     // It's safe to mutate the pointee without introducing side effects.
///     guard->modifyYourself();
///
///     // Ok to do early return. The member "this->m_ptr" will be assigned
///     // back to contain the mutated pointee upon the PtrGuard's destruction.
///     if (someCondition) return;
///
///     // Still safe to mutate as long as the guard lives.
///     guard->modifySomethingElse();
/// }
/// // The m_ptr member was restored to contain the mutated pointee upon the
/// // PtrGuard's destruction.
/// assert(this->m_ptr);
/// assert(this->m_ptr.unique());
/// \endcode
template <typename T>
class PtrGuard {
private:
    /*----- types -----*/

    /// \copydoc Ptr<T>::if_convertible_from
    template <typename Y>
    using if_convertible_from =
        typename std::enable_if<std::is_convertible<Y*, T*>::value>::type;

public:
    /// \brief Constructor.
    ///
    /// \warning The PtrGuard is holding a reference to the source \p src Ptr.
    /// This pointer must therefore live at least as long as the PtrGuard lives.
    explicit PtrGuard(Ptr<T>& src);
    /// \brief Constructor for the guard when the pointer is
    ///  known to be uniquely owned at compile time \see PtrGuardUniqueFlag.
    explicit PtrGuard(Ptr<T>& src, PtrGuardUniqueFlag);

    /// \brief Conversion constructor.
    ///
    /// \warning The PtrGuard is holding a reference to the source \p src Ptr.
    /// This pointer must therefore live at least as long as the PtrGuard lives.
    template <class Y, class = if_convertible_from<Y>>
    explicit PtrGuard(Ptr<Y>& src);

    /// \brief Move constructor.
    ///
    /// \warning This should not be used typically, but is necessary for
    /// implementing createPtrGuard(), even if the compiler will elide the call
    /// (RVO - Return Value Optimization).
    PtrGuard(PtrGuard&&) noexcept = default;

    /// \brief \ref PtrGuard are not copy constructible.
    PtrGuard(PtrGuard const&) noexcept = delete;

    /// \brief \ref PtrGuard are not move assignable.
    ///
    /// \note They could be, if we judge there are valid uses for it.
    PtrGuard& operator=(PtrGuard&&) noexcept = delete;

    /// \brief \ref PtrGuard are not copy assignable.
    PtrGuard& operator=(PtrGuard const&) noexcept = delete;

    /// \brief Destructor.
    ///
    /// Restore the orinal source pointer reference to contain the mutated
    /// pointee.
    ~PtrGuard();

    /// \brief Returns a reference to the uniquely owned object.
    T& operator*() { return *m_ptr; }

    /// \brief Returns a pointer to the uniquely owned object.
    T* operator->() { return m_ptr.operator->(); }

    /// \brief Returns a const reference to the uniquely owned object.
    const T& operator*() const { return *m_ptr; }

    /// \brief Returns a const pointer to the uniquely owned object.
    const T* operator->() const { return m_ptr.operator->(); }

private:
    /// \brief The source pointer reference that is mutated.
    Ptr<T>* m_src = nullptr;

    /// \brief The temporary MutablePtr use to access the pointee to mutate.
    MutablePtr<T> m_ptr;
};

/// \brief Deduction guide for \ref PtrGuard.
/// \{
template <typename T>
PtrGuard(Ptr<T>&) -> PtrGuard<T>;
template <typename T>
PtrGuard(Ptr<T>&, PtrGuardUniqueFlag) -> PtrGuard<T>;
/// \}

//==============================================================================
// CLASS Ptr
//==============================================================================

//------------------------------------------------------------------------------
//
template <class T>
inline constexpr Ptr<T>::Ptr() noexcept : PtrRep(nullptr) {}

//------------------------------------------------------------------------------
//
template <class T>
inline constexpr Ptr<T>::Ptr(std::nullptr_t) noexcept : PtrRep(nullptr) {}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class>
inline Ptr<T>::Ptr(Y* p) : PtrRep(PtrInternal::kUninitialized) {
    // The control block must dispose of the pointer using its
    // original type, i.e Y, not T!!!
    using NonConstY = typename std::remove_cv<Y>::type;
    auto nonConstP  = const_cast<NonConstY*>(p);
    this->template init_dispatch<NonConstY>(nonConstP);

    // FIXME: In theory, we have to delete "p" if the previous allocation fails.
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class D, class>
inline Ptr<T>::Ptr(Y* p, D d) : PtrRep(PtrInternal::kUninitialized) {
    // The control block must dispose of the pointer using its
    // original type, i.e Y, not T!!!
    this->init(p, new PtrInternal::PtrCntrlBlkPtrDel<Y, D>(p, d));

    // FIXME: In theory, we have to delete "p" if the previous allocation fails.
}

//------------------------------------------------------------------------------
//
template <class T>
template <class D>
inline Ptr<T>::Ptr(std::nullptr_t, D d) : PtrRep(PtrInternal::kUninitialized) {
    this->init(nullptr, new PtrInternal::PtrCntrlBlkPtrDel<T, D>(nullptr, d));

    // FIXME: In theory, we have to delete "p" if the previous allocation fails.
}

//------------------------------------------------------------------------------
//
/// \cond AMINO_INTERNAL_DOCS
template <class T>
inline Ptr<T>::Ptr(T* p, PtrInternal::PtrCntrlBlk* cntrlBlk, bool doIncUseCount)
    : PtrRep(p, cntrlBlk) {
    if (doIncUseCount) this->incUseCount();
}
/// \endcond

//------------------------------------------------------------------------------
//
template <class T>
inline Ptr<T>::Ptr(Ptr const& rhs) noexcept
    : PtrRep(rhs.getPointee(), rhs.getCntrlBlk()) {
    this->incUseCount();
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class>
inline Ptr<T>::Ptr(Ptr<Y> const& rhs) noexcept
    : PtrRep(rhs.getPointee(), rhs.getCntrlBlk()) {
    this->incUseCount();
}

//------------------------------------------------------------------------------
//
template <class T>
inline Ptr<T>::Ptr(Ptr&& rhs) noexcept
    : PtrRep(rhs.getPointee(), rhs.getCntrlBlk()) {
    rhs.init(nullptr, nullptr);
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class>
inline Ptr<T>::Ptr(Ptr<Y>&& rhs) noexcept
    : PtrRep(rhs.getPointee(), rhs.getCntrlBlk()) {
    rhs.init(nullptr, nullptr);
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class>
inline Ptr<T>::Ptr(MutablePtr<Y> rhs) noexcept
    : PtrRep(rhs.getPointee(), rhs.getCntrlBlk()) {
    rhs.init(nullptr, nullptr);
    assert(!rhs.getPointee() || unique());
}

//------------------------------------------------------------------------------
//
template <class T>
inline Ptr<T>::~Ptr() = default;

//------------------------------------------------------------------------------
//
template <class T>
inline Ptr<T>& Ptr<T>::operator=(Ptr const& rhs) noexcept {
    this->PtrRep::operator=(rhs);
    return *this;
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class>
inline Ptr<T>& Ptr<T>::operator=(Ptr<Y> const& rhs) noexcept {
    this->PtrRep::operator=(Ptr(rhs));
    return *this;
}

//------------------------------------------------------------------------------
//
template <class T>
inline Ptr<T>& Ptr<T>::operator=(Ptr&& rhs) noexcept {
    this->PtrRep::operator=(std::move(rhs));
    return *this;
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class>
inline Ptr<T>& Ptr<T>::operator=(Ptr<Y>&& rhs) noexcept {
    this->PtrRep::operator=(Ptr(std::move(rhs)));
    return *this;
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class>
inline Ptr<T>& Ptr<T>::operator=(MutablePtr<Y> rhs) noexcept {
    this->PtrRep::operator=(Ptr<T>(std::move(rhs)));
    return *this;
}

//------------------------------------------------------------------------------
//
template <class T>
inline void Ptr<T>::swap(Ptr& rhs) noexcept {
    PtrRep::swap(rhs);
}

//------------------------------------------------------------------------------
//
template <class T>
inline void Ptr<T>::reset() noexcept {
    this->operator=(Ptr());
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class>
inline void Ptr<T>::reset(Y* p) {
    this->operator=(Ptr(p));
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y, class D, class>
inline void Ptr<T>::reset(Y* p, D d) {
    this->operator=(Ptr(p, d));
}

//------------------------------------------------------------------------------
//
template <class T>
inline MutablePtr<typename Ptr<T>::element_type> Ptr<T>::toMutable() noexcept {
    auto p = const_cast<element_type*>(this->getPointee());
    if (!p) {
        return MutablePtr<element_type>();
    } else {
        // Move the pointer...
        auto cntrl = this->getCntrlBlk();
        if (unique()) {
            // Simply move-const-cast the pointer...
            this->init(nullptr, nullptr);
            return MutablePtr<element_type>(p, cntrl);
        } else {
            // Non-unique owner, take a copy using the clone operation captured
            // at type erasure time!
            auto cloned = cntrl->clonePointee(p);
            reset();
            return MutablePtr<element_type>(
                static_cast<element_type*>(cloned.m_pointee),
                cloned.getCntrlBlk());
        }
    }
}

//------------------------------------------------------------------------------
//
template <class T>
template <typename Func>
void Ptr<T>::mutate(Func&& func) {
    assert(unique());

    Ptr<T> o = std::move(*this);

    auto ptee =
        o.unique() ? const_cast<element_type*>(o.getPointee()) : nullptr;
    assert(ptee);
    func(ptee);

    *this = std::move(o);
    assert(unique());
}

//------------------------------------------------------------------------------
//
template <class T>
inline typename Ptr<T>::element_const_reference_type Ptr<T>::operator*()
    const noexcept {
    assert(this->getPointee());
    return *this->getPointee();
}

//------------------------------------------------------------------------------
//
template <class T>
inline typename Ptr<T>::element_type const* Ptr<T>::operator->()
    const noexcept {
    assert(this->getPointee());
    return this->getPointee();
}

//------------------------------------------------------------------------------
//
template <class T>
inline typename Ptr<T>::element_type const* Ptr<T>::get() const noexcept {
    return this->getPointee();
}

//------------------------------------------------------------------------------
//
template <class T>
inline typename Ptr<T>::use_count_type Ptr<T>::use_count() const noexcept {
    auto cblk = this->getCntrlBlk();
    return cblk ? cblk->use_count() : 0;
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool Ptr<T>::unique() const noexcept {
    return use_count() == 1;
}

//------------------------------------------------------------------------------
//
template <class T>
inline Ptr<T>::operator bool() const noexcept {
    return this->getPointee() != nullptr;
}

//------------------------------------------------------------------------------
//
template <class T>
template <class Y>
inline bool Ptr<T>::owner_before(Ptr<Y> const& rhs) const noexcept {
    return (this->getCntrlBlk() < rhs.getCntrlBlk());
}

//==============================================================================
// CLASS MutablePtr
//==============================================================================

//------------------------------------------------------------------------------
//
template <typename T>
inline constexpr MutablePtr<T>::MutablePtr(std::nullptr_t) noexcept
    : Base(nullptr) {}

//------------------------------------------------------------------------------
//
template <typename T>
inline MutablePtr<T>::MutablePtr(T* p) : Base(p) {
    assert(unique_or_null());
}

//------------------------------------------------------------------------------
//
template <typename T>
template <class Y, class>
inline MutablePtr<T>::MutablePtr(MutablePtr<Y> rhs) noexcept
    : Base(std::move(rhs)) {
    assert(unique_or_null());
}

//------------------------------------------------------------------------------
//
template <typename T>
inline MutablePtr<T>::~MutablePtr() {
    assert(unique_or_null());
}

//------------------------------------------------------------------------------
//
template <typename T>
template <class Y, class>
inline MutablePtr<T>& MutablePtr<T>::operator=(MutablePtr<Y> rhs) noexcept {
    Base::operator=(std::move(rhs));
    assert(unique_or_null());
    return *this;
}

//------------------------------------------------------------------------------
//
template <typename T>
void MutablePtr<T>::swap(MutablePtr& rhs) noexcept {
    Base::swap(rhs);
}

//------------------------------------------------------------------------------
//
template <typename T>
Amino::Ptr<T> MutablePtr<T>::toImmutable() noexcept {
    Amino::Ptr<T> o;
    o.swap(*this);
    return o;
}

//==============================================================================
// CLASS PtrGuard
//==============================================================================

template <typename T>
inline PtrGuard<T>::PtrGuard(Ptr<T>& src)
    : m_src(&src), m_ptr(src.toMutable()) {
    assert(!*m_src);
}
template <typename T>
inline PtrGuard<T>::PtrGuard(Ptr<T>& src, PtrGuardUniqueFlag)
    : m_src(&src), m_ptr(src.getPointee(), src.getCntrlBlk()) {
    m_src->init(nullptr, nullptr);
    assert(!*m_src);
    assert(m_ptr.unique_or_null());
}
template <typename T>
template <class Y, class>
inline PtrGuard<T>::PtrGuard(Ptr<Y>& src)
    : m_src(&reinterpret_cast<Ptr<T>&>(src)), m_ptr(src.toMutable()) {
    assert(!*m_src);
}
template <typename T>
inline PtrGuard<T>::~PtrGuard() {
    if (!m_ptr) return;
    assert(!*m_src);
    *m_src = m_ptr.toImmutable();
}

//==============================================================================
// GLOBAL FUNCTIONS CLASS Amino::Ptr
//==============================================================================

/// \name Equality comparison

/// \{

/// \brief Return true if pointers are equal
///
/// Returns true if the stored pointers of both arguments are pointing to the
/// same object under implicit conversion rules.
///
/// \return `x.get() == y.get()`

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator==(Ptr<T> const& x, Ptr<U> const& y) noexcept {
    return x.get() == y.get();
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator==(const Ptr<T>& x, std::nullptr_t) noexcept {
    return !x;
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator==(std::nullptr_t, const Ptr<T>& y) noexcept {
    return !y;
}

/// \brief Return true if pointers are not equal
///
/// Returns true if the stored pointers of both arguments are not pointing to
/// the same object under implicit conversion rules.
///
/// \return `x.get() != y.get()`

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator!=(Ptr<T> const& x, Ptr<U> const& y) noexcept {
    return !(x == y);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator!=(const Ptr<T>& x, std::nullptr_t) noexcept {
    return static_cast<bool>(x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator!=(std::nullptr_t, const Ptr<T>& y) noexcept {
    return static_cast<bool>(y);
}
/// \}

/// \name Ordering comparison

/// \{

/// \brief Compares the pointer values
///
/// Returns true if the stored pointer of \p x is less than the stored pointer
/// of \p y under implicit conversion rules.
///
/// \return `x.get() < y.get()`; where the pointer values are converted to
///         the composite pointer type of T* and U* before the comparison is
///         made.

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator<(Ptr<T> const& x, Ptr<U> const& y) noexcept {
    using VP = typename std::common_type<T*, U*>::type;
    using V  = typename std::remove_pointer<VP>::type;

    return std::less<V const*>()(x.get(), y.get());
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator<(const Ptr<T>& x, std::nullptr_t) noexcept {
    return std::less<T const*>()(x.get(), nullptr);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator<(std::nullptr_t, const Ptr<T>& y) noexcept {
    return std::less<T const*>()(nullptr, y.get());
}

/// \brief Compares the pointer values
///
/// Returns true if the stored pointer of \p x is greater than the stored
/// pointer of \p y under implicit conversion rules.
///
/// \return `x.get() > y.get()`; where the pointer values are converted to
///         the composite pointer type of T* and U* before the comparison is
///         made.

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator>(Ptr<T> const& x, Ptr<U> const& y) noexcept {
    return (y < x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator>(const Ptr<T>& x, std::nullptr_t) noexcept {
    return (nullptr < x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator>(std::nullptr_t, const Ptr<T>& y) noexcept {
    return (y < nullptr);
}

/// \brief Compares the pointer values
///
/// Returns true if the stored pointer of \p x is less than or equal to the
/// stored pointer of \p y under implicit conversion rules.
///
/// \return `x.get() <= y.get()`; where the pointer values are converted to
///         the composite pointer type of T* and U* before the comparison is
///         made.

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator<=(Ptr<T> const& x, Ptr<U> const& y) noexcept {
    return !(y < x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator<=(const Ptr<T>& x, std::nullptr_t) noexcept {
    return !(nullptr < x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator<=(std::nullptr_t, const Ptr<T>& y) noexcept {
    return !(y < nullptr);
}

/// \brief Compares the pointer values
///
/// Returns true if the stored pointer of \p x is greater than or equal to the
/// stored pointer of \p y under implicit conversion rules.
///
/// \return `x.get() >= y.get()`; where the pointer values are converted to
///         the composite pointer type of T* and U* before the comparison is
///         made.

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator>=(Ptr<T> const& x, Ptr<U> const& y) noexcept {
    return !(x < y);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator>=(const Ptr<T>& x, std::nullptr_t) noexcept {
    return !(x < nullptr);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator>=(std::nullptr_t, const Ptr<T>& y) noexcept {
    return !(nullptr < y);
}
/// \}

//------------------------------------------------------------------------------
//
/// \brief Swap two pointers
///
/// Exchanges the contents of the two smart pointers.
///
/// \param [in] lhs the first pointer to swap
/// \param [in] rhs the second pointer to swap
template <class T>
inline void swap(Ptr<T>& lhs, Ptr<T>& rhs) noexcept {
    lhs.swap(rhs);
}

//==============================================================================
// GLOBAL FUNCTIONS CLASS Amino::MutablePtr
//==============================================================================

/// \name Comparison operator with nullptr.

/// \{
/// \brief Return true if pointers are equal
/// \return `x.get() == y.get()`

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator==(
    MutablePtr<T> const& x, MutablePtr<U> const& y) noexcept {
    assert(x.get() != y.get() || &x == &y);
    return x.get() == y.get();
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator==(const MutablePtr<T>& x, std::nullptr_t) noexcept {
    return !x;
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator==(std::nullptr_t, const MutablePtr<T>& y) noexcept {
    return !y;
}

/// \brief Return true if pointers are not equal
/// \return `x.get() != y.get()`

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator!=(
    MutablePtr<T> const& x, MutablePtr<U> const& y) noexcept {
    return !(x == y);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator!=(const MutablePtr<T>& x, std::nullptr_t) noexcept {
    return static_cast<bool>(x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator!=(std::nullptr_t, const MutablePtr<T>& y) noexcept {
    return static_cast<bool>(y);
}
/// \}

/// \name Ordering comparison

/// \{

/// \brief Compares the pointer values
///
/// Returns true if the stored pointer of \p x is less than the stored pointer
/// of \p y under implicit conversion rules.
///
/// \return `x.get() < y.get()`; where the pointer values are converted to
///         the composite pointer type of T* and U* before the comparison is
///         made.

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator<(MutablePtr<T> const& x, MutablePtr<U> const& y) noexcept {
    using VP = typename std::common_type<T*, U*>::type;
    using V  = typename std::remove_pointer<VP>::type;

    return std::less<V const*>()(x.get(), y.get());
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator<(const MutablePtr<T>& x, std::nullptr_t) noexcept {
    return std::less<T const*>()(x.get(), nullptr);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator<(std::nullptr_t, const MutablePtr<T>& y) noexcept {
    return std::less<T const*>()(nullptr, y.get());
}

/// \brief Compares the pointer values
///
/// Returns true if the stored pointer of \p x is greater than the stored
/// pointer of \p y under implicit conversion rules.
///
/// \return `x.get() > y.get()`; where the pointer values are converted to
///         the composite pointer type of T* and U* before the comparison is
///         made.

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator>(MutablePtr<T> const& x, MutablePtr<U> const& y) noexcept {
    return (y < x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator>(const MutablePtr<T>& x, std::nullptr_t) noexcept {
    return (nullptr < x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator>(std::nullptr_t, const MutablePtr<T>& y) noexcept {
    return (y < nullptr);
}

/// \brief Compares the pointer values
///
/// Returns true if the stored pointer of \p x is less than or equal to the
/// stored pointer of \p y under implicit conversion rules.
///
/// \return `x.get() <= y.get()`; where the pointer values are converted to
///         the composite pointer type of T* and U* before the comparison is
///         made.

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator<=(
    MutablePtr<T> const& x, MutablePtr<U> const& y) noexcept {
    return !(y < x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator<=(const MutablePtr<T>& x, std::nullptr_t) noexcept {
    return !(nullptr < x);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator<=(std::nullptr_t, const MutablePtr<T>& y) noexcept {
    return !(y < nullptr);
}

/// \brief Compares the pointer values
///
/// Returns true if the stored pointer of \p x is greater than or equal to the
/// stored pointer of \p y under implicit conversion rules.
///
/// \return `x.get() >= y.get()`; where the pointer values are converted to
///         the composite pointer type of T* and U* before the comparison is
///         made.

//------------------------------------------------------------------------------
//
template <class T, class U>
inline bool operator>=(
    MutablePtr<T> const& x, MutablePtr<U> const& y) noexcept {
    return !(x < y);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator>=(const MutablePtr<T>& x, std::nullptr_t) noexcept {
    return !(x < nullptr);
}

//------------------------------------------------------------------------------
//
template <class T>
inline bool operator>=(std::nullptr_t, const MutablePtr<T>& y) noexcept {
    return !(nullptr < y);
}
/// \}

//------------------------------------------------------------------------------
//
/// \brief Swap two pointers
///
/// Exchanges the contents of the two Amino::MutablePtr.
///
/// \param [in] lhs the first pointer to swap
/// \param [in] rhs the second pointer to swap
template <class T>
inline void swap(MutablePtr<T>& lhs, MutablePtr<T>& rhs) noexcept {
    lhs.swap(rhs);
}

/// \name Pointer casts
/// \{

//==============================================================================
// GLOBAL CASTING FUNCTIONS
//==============================================================================

/// \brief Static pointer cast
///
/// Creates a new instance of Ptr whose element type is obtained from the \p
/// rhs element type using a `static_cast<>` expression. The returned pointer
/// shares the ownership of the owned object with the original pointer.
///
/// If the argument is an empty pointer, the result will only be an empty
/// pointer.
///
/// \param [in] ptr the pointer to cast
/// \return the static cast pointer
/// \{
template <class T, class U>
inline Ptr<T> static_pointer_cast(Ptr<U> const& ptr) noexcept;
template <class T, class U>
inline Ptr<T> static_pointer_cast(Ptr<U>&& ptr) noexcept;
/// \}

//------------------------------------------------------------------------------
//
/// \brief Dynamic pointer cast
///
/// Creates a new instance of Ptr whose element type is obtained from the \p
/// rhs element type using a `dynamic_cast<>` expression. The returned pointer
/// shares the ownership of the owned object with the original pointer.
///
/// If the argument is an empty pointer, the result will only be an empty
/// pointer.
///
/// \param [in] ptr the pointer to cast
/// \return the dynamic cast pointer
/// \{
template <class T, class U>
inline Ptr<T> dynamic_pointer_cast(Ptr<U> const& ptr) noexcept;
template <class T, class U>
inline Ptr<T> dynamic_pointer_cast(Ptr<U>&& ptr) noexcept;
/// \}
/// \}

//==============================================================================
// FUNCTION makeDefaultPtr
//==============================================================================

/// \brief Creates a Ptr holding the default value for T
///
/// \see PtrDefaultFlag
/// \{
template <typename T>
std::enable_if_t<
    PtrInternal::DefaultPtrTraits::has_default_class<T>::value,
    Ptr<T>>
makeDefaultPtr() {
    return Internal::getDefaultClass<T>();
}
template <typename T>
std::enable_if_t<PtrInternal::DefaultPtrTraits::is_array<T>::value, Ptr<T>>
makeDefaultPtr() {
    return Ptr<T>(PointeeManager::newClass<T>());
}
template <typename T>
std::enable_if_t<
    !PtrInternal::DefaultPtrTraits::is_defaultable<T>::value,
    Ptr<T>>
makeDefaultPtr() {
    // This static_assert will always fail when makeDefaultPtr resolves to this
    // overload, indicating what needs to be done to fix the compile error.
    static_assert(
        PtrInternal::DefaultPtrTraits::has_default_class<T>::value,
        "Missing default class getter for class T. See "
        "AMINO_DECLARE_DEFAULT_CLASS in <Amino/Cpp/ClassDeclare.h> and "
        "AMINO_DEFINE_DEFAULT_CLASS in <Amino/Cpp/ClassDefine.h>");
    return nullptr;
}
/// \}

//------------------------------------------------------------------------------
// This ctor has to be defined after makeDefaultPtr() since it uses it.
template <class T>
inline Ptr<T>::Ptr(PtrDefaultFlag) : Ptr(makeDefaultPtr<T>()) {}

//==============================================================================
// FUNCTION newClassPtr
//==============================================================================

/// \brief Creates a Ptr holding a new T constructed from the given arguments.
///
/// This convenience function invokes Amino::newClass<T>() to allocate the
/// object, wraps it in a Amino::Ptr<T> and returns the Amino::Ptr.
///
/// \tparam     T     the type of object to allocate
/// \tparam     Args  the types of the constructor arguments
/// \param [in] args  the arguments to pass to the constructor of the object
/// \return           a Amino::Ptr to the allocated object
template <class T, class... Args>
inline Ptr<T> newClassPtr(Args&&... args) {
    static_assert(
        PointeeTraits::is_compliant<T>::value,
        "The class of type T cannot be stored in an Amino::Ptr<T>");
    return Ptr<T>(PointeeManager::newClass<T>(std::forward<Args>(args)...));
}

/// \brief Creates a Ptr holding a new T constructed from the given
/// initializer_list.
///
/// This allows writing simpler/shorter code. For example:
/// \code{.cpp}
/// auto array1 = Amino::newClassPtr<Amino::Array<int>>({1, 2, 3, 4});
/// // instead of
/// auto array2 = Amino::newClassPtr<Amino::Array<int>>(
///     std::initializer_list<int>{1, 2, 3, 4});
/// \endcode
///
/// \warning The curly braces must contain at least one element and all the
/// elements must have the exact same type. Otherwise the initializer_list's
/// element type \p E can't be deduced, and therefore it won't compile.
///
/// \tparam     T     the type of object to allocate
/// \tparam     E     the type of the elements of the initializer_list
/// \param [in] list  the initializer_list to pass to the constructor
/// \return           a Amino::Ptr to the allocated object
template <class T, class E>
inline Ptr<T> newClassPtr(std::initializer_list<E> list) {
    static_assert(
        PointeeTraits::is_compliant<T>::value,
        "The class of type T cannot be stored in an Amino::Ptr<T>");
    return Ptr<T>(PointeeManager::newClass<T>(std::move(list)));
}

//==============================================================================
// FUNCTION newMutablePtr
//==============================================================================

/// \brief Creates a MutablePtr holding a new T constructed from the given
/// arguments.
///
/// \tparam     T     the type of object to allocate
/// \tparam     Args  the types of the constructor arguments
/// \param [in] args  the arguments to pass to the constructor of the object
/// \return           a Amino::MutablePtr to the allocated object
///
/// \todo BIFROST-6529 Optimize to get single invocation for allocation of
/// T and control block.
template <class T, class... Args>
inline MutablePtr<T> newMutablePtr(Args&&... args) {
    static_assert(
        PointeeTraits::is_compliant<T>::value,
        "The class of type T cannot be stored in an Amino::MutablePtr<T>");
    return MutablePtr<T>(
        PointeeManager::newClass<T>(std::forward<Args>(args)...));
}

/// \brief Creates a MutablePtr holding a new T constructed from the given
/// initializer_list.
///
/// This allows writing simpler/shorter code. For example:
/// \code{.cpp}
/// auto array1 = Amino::newMutablePtr<Amino::Array<int>>({1, 2, 3, 4});
/// // instead of
/// auto array2 = Amino::newMutablePtr<Amino::Array<int>>(
///     std::initializer_list<int>{1, 2, 3, 4});
/// \endcode
///
/// \warning The curly braces must contain at least one element and all the
/// elements must have the exact same type. Otherwise the initializer_list's
/// element type \p E can't be deduced, and therefore it won't compile.
///
/// \tparam     T     the type of object to allocate
/// \tparam     E     the type of the elements of the initializer_list
/// \param [in] list  the initializer_list to pass to the constructor
/// \return           a Amino::MutablePtr to the allocated object
template <class T, class E>
inline MutablePtr<T> newMutablePtr(std::initializer_list<E> list) {
    static_assert(
        PointeeTraits::is_compliant<T>::value,
        "The class of type T cannot be stored in an Amino::MutablePtr<T>");
    return MutablePtr<T>(PointeeManager::newClass<T>(std::move(list)));
}

/// \brief Create a PtrGuard for the given Ptr.
///
/// Equivalent to `PtrGuard guard{src};`.
/// \{
template <typename T>
PtrGuard<T> createPtrGuard(Ptr<T>& src) {
    return PtrGuard{src};
}
template <typename T1, typename T2>
PtrGuard<T1> createPtrGuard(Ptr<T2>& src) {
    return PtrGuard<T1>(src);
}
template <typename T>
PtrGuard<T> createPtrGuard(Ptr<T>& src, PtrGuardUniqueFlag) {
    return PtrGuard{src, PtrGuardUniqueFlag{}};
}
/// \}

//==============================================================================
// PTR CAST IMPLEMENTATIONS
//==============================================================================

namespace Internal {
struct PtrCast {
    template <class T, class U>
    static inline Ptr<T> static_pointer_cast(Ptr<U> const& ptr) noexcept {
        T* p = static_cast<T*>(ptr.getPointee());
        return Ptr<T>(p, ptr.getCntrlBlk(), true);
    }
    template <class T, class U>
    static inline Ptr<T> static_pointer_cast(Ptr<U>&& ptr) noexcept {
        T*   p   = static_cast<T*>(ptr.getPointee());
        auto ret = Ptr<T>(p, ptr.getCntrlBlk(), false);
        ptr.init(nullptr, nullptr);
        return ret;
    }
    template <class T, class U>
    static inline Ptr<T> dynamic_pointer_cast(Ptr<U> const& ptr) noexcept {
        T* p = dynamic_cast<T*>(ptr.getPointee());
        if (!p) return Ptr<T>{};
        return Ptr<T>(p, ptr.getCntrlBlk(), true);
    }
    template <class T, class U>
    static inline Ptr<T> dynamic_pointer_cast(Ptr<U>&& ptr) noexcept {
        T* p = dynamic_cast<T*>(ptr.getPointee());
        if (!p) {
            ptr.reset();
            return Ptr<T>{};
        }
        auto ret = Ptr<T>(p, ptr.getCntrlBlk(), false);
        ptr.init(nullptr, nullptr);
        return ret;
    }
};
} // namespace Internal

//------------------------------------------------------------------------------
//
template <class T, class U>
inline Ptr<T> static_pointer_cast(Ptr<U> const& ptr) noexcept {
    return Internal::PtrCast::static_pointer_cast<T>(ptr);
}
template <class T, class U>
inline Ptr<T> static_pointer_cast(Ptr<U>&& ptr) noexcept {
    return Internal::PtrCast::static_pointer_cast<T>(std::move(ptr));
}

//------------------------------------------------------------------------------
//
template <class T, class U>
inline Ptr<T> dynamic_pointer_cast(Ptr<U> const& ptr) noexcept {
    return Internal::PtrCast::dynamic_pointer_cast<T>(ptr);
}
template <class T, class U>
inline Ptr<T> dynamic_pointer_cast(Ptr<U>&& ptr) noexcept {
    return Internal::PtrCast::dynamic_pointer_cast<T>(std::move(ptr));
}
} // namespace Amino

//==============================================================================
// std::hash< Amino::Ptr<T> >
//==============================================================================

namespace std {

/// \brief Hash functor for Amino::Ptr
///
/// This is a specialization of std::hash for \ref Amino::Ptr<T>. It allows
/// users users to obtain a default functor for the unordered std containers.
/// The hash function is based on the pointer value
/// (i.e. \ref Amino::Ptr<T>::get()).
///
/// \tparam T the \ref Amino::Ptr element_type
template <class T>
struct hash<Amino::Ptr<T>> {
    using argument_type = Amino::Ptr<T>;
    using result_type   = size_t;

    result_type operator()(const argument_type& ptr) const noexcept {
        return hash<T const*>()(ptr.get());
    }
};
} // namespace std

#endif

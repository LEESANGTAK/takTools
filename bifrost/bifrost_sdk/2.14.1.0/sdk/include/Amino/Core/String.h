//-
// =============================================================================
// Copyright 2025 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

/// \file String.h
///
/// \brief String class
///
/// \see Amino::String

#ifndef AMINO_CORE_STRING_H
#define AMINO_CORE_STRING_H

#include "CoreExport.h"

#include <Amino/Core/StringView.h>

#include "internal/ConfigMacros.h"
#include "internal/Storage.h"
#include "internal/TypeTraits.h"

#include <cstddef>
#include <string_view>

namespace Amino {
struct SdkStorage;

//-----------------------------------------------------------------------------
// Class String
//-----------------------------------------------------------------------------

/// \brief The string class used by Amino
///
/// \warning \ref Amino::String is NOT a replacement for standard strings
/// (like std::string). It is only meant to be used with Amino graphs. Therefore
/// if a value never needs to flow directly into a graph, a standard string
/// (like std::string) should be used instead.
class AMINO_CORE_SHARED_DECL String {
private:
    /// \brief Helper traits to enable functions for StringViewLike types.
    /// \{
    template <typename T>
    using is_string_view_like = std::is_convertible<T const&, StringView>;
    template <typename T, typename R = void>
    using enable_if_string_view_like =
        std::enable_if_t<is_string_view_like<T>::value, R>;
    /// \}

public:
    /*----- types -----*/

    using value_type      = char;
    using iterator        = value_type*;
    using const_iterator  = const value_type*;
    using size_type       = std::size_t;
    using difference_type = std::ptrdiff_t;

    /*----- member functions -----*/

    /// \brief Construct an empty string
    String();

    /// \brief Constructing a \ref String from a nullptr_t is not allowed.
    // NOLINTNEXTLINE(google-explicit-constructor)
    String(std::nullptr_t) = delete;

    /// \brief Copy constructor
    ///
    /// \param str The string to copy
    String(const String& str);

    /// \brief Move constructor
    ///
    /// \param str The string to move
    String(String&& str) noexcept;

    /// \brief Construct a string from another
    ///
    /// \details The portion of the string to copy is specified by the starting
    /// position and length. If the string is too short or len is npos then the
    /// entire string will be copied
    ///
    /// \param str The other string
    ///
    /// \param pos The position to start from
    ///
    /// \param len The number of characters to take
    String(const String& str, size_type pos, size_type len = npos);

    /// \brief Construct a string from char char*
    ///
    /// \param s The char * to use
    String(const char* s); // NOLINT: implicit conversion allowed!

    /// \brief Construct a string from a char*
    ///
    /// \param s The char* to use
    ///
    /// \param n The number of characters to take from the char* buffer
    String(const char* s, size_type n);

    /// \brief Construct a \ref String from a \ref StringView
    ///
    /// \param sv The \ref StringView from which to copy the data when
    /// constructing the \ref String.
    explicit String(StringView sv) : String(sv.data(), sv.size()) {}

    /// \brief Construct a string by filling it
    ///
    /// \param n The number or characters to fill
    ///
    /// \param c The character to use in the fill
    String(size_type n, char c);

    /// \brief Destructor
    ~String();

    /// \brief Assign to a string
    ///
    /// \param s The string/character(s) to assign
    ///
    /// \return The new string
    /// \{
    String& operator=(const String& s);
    String& operator=(String&& s) noexcept;
    String& operator=(const char* s);
    String& operator=(char s);

    template <
        typename StringViewLike,
        typename = enable_if_string_view_like<StringViewLike>>
    AMINO_INTERNAL_FORCEINLINE String& operator=(StringViewLike const& s) {
        internal_assign(s);
        return *this;
    }
    /// \}

    /// \brief std::string_view conversions
    /// \{
    // NOLINTNEXTLINE(google-explicit-constructor)
    AMINO_INTERNAL_FORCEINLINE operator std::string_view() const {
        return {internal_string_view()}; // LCOV_EXCL_BR_LINE
    }
    /// \}

    /// \brief Append a copy of a string
    ///
    /// \param s The string to append
    ///
    /// \return The appended string
    /// \{
    String& append(const String& s);
    String& append(String&& s);
    String& append(const char* s);

    template <typename StringViewLike>
    AMINO_INTERNAL_FORCEINLINE //
        enable_if_string_view_like<StringViewLike, String&>
        append(StringViewLike const& s) {
        internal_append(s);
        return *this;
    }
    /// \}

    /// \brief Appends a char* to the string
    ///
    /// \param s The char* to append
    ///
    /// \param n The number of characters from the char* buffer to append
    ///
    /// \return The appended string
    String& append(const char* s, size_type n);

    /// \brief Appends a part of a string
    ///
    /// \details The portion of the string to append is specified by the sub
    /// position and sub length. If the string is too short or len is npos then
    /// the entire string will be copied
    ///
    /// \param str The string to append
    ///
    /// \param subpos The subposition of the string to use
    ///
    /// \param sublen The sub length to use
    ///
    /// \return The appended string
    String& append(const String& str, size_type subpos, size_type sublen);

    /// \brief Append the same character multiple times
    ///
    /// \param n The number of times to append the character
    ///
    /// \param c The character to append
    ///
    /// \return The appended string
    String& append(size_type n, char c);

    /// \brief Assign a string
    ///
    /// \param s The string to assign
    ///
    /// \return The string that was assigned
    /// \{
    String& assign(const String& s) { return *this = s; }
    String& assign(String&& s) noexcept { return *this = std::move(s); }
    String& assign(const char* s) { return *this = s; }

    template <typename StringViewLike>
    AMINO_INTERNAL_FORCEINLINE //
        enable_if_string_view_like<StringViewLike, String&>
        assign(StringViewLike const& s) {
        internal_assign(s);
        return *this;
    }
    /// \}

    /// \brief Assign a char* to the string
    ///
    /// \param s The char* to assign
    ///
    /// \param n The number of characters from the char* buffer to assign
    ///
    /// \return The string that was assigned
    String& assign(const char* s, size_type n);

    /// Assign a part of a string
    ///
    /// \details The portion of the string to assign is specified by the sub
    /// position and sub length. If the string is too short or len is npos then
    /// the entire string will be copied
    ///
    /// \param str The string to assign a part of
    ///
    /// \param subpos The sub position to use
    ///
    /// \param sublen The sub length to use
    ///
    /// \return The string that was assigned
    String& assign(const String& str, size_type subpos, size_type sublen);

    /// \brief Assign a character multiple times to the string
    ///
    /// \param n The number of times to assign the character
    ///
    /// \param c The character to assign
    ///
    /// \return The string that was assigned
    String& assign(size_type n, char c);

    /// \brief Return a character at a position
    ///
    /// \param pos The position of the character
    char& at(size_type pos);

    /// \brief Return a character at a position
    ///
    /// \param pos The position of the character
    const char& at(size_type pos) const;

    /// \brief Return the last character
    char& back();

    /// \brief Return the last character
    const char& back() const;

    /// \brief Return the allocated storage size of the string
    ///
    /// \details This is not necessarily the same as the string length
    ///
    /// \return The capacity
    size_type capacity() const;

    /// \brief Clear the string
    ///
    /// \post `empty() == true`
    void clear();

    /// \brief Compare a string
    ///
    /// \param s The string to compare to
    ///
    /// \return 0 if they are equal, < 0 is less than or >0 if greater than
    /// \{
    int compare(const String& s) const;
    int compare(const char* s) const;

    template <typename StringViewLike>
    AMINO_INTERNAL_FORCEINLINE //
        enable_if_string_view_like<StringViewLike, int>
        compare(StringViewLike const& s) const {
        return internal_compare(s);
    }
    /// \}

    /// \brief Compare a string
    ///
    /// \param str The string to compare to
    ///
    /// \param pos The position to start at
    ///
    /// \param len The number of characters to compare
    ///
    /// \return 0 if they are equal, < 0 is less than or >0 if greater than
    int compare(size_type pos, size_type len, const String& str) const;

    /// \brief Compare a string
    ///
    /// \param str The string to compare to
    ///
    /// \param pos The position to start at
    ///
    /// \param len The number of characters to compare
    ///
    /// \param subpos The position in str to use
    ///
    /// \param sublen The number of characters in str to use
    ///
    /// \return 0 if they are equal, < 0 is less than or >0 if greater than
    int compare(
        size_type     pos,
        size_type     len,
        const String& str,
        size_type     subpos,
        size_type     sublen) const;

    /// \brief Compare a string
    ///
    /// \param s The char* to compare to
    ///
    /// \param pos The position to start at
    ///
    /// \param len The number of characters to compare
    ///
    /// \return 0 if they are equal, < 0 is less than or >0 if greater than
    int compare(size_type pos, size_type len, const char* s) const;

    /// \brief Compare a string
    ///
    /// \param s The char* to compare to
    ///
    /// \param pos The position to start at
    ///
    /// \param len The number of characters to compare
    ///
    /// \param n The number of characters in the char* buffer to compare to
    ///
    /// \return 0 if they are equal, < 0 is less than or >0 if greater than
    int compare(size_type pos, size_type len, const char* s, size_type n) const;

    /// \brief Copy part of the string into a char*
    ///
    /// \details Method does not append a null character at the end of the
    /// string
    ///
    /// \param s The char* array to copy into
    ///
    /// \param len The number of characters to copy
    ///
    /// \param pos The position of the first character to be copied
    ///
    /// \return The number of characters copied
    size_type copy(char* s, size_type len, size_type pos = 0) const;

    /// \brief Return the string as a char*
    const char* c_str() const;

    /// \brief Return the string as a char*
    const char* data() const;

    /// Return true if this string is empty
    bool empty() const;

    /// \brief Erase a part of a string
    ///
    /// \param pos The starting position
    ///
    /// \param len The number of string positions to erase
    ///
    /// \return The string result
    String& erase(size_type pos = 0, size_type len = npos);

    /// \brief Multiple methods for finding strings
    ///
    /// \details Searches can be done for Strings, char* or char. The pos
    /// parameter is where the search is started in this string. The n parameter
    /// gives how many characters out of the char* buffer to use in the search.
    /// The return value is the position of the first character that matches or
    /// npos if there is no match.
    ///
    /// \{
    size_type find(const String& str, size_type pos = 0) const;
    size_type find(const char* s, size_type pos = 0) const;
    size_type find(const char* s, size_type pos, size_type n) const;
    size_type find(char c, size_type pos = 0) const;
    /// \}

    /// \brief Multiple methods for finding the first character that does not
    /// match
    ///
    /// \details Matches can be performed by string, char* or char. The pos
    /// parameter is the starting point in the string. The n parameter is the
    /// starting point in the char* buffer array. The return values is the
    /// position for the first character that does not match or npos otherwise
    ///
    /// \{
    size_type find_first_not_of(const String& str, size_type pos = 0) const;
    size_type find_first_not_of(const char* s, size_type pos = 0) const;
    size_type find_first_not_of(
        const char* s, size_type pos, size_type n) const;
    size_type find_first_not_of(char c, size_type pos = 0) const;
    /// \}

    /// \brief Multiple methods for finding the first character that matches
    ///
    /// \details Matches can be performed by string, char* or char. The pos
    /// parameter is the starting point in the string. The n parameter is the
    /// starting point in the char* buffer array. The return values is the
    /// position for the first character that match or npos otherwise
    ///
    /// \{
    size_type find_first_of(const String& str, size_type pos = 0) const;
    size_type find_first_of(const char* s, size_type pos = 0) const;
    size_type find_first_of(const char* s, size_type pos, size_type n) const;
    size_type find_first_of(char c, size_type pos = 0) const;
    /// \}

    /// \brief Multiple methods for finding the first character that does not
    /// match from the end
    ///
    /// \details Matches can be performed by string, char* or char. The pos
    /// parameter is the starting point in the string. The n parameter is the
    /// starting point in the char* buffer array. The return values is the
    /// position for the first character that does not match or npos otherwise
    ///
    /// \{
    size_type find_last_not_of(const String& str, size_type pos = npos) const;
    size_type find_last_not_of(const char* s, size_type pos = npos) const;
    size_type find_last_not_of(const char* s, size_type pos, size_type n) const;
    size_type find_last_not_of(char c, size_type pos = npos) const;
    /// \}

    /// \brief Multiple methods for finding the first character that matches
    /// from the end
    ///
    /// \details Matches can be performed by string, char* or char. The pos
    /// parameter is the starting point in the string. The n parameter is the
    /// starting point in the char* buffer array. The return values is the
    /// position for the first character that match or npos otherwise
    ///
    /// \{
    size_type find_last_of(const String& str, size_type pos = npos) const;
    size_type find_last_of(const char* s, size_type pos = npos) const;
    size_type find_last_of(const char* s, size_type pos, size_type n) const;
    size_type find_last_of(char c, size_type pos = npos) const;
    /// \}

    /// Return an iterator to the beginning of the string
    ///
    /// \{
    iterator       begin();
    const_iterator begin() const { return cbegin(); }
    const_iterator cbegin() const;
    /// \}

    /// Return an iterator to the end of the string
    ///
    /// \{
    iterator       end();
    const_iterator end() const { return cend(); }
    const_iterator cend() const;
    /// \}

    /// Return the first character of the string
    /// \{
    char&       front();
    const char& front() const;
    /// \}

    /// \brief Multiple methods for string insertion
    ///
    /// \details String insertion can be done by String, char* or char. The pos
    /// parameter is the starting position of the insertion. The subpos is the
    /// starting position of the string to be inserted while the sublen is how
    /// many characters of the string should be inserted. The n parameter is how
    /// many characters of the char* buffer should be copied. The result is the
    /// new string
    ///
    /// \{
    String& insert(size_type pos, const String& str);
    String& insert(
        size_type pos, const String& str, size_type subpos, size_type sublen);
    String& insert(size_type pos, const char* s);
    String& insert(size_type pos, const char* s, size_type n);
    String& insert(size_type pos, size_type n, char c);
    /// \}

    /// \brief Return the length of the string
    size_type length() const;

    /// Return the maximum size this string can reach
    size_type max_size() const;

    /// \brief The append operator
    ///
    /// \param s The string/character(s) to append
    ///
    /// \return The appended string
    /// \{
    String& operator+=(const String& s) { return append(s); }
    String& operator+=(const char* s) { return append(s); }
    String& operator+=(char s) {
        push_back(s);
        return *this;
    }
    template <typename StringViewLike>
    AMINO_INTERNAL_FORCEINLINE //
        enable_if_string_view_like<StringViewLike, String&>
        operator+=(StringViewLike const& s) {
        return internal_append(s);
    }
    /// \}

    /// \brief Return a character at a position
    ///
    /// \param pos The position of the character
    ///
    /// \return Reference to the character at the specified position
    char& operator[](size_type pos);

    /// \brief Return a character at a position
    ///
    /// \param pos The position of the character
    ///
    /// \return Reference to the character at the specified position
    const char& operator[](size_type pos) const;

    /// \brief Remove the last character of the string
    void pop_back();

    /// \brief Push a new character onto the back of the string
    ///
    /// \param c The new character to add to the back
    void push_back(char c);

    /// \brief Multiple methods for string replacement
    ///
    /// \details String replacement can be done with a String, char* or char.
    /// The pos parameter is the starting position of the replacement in this
    /// string. The len parameter is the length of the replacement in this
    /// string. The subpos and sublen are the equivalents in the String
    /// parameter for that specific method.
    ///
    /// \{
    String& replace(size_type pos, size_type len, const String& str);
    String& replace(
        size_type     pos,
        size_type     len,
        const String& str,
        size_type     subpos,
        size_type     sublen);
    String& replace(size_type pos, size_type len, const char* s);
    String& replace(size_type pos, size_type len, const char* s, size_type n);
    String& replace(size_type pos, size_type len, size_type n, char c);
    /// \}

    /// \brief Change the capacity of the string
    ///
    /// \param n The new size
    void reserve(size_type n = 0);

    /// \brief Change the size of the string
    ///
    /// \param n The new size of the string
    void resize(size_type n);

    /// \brief Change the size of the string
    ///
    /// \param n The new size of the string
    ///
    /// \param c The fill character to use if the string was expanded
    void resize(size_type n, char c);

    /// \brief Multiple methods for finding a string starting from the end
    ///
    /// \details We can search for a String, char* or char. The pos parameter
    /// gives the starting position while the n parameter is how much characters
    /// to search for. The return value is the first character of the match or
    /// npos if there is no match
    ///
    /// \{
    size_type rfind(const String& str, size_type pos = npos) const;
    size_type rfind(const char* s, size_type pos = npos) const;
    size_type rfind(const char* s, size_type pos, size_type n) const;
    size_type rfind(char c, size_type pos = npos) const;
    /// \}

    /// \brief Try to reduce the memory footprint of the string
    void shrink_to_fit();

    /// \brief Return the size of the string
    size_type size() const;

    /// \brief Return a part of this string
    ///
    /// \param pos The position to start at
    ///
    /// \param len The number of characters to take
    ///
    /// \return The substring
    String substr(size_type pos = 0, size_type len = npos) const;

    /// \brief Swap this string with another
    ///
    /// \param str The other string to swap
    void swap(String& str);

    /// \brief Operator ==
    ///
    /// \param rhs The string to compare to
    ///
    /// \return true if the strings are equal, false otherwise
    /// \{
    bool operator==(const String& rhs) const;
    bool operator==(char const* rhs) const;

    template <typename StringViewLike>
    AMINO_INTERNAL_FORCEINLINE //
        enable_if_string_view_like<StringViewLike, bool>
        operator==(StringViewLike const& rhs) const {
        return internal_equals(rhs);
    }
    /// \}

    /// \brief Operator !=
    ///
    /// \param rhs The string to compare to
    ///
    /// \return true if the strings are equal, false otherwise
    /// \{
    bool operator!=(const String& rhs) const { return !(*this == rhs); }
    bool operator!=(char const* rhs) const { return !(*this == rhs); }

    template <typename StringViewLike>
    AMINO_INTERNAL_FORCEINLINE //
        enable_if_string_view_like<StringViewLike, bool>
        operator!=(StringViewLike const& rhs) const {
        return !internal_equals(rhs);
    }
    /// \}

    /// \brief Operator <
    ///
    /// \param rhs The string to compare to
    ///
    /// \return true if the strings are equal, false otherwise
    /// \{
    template <typename T>
    AMINO_INTERNAL_FORCEINLINE auto operator<(T const& rhs) const
        -> decltype(compare(rhs) < 0) {
        return compare(rhs) < 0;
    }
    template <typename T>
    AMINO_INTERNAL_FORCEINLINE auto operator>(T const& rhs) const
        -> decltype(compare(rhs) > 0) {
        return compare(rhs) > 0;
    }
    template <typename T>
    AMINO_INTERNAL_FORCEINLINE auto operator<=(T const& rhs) const
        -> decltype(compare(rhs) <= 0) {
        return compare(rhs) <= 0;
    }
    template <typename T>
    AMINO_INTERNAL_FORCEINLINE auto operator>=(T const& rhs) const
        -> decltype(compare(rhs) >= 0) {
        return compare(rhs) >= 0;
    }
    /// \}

    /// \brief Return the string as a char*
    const char* asChar() const;

public:
    /// \brief Maximum value for a size_type.
    ///
    /// \note `npos` does not have a One Definition Rule (ODR). Do not reference
    /// it (do not use &npos).
    static constexpr size_type npos = ~size_type(0);

private:
    /// \cond AMINO_INTERNAL_DOCS
    ///
    /// \brief Implementation of the string_view conversion operator.
    StringView internal_string_view() const;

    /// \brief Implementation of append for StringViewLike types.
    String& internal_append(StringView s);

    /// \brief Implementation of assign for StringViewLike types.
    String& internal_assign(StringView s);

    /// \brief Implementation of operator== for StringViewLike types.
    bool internal_equals(StringView s) const;

    /// \brief Implementation of compare for StringViewLike types.
    int internal_compare(StringView s) const;

    friend SdkStorage;
    Internal::Storage_t<2> m_storage{};
    /// \endcond
};

//
// Non-member functions
//

/// \brief Concatenation operators( non member )
///
/// \{
AMINO_CORE_SHARED_DECL String operator+(const String& lhs, const String& rhs);
AMINO_CORE_SHARED_DECL String operator+(const String& lhs, const char* rhs);
AMINO_CORE_SHARED_DECL String operator+(const char* lhs, const String& rhs);
AMINO_CORE_SHARED_DECL String operator+(const String& lhs, char rhs);
AMINO_CORE_SHARED_DECL String operator+(char lhs, const String& rhs);
/// \}

/// \cond AMINO_INTERNAL_DOCS
namespace Internal {
/// \brief Traits to enable comparison operators when Amino::String is on the
/// right hand side.
/// \{
template <typename T>
using is_amino_string = std::
    is_same<std::remove_cv_t<std::remove_reference_t<std::decay_t<T>>>, String>;
template <typename LHS, typename RHS>
using enable_if_rhs_compare = std::enable_if_t<
    !is_amino_string<LHS>::value && is_amino_string<RHS>::value,
    bool>;
/// \}
} // namespace Internal
///  \endcond

/// \brief Relational operators (if Amino::String is on the right hand side)
/// \{
// String on the right hand side
template <typename LHS, typename RHS>
AMINO_INTERNAL_FORCEINLINE Internal::enable_if_rhs_compare<LHS, RHS> operator==(
    LHS const& lhs, RHS&& rhs) {
    return rhs.operator==(lhs);
}
template <typename LHS, typename RHS>
AMINO_INTERNAL_FORCEINLINE Internal::enable_if_rhs_compare<LHS, RHS> operator!=(
    LHS const& lhs, RHS&& rhs) {
    return rhs.operator!=(lhs);
}
template <typename LHS, typename RHS>
AMINO_INTERNAL_FORCEINLINE Internal::enable_if_rhs_compare<LHS, RHS> operator<(
    LHS const& lhs, RHS&& rhs) {
    return rhs.operator>(lhs);
}
template <typename LHS, typename RHS>
AMINO_INTERNAL_FORCEINLINE Internal::enable_if_rhs_compare<LHS, RHS> operator>(
    LHS const& lhs, RHS&& rhs) {
    return rhs.operator<(lhs);
}
template <typename LHS, typename RHS>
AMINO_INTERNAL_FORCEINLINE Internal::enable_if_rhs_compare<LHS, RHS> operator<=(
    LHS const& lhs, RHS&& rhs) {
    return rhs.operator>=(lhs);
}
template <typename LHS, typename RHS>
AMINO_INTERNAL_FORCEINLINE Internal::enable_if_rhs_compare<LHS, RHS> operator>=(
    LHS const& lhs, RHS&& rhs) {
    return rhs.operator<=(lhs);
}
/// \}

/// \brief Swap two strings( non member )
///
/// \param x The first string
///
/// \param y the second string
AMINO_CORE_SHARED_DECL void swap(String& x, String& y);

/// \brief Converts a integral value to a string (in base 10).
///
/// (Same as std::to_string).
/// \{
AMINO_CORE_SHARED_DECL String to_string(signed char value);
AMINO_CORE_SHARED_DECL String to_string(signed short value);
AMINO_CORE_SHARED_DECL String to_string(signed int value);
AMINO_CORE_SHARED_DECL String to_string(signed long long value);
AMINO_CORE_SHARED_DECL String to_string(unsigned char value);
AMINO_CORE_SHARED_DECL String to_string(unsigned short value);
AMINO_CORE_SHARED_DECL String to_string(unsigned int value);
AMINO_CORE_SHARED_DECL String to_string(unsigned long long value);
/// \}

template <>
struct Internal::GetTypeCategory<String> {
    static constexpr auto value = TypeCategory::eStr;
};

//==============================================================================
// NAMESPACE StringLiteral
//==============================================================================

namespace StringLiteral {

/// \brief User defined literal for Amino::String.
///
/// Example:
/// \code{.cpp}
/// using namespace Amino::StringLiteral;
/// auto my_amino_string = "some string"_as;
/// \endcode
inline String operator""_as(char const* data, size_t size) {
    return String{data, size};
}

} // namespace StringLiteral

} // namespace Amino

#endif

//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \cond AMINO_INTERNAL_DOCS
///
/// \file ConfigMacros.h
///
/// \brief Compile configuration macros.

#ifndef AMINO_CONFIG_MACROS_H
#define AMINO_CONFIG_MACROS_H

//==============================================================================
// PLATFORM DETECTION
//==============================================================================

#define AMINO_INTERNAL_PLATFORM_IS_WINDOWS 0
#define AMINO_INTERNAL_PLATFORM_IS_LINUX 0
#define AMINO_INTERNAL_PLATFORM_IS_OSX 0

#if defined(_WIN32)
#undef AMINO_INTERNAL_PLATFORM_IS_WINDOWS
#define AMINO_INTERNAL_PLATFORM_IS_WINDOWS 1
#elif defined(__linux__)
#undef AMINO_INTERNAL_PLATFORM_IS_LINUX
#define AMINO_INTERNAL_PLATFORM_IS_LINUX 1
#elif defined(__APPLE__)
#undef AMINO_INTERNAL_PLATFORM_IS_OSX
#define AMINO_INTERNAL_PLATFORM_IS_OSX 1
#else
#error "Unsupported platform..."
#endif

//==============================================================================
// COMPILER TARGET DETECTION - the architecture the compiler is compiling for.
//==============================================================================
// GCC and clang defines __aarch64__
// MSVC defines _M_ARM64
#if (defined(__aarch64__) || defined(_M_ARM64))
#define AMINO_INTERNAL_ARCH_IS_ARM64 1
#define AMINO_INTERNAL_ARCH_IS_X86_64 0
#elif (defined(__x86_64__) || defined(_M_AMD64))
#define AMINO_INTERNAL_ARCH_IS_X86_64 1
#define AMINO_INTERNAL_ARCH_IS_ARM64 0
#else
#define AMINO_INTERNAL_ARCH_IS_X86_64 0
#define AMINO_INTERNAL_ARCH_IS_ARM64 0
#endif

//==============================================================================
// COMPILER DETECTION
//==============================================================================

#define AMINO_INTERNAL_COMPILER_IS_CLANG 0
#define AMINO_INTERNAL_COMPILER_IS_INTEL 0
#define AMINO_INTERNAL_COMPILER_IS_GCC 0
#define AMINO_INTERNAL_COMPILER_IS_MSC 0

#if defined(__clang__)
//  Clang C++ emulates GCC and MSC, so it has to appear early.
#undef AMINO_INTERNAL_COMPILER_IS_CLANG
#define AMINO_INTERNAL_COMPILER_IS_CLANG 1
#elif defined(__INTEL_COMPILER) || defined(__ICL) || defined(__ICC) || \
    defined(__ECC)
//  Intel emulates MSC, so it has to appear early.
#undef AMINO_INTERNAL_COMPILER_IS_INTEL
#define AMINO_INTERNAL_COMPILER_IS_INTEL 1
#elif defined(__GNUC__)
//  GNU C++.
#undef AMINO_INTERNAL_COMPILER_IS_GCC
#define AMINO_INTERNAL_COMPILER_IS_GCC 1
#elif defined(_MSC_VER)
//  Microsoft visual studio
#undef AMINO_INTERNAL_COMPILER_IS_MSC
#define AMINO_INTERNAL_COMPILER_IS_MSC 1
#else
#error "Unknown compiler configuration..."
#endif

//==============================================================================
// COMPILER OPTIONS
//==============================================================================

#define AMINO_INTERNAL_OPTION_HAS_RTTI 0

#ifdef __has_feature
#if __has_feature(cxx_rtti)
#undef AMINO_INTERNAL_OPTION_HAS_RTTI
#define AMINO_INTERNAL_OPTION_HAS_RTTI 1
#endif
#endif

#if defined(__GXX_RTTI) || defined(_CPPRTTI)
#undef AMINO_INTERNAL_OPTION_HAS_RTTI
#define AMINO_INTERNAL_OPTION_HAS_RTTI 1
#endif

//==============================================================================
// UNREACHABLE
//==============================================================================

/// \def AMINO_INTERNAL_UNREACHABLE(MSG)
///
/// \brief Macro indicating that the code path is unreachable
///
/// Macro indicating that the code path is unreachable. The code path might be
/// unreachable for various reasons: class invariants, all cases covered by a
/// switch statement, etc...
///
/// In debug builds, an assertion is raised if the macro is ever executed. In
/// optimized builds, an intrinsic is used to tell the optimizer that the code
/// path can be entirely pruned out. That often leads to significantly more
/// efficient code being generated.
#if AMINO_INTERNAL_COMPILER_IS_CLANG || AMINO_INTERNAL_COMPILER_IS_GCC
// NOLINT to silence up clang-tidy warning:
// warning: found assert() that could be replaced by static_assert()
// [cert-dcl03-c]
#define AMINO_INTERNAL_UNREACHABLE(MSG) \
    assert(false && MSG); /* NOLINT */  \
    __builtin_unreachable()

#elif AMINO_INTERNAL_COMPILER_IS_MSC
#define AMINO_INTERNAL_UNREACHABLE(MSG) \
    assert(false && MSG);               \
    __assume(false)

#else
#error "AMINO_INTERNAL_UNREACHABLE(): Unsupported compiler!"
#define AMINO_INTERNAL_UNREACHABLE(MSG) assert(false && MSG)
#endif

//==============================================================================
// WARNING MACROS
//==============================================================================

/// \brief Helper defining the various warning macros.
///
/// It encapsulates the compiler differences. For gcc and clang, the macro uses
/// the C99 _Pragma() preprocessor directive. It also takes care of stringizing
/// the argument passed to _Pragma(). For MSC, this is using the Microsoft
/// specific __pragma() preprocessor extension.
#if AMINO_INTERNAL_COMPILER_IS_CLANG || AMINO_INTERNAL_COMPILER_IS_GCC
#define AMINO_INTERNAL_PRAGMA(a) _Pragma(#a)
#elif AMINO_INTERNAL_COMPILER_IS_MSC
#define AMINO_INTERNAL_PRAGMA(a) __pragma(a)
#else
#define AMINO_INTERNAL_PRAGMA(a) /* empty */
#endif

//------------------------------------------------------------------------------
//
/// \brief Warning Push
///
/// This is to be called before a collection of warnings which are to
/// be ignored, and when used should be closed with the
/// AMINO_INTERNAL_WARNING_POP.
///
/// Any additional compilers that are added to this macro should have
/// an equivalent statement included in the disable and pop macro
/// respectively.
#if AMINO_INTERNAL_COMPILER_IS_CLANG || AMINO_INTERNAL_COMPILER_IS_GCC
#define AMINO_INTERNAL_WARNING_PUSH AMINO_INTERNAL_PRAGMA(GCC diagnostic push)
#elif AMINO_INTERNAL_COMPILER_IS_MSC
#define AMINO_INTERNAL_WARNING_PUSH AMINO_INTERNAL_PRAGMA(warning(push))
#else
#define AMINO_INTERNAL_WARNING_PUSH
#endif

//------------------------------------------------------------------------------
//
/// \brief Warning Disable
///
/// This macro should be called within a compiler or OS specific set
/// of warnings, as it does not distinguish which warning identifiers
/// correspond to which compiler. It can be called once for every
/// warning to be disabled.
///
/// Assure that any call of this macro is surrounded with a push and
/// pop macro.
#if AMINO_INTERNAL_COMPILER_IS_CLANG || AMINO_INTERNAL_COMPILER_IS_GCC
#define AMINO_INTERNAL_WARNING_DISABLE(a) \
    AMINO_INTERNAL_PRAGMA(GCC diagnostic ignored #a)
#elif AMINO_INTERNAL_COMPILER_IS_MSC
#define AMINO_INTERNAL_WARNING_DISABLE(a) \
    AMINO_INTERNAL_PRAGMA(warning(disable : a))
#else
#define AMINO_INTERNAL_WARNING_DISABLE(a)
#endif

//------------------------------------------------------------------------------
//
/// \brief Disable specific warnings on specific compilers
/// \{
#if AMINO_INTERNAL_COMPILER_IS_MSC
#define AMINO_INTERNAL_WARNING_DISABLE_MSC(a) AMINO_INTERNAL_WARNING_DISABLE(a)
#else
#define AMINO_INTERNAL_WARNING_DISABLE_MSC(a)
#endif

#if AMINO_INTERNAL_COMPILER_IS_CLANG
#define AMINO_INTERNAL_WARNING_DISABLE_CLANG(a) \
    AMINO_INTERNAL_WARNING_DISABLE(a)
#else
#define AMINO_INTERNAL_WARNING_DISABLE_CLANG(a)
#endif

#if AMINO_INTERNAL_COMPILER_IS_GCC
#define AMINO_INTERNAL_WARNING_DISABLE_GCC(a) AMINO_INTERNAL_WARNING_DISABLE(a)
#else
#define AMINO_INTERNAL_WARNING_DISABLE_GCC(a)
#endif
/// \}

//------------------------------------------------------------------------------
//
/// \brief Warning Pop
///
/// This will end a selection of disabled warnings, and must match to
/// AMINO_INTERNAL_WARNING_PUSH, after a selection (possibly empty) of
/// AMINO_INTERNAL_WARNING_DISABLE.
#if AMINO_INTERNAL_COMPILER_IS_CLANG || AMINO_INTERNAL_COMPILER_IS_GCC
#define AMINO_INTERNAL_WARNING_POP AMINO_INTERNAL_PRAGMA(GCC diagnostic pop)
#elif AMINO_INTERNAL_COMPILER_IS_MSC
#define AMINO_INTERNAL_WARNING_POP AMINO_INTERNAL_PRAGMA(warning(pop))
#else
#define AMINO_INTERNAL_WARNING_POP
#endif

//------------------------------------------------------------------------------
//
/// \def AMINO_INTERNAL_DEPRECATED(REASON)
///
/// \brief Macro indicating that a declaration is deprecated
///
/// The macro can be used to indicate that a declaration is deprecated and
/// shouldn't be used anymore in new code. The deprecated declaration could be
/// a function or a class, for example. The macro also allows one to provide an
/// explanation concerning the deprecation.
///
/// \note The deprecation warning is disabled on MSC because it leads to an
///       error being reported which causes the entire build to fail. This is
///       due to the presence of the "warning as errors (/WX)" flag. There
///       doesn't seem to be a way to turn off the warning as errors for a
///       single specific warning.
#if AMINO_INTERNAL_COMPILER_IS_MSC
#define AMINO_INTERNAL_DEPRECATED(REASON)
#else
#define AMINO_INTERNAL_DEPRECATED(REASON) [[deprecated(REASON)]]
#endif

//==============================================================================
// EXPORT DIRECTIVES
//==============================================================================

/// \brief Marks a symbol as being externally visible on UNIX platforms
///
/// \warning This macro is only required in special cases. One of those cases
///          is when manually exported templates must be declared as externally
///          visible for the compiler to instantiate them.
#if AMINO_INTERNAL_COMPILER_IS_GCC || AMINO_INTERNAL_COMPILER_IS_CLANG
#define AMINO_INTERNAL_EXPORT_UNIX __attribute__((visibility("default")))
#else
#define AMINO_INTERNAL_EXPORT_UNIX
#endif

//------------------------------------------------------------------------------
//
/// \def AMINO_INTERNAL_ASSERT_CODE(CODE)
/// \def AMINO_INTERNAL_ASSERT_BLOCK(CODE)
///
/// \brief Used to have code only in builds with assertions enabled.
#ifndef NDEBUG
#define AMINO_INTERNAL_ASSERT_CODE(CODE) CODE
#define AMINO_INTERNAL_ASSERT_BLOCK(CODE) CODE static_assert(true, "Need ;")
#else
#define AMINO_INTERNAL_ASSERT_CODE(CODE)
#define AMINO_INTERNAL_ASSERT_BLOCK(CODE) static_assert(true, "Need ;")
#endif

//------------------------------------------------------------------------------
//
/// \brief Force function inlining
///
/// This macro provides a hint to the compiler that a function must be inlined.
/// Please refer to your compiler's documentation for additional information
/// regarding how "force inline" behave for your compiler.
#if AMINO_INTERNAL_COMPILER_IS_MSC || AMINO_INTERNAL_COMPILER_IS_INTEL
#define AMINO_INTERNAL_FORCEINLINE __forceinline
#elif AMINO_INTERNAL_COMPILER_IS_GCC || AMINO_INTERNAL_COMPILER_IS_CLANG
#define AMINO_INTERNAL_FORCEINLINE inline __attribute__((always_inline))
#endif

#endif
/// \endcond

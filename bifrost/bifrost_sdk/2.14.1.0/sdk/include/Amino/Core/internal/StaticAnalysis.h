//-
// =============================================================================
// Copyright 2023 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

#ifndef AMINO_INTERNAL_STATIC_ANALYSIS_H
#define AMINO_INTERNAL_STATIC_ANALYSIS_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  StaticAnalysis.h
/// \brief Helper function to escape variable from clang static analysis.
///        Useful to silence clang-tidy "Potential Leak" false positives. Should
///        be used very sparingly, and annotations should be preferred when
///        possible.

namespace Amino {
namespace Internal {

//==============================================================================
// FUNCTION escapeFromClangStaticAnalysis
//==============================================================================

/// \brief Escape a variable from the analysis of the clang static analyzer
///
/// This function takes a reference to a variable as an argument. This causes
/// the static analyzer tool to notice that the variable has escape the scope of
/// its analysis. It forces the static analyzer to make very conservative
/// assumptions about the state of the variable. This also includes assumptions
/// about any memory location referenced by this variable.
///
/// This can be used to silence up false positives. In general, it is better to
/// augment the information available to the static analyzer using attributes
/// and/or assertions. Unfortunately, this isn't always possible. For example,
/// it might be impossible to describe that a given object is destructed along
/// all execution paths.
///
/// \warning Prefer using other means of providing enough information to the
/// static analyzer. The extra information can provided as attributes and/or
/// assertions describing assumptions and/or invariants. These are facts that
/// the static analyzer can assume to be true. They will allow the static
/// analyzer to prove that the faulty condition can't occur. See:
/// http://clang-analyzer.llvm.org/annotations.html.
///
/// \warning This function is never defined anywhere, so it will cause a link
/// error if you try to produce an executable.
///
/// \{
#ifdef __clang_analyzer__
void escapeFromClangStaticAnalysisImp(void* x);
template <typename V>
void escapeFromClangStaticAnalysis(V& escapedVar) {
    escapeFromClangStaticAnalysisImp(&escapedVar);
}
#else
template <typename V>
void escapeFromClangStaticAnalysis(V&) {}
#endif
/// \}

} // namespace Internal
} // namespace Amino
/// \endcond

#endif

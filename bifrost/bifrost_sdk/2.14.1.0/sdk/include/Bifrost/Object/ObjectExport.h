//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

//
/// \file Bifrost/Object/ObjectExport.h
///
/// \brief Definition of macros for symbol visibility.
///

#ifndef OBJECT_EXPORT_H
#define OBJECT_EXPORT_H

#if defined(_WIN32)
#define OBJECT_EXPORT __declspec(dllexport)
#define OBJECT_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define OBJECT_EXPORT __attribute__ ((visibility("default")))
#define OBJECT_IMPORT __attribute__ ((visibility("default")))
#else
#define OBJECT_EXPORT
#define OBJECT_IMPORT
#endif

#if defined(OBJECT_BUILD_DLL)
#define OBJECT_DECL OBJECT_EXPORT
#else
#define OBJECT_DECL OBJECT_IMPORT
#endif

#ifndef BIFMETADOC
#define BIFMETADOC( fDoc ) "{documentation, \\../docs/\\$\\{language\\}/" fDoc "}"
#endif

#ifndef BIFMETAICN
#define BIFMETAICN( fIcn ) "{icon, \\../icons/" fIcn ".svg}"
#endif

#ifndef BIFMETA_DISPLAY_VALUE
#define BIFMETA_DISPLAY_VALUE( value ) "{NodeValueDisplay, {format," value "}}"
#endif

#endif

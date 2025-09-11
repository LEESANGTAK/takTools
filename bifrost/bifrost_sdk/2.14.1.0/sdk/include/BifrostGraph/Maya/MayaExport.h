//-
//**************************************************************************/
// Copyright 2022 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk
// license agreement provided at the time of installation or download,
// or which otherwise accompanies this software in either electronic
// or hard copy form.
//**************************************************************************/
//+

#ifndef MAYA_HOST_DATA_DECL
#define MAYA_HOST_DATA_DECL

#ifdef _WIN32
    #ifdef MAYA_HOST_DATA_BUILD_DLL
        #define MAYA_HOST_DATA_SHARED_DECL __declspec(dllexport)
    #else
        #define MAYA_HOST_DATA_SHARED_DECL __declspec(dllimport)
    #endif
#elif defined(__GNUC__)
    #define MAYA_HOST_DATA_SHARED_DECL __attribute__((visibility("default")))
#else
    #define MAYA_HOST_DATA_SHARED_DECL
#endif

#endif

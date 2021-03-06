#ifndef __PYX_HAVE__unwarp
#define __PYX_HAVE__unwarp


#ifndef __PYX_HAVE_API__unwarp

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

#ifndef DL_IMPORT
  #define DL_IMPORT(_T) _T
#endif

__PYX_EXTERN_C DL_IMPORT(void) pydebug(char *);
__PYX_EXTERN_C DL_IMPORT(void) pyinfo(char *);
__PYX_EXTERN_C DL_IMPORT(void) pyuser(char *);

#endif /* !__PYX_HAVE_API__unwarp */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initunwarp(void);
#else
PyMODINIT_FUNC PyInit_unwarp(void);
#endif

#endif /* !__PYX_HAVE__unwarp */

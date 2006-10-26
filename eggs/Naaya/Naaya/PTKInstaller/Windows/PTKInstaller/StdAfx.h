// stdafx.h : include file for standard system include files,
//  or project specific include files that are used frequently, but
//      are changed infrequently
//

#if !defined(AFX_STDAFX_H__D407E3D0_5C18_42A3_978B_EFBAB8367AF0__INCLUDED_)
#define AFX_STDAFX_H__D407E3D0_5C18_42A3_978B_EFBAB8367AF0__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#define VC_EXTRALEAN		// Exclude rarely-used stuff from Windows headers

#include <afxwin.h>         // MFC core and standard components
#include <afxext.h>         // MFC extensions
#include <afxdisp.h>        // MFC Automation classes
#include <afxdtctl.h>		// MFC support for Internet Explorer 4 Common Controls
#include <Winsvc.h>
#include <afxtempl.h>
#ifndef _AFX_NO_AFXCMN_SUPPORT
#include <afxcmn.h>			// MFC support for Windows Common Controls
#endif // _AFX_NO_AFXCMN_SUPPORT


class CRString : public CString
{
public:
	CRString(int nID); //a resource ID to load the string from
	~CRString();
};

struct sItemData  
{
	CString strServiceName;
	CString strDisplayName;
	CString strDescription;
	DWORD nStatus;
	DWORD nStartupType;
	CString strLogOnAs;
	CString strBinaryPath;
	DWORD dwControlsAccepted;
};
typedef sItemData ITEMDATA;
typedef ITEMDATA* LPITEMDATA;

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_STDAFX_H__D407E3D0_5C18_42A3_978B_EFBAB8367AF0__INCLUDED_)

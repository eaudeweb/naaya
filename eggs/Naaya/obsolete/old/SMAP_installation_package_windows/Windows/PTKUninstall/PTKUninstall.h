// PTKUninstall.h : main header file for the PTKUNINSTALL application
//

#if !defined(AFX_PTKUNINSTALL_H__CA8BD3B3_BDDD_442A_9FC7_4665696348F4__INCLUDED_)
#define AFX_PTKUNINSTALL_H__CA8BD3B3_BDDD_442A_9FC7_4665696348F4__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

#define UWM_ARE_YOU_ME_MSG _T("UWM_ARE_YOU_ME-{CD52C52B-FC94-444c-AC25-E399F9C36985}")
#define DECLARE_USER_MESSAGE(name) \
     static const UINT name = ::RegisterWindowMessage(name##_MSG);

DECLARE_USER_MESSAGE(UWM_ARE_YOU_ME)

/////////////////////////////////////////////////////////////////////////////
// CPTKUninstallApp:
// See PTKUninstall.cpp for the implementation of this class
//

class CPTKUninstallApp : public CWinApp
{
public:
	CPTKUninstallApp();

	static BOOL CALLBACK searcher(HWND hWnd, LPARAM lParam);
// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPTKUninstallApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CPTKUninstallApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_PTKUNINSTALL_H__CA8BD3B3_BDDD_442A_9FC7_4665696348F4__INCLUDED_)

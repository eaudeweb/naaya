// CHM2Console.h : main header file for the CHM2CONSOLE application
//

#if !defined(AFX_CHM2CONSOLE_H__B34035A1_D7F5_4C1C_A2B9_B7BF9B3BC198__INCLUDED_)
#define AFX_CHM2CONSOLE_H__B34035A1_D7F5_4C1C_A2B9_B7BF9B3BC198__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

#define UWM_ARE_YOU_ME_MSG _T("UWM_ARE_YOU_ME-{5B73EEF2-B756-48dc-822C-EAF06813A8E2}")
#define DECLARE_USER_MESSAGE(name) \
     static const UINT name = ::RegisterWindowMessage(name##_MSG);

DECLARE_USER_MESSAGE(UWM_ARE_YOU_ME)

/////////////////////////////////////////////////////////////////////////////
// CCHM2ConsoleApp:
// See CHM2Console.cpp for the implementation of this class
//

class CCHM2ConsoleApp : public CWinApp
{
public:
	CCHM2ConsoleApp();

	static BOOL CALLBACK searcher(HWND hWnd, LPARAM lParam);
// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CCHM2ConsoleApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CCHM2ConsoleApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CHM2CONSOLE_H__B34035A1_D7F5_4C1C_A2B9_B7BF9B3BC198__INCLUDED_)

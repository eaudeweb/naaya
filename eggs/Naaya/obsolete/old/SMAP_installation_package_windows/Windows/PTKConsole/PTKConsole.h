// PTKConsole.h : main header file for the PTKCONSOLE application
//

#if !defined(AFX_PTKCONSOLE_H__889CFA6C_0F80_4637_8BEA_F0201DA5548E__INCLUDED_)
#define AFX_PTKCONSOLE_H__889CFA6C_0F80_4637_8BEA_F0201DA5548E__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

#define UWM_ARE_YOU_ME_MSG _T("UWM_ARE_YOU_ME-{641B03D3-8648-4343-82E2-57D94681D600}")
#define DECLARE_USER_MESSAGE(name) \
     static const UINT name = ::RegisterWindowMessage(name##_MSG);

DECLARE_USER_MESSAGE(UWM_ARE_YOU_ME)

/////////////////////////////////////////////////////////////////////////////
// CPTKConsoleApp:
// See PTKConsole.cpp for the implementation of this class
//

class CPTKConsoleApp : public CWinApp
{
public:
	CPTKConsoleApp();

	static BOOL CALLBACK searcher(HWND hWnd, LPARAM lParam);
// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPTKConsoleApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CPTKConsoleApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_PTKCONSOLE_H__889CFA6C_0F80_4637_8BEA_F0201DA5548E__INCLUDED_)

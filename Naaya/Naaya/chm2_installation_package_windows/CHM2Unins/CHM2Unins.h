// CHM2Unins.h : main header file for the CHM2UNINS application
//

#if !defined(AFX_CHM2UNINS_H__68045569_7AB8_48BE_9659_6FF8496C4CA8__INCLUDED_)
#define AFX_CHM2UNINS_H__68045569_7AB8_48BE_9659_6FF8496C4CA8__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

#define UWM_ARE_YOU_ME_MSG _T("UWM_ARE_YOU_ME-{D86CE623-A660-4a06-B090-981F86EB4000}")
#define DECLARE_USER_MESSAGE(name) \
     static const UINT name = ::RegisterWindowMessage(name##_MSG);

DECLARE_USER_MESSAGE(UWM_ARE_YOU_ME)

/////////////////////////////////////////////////////////////////////////////
// CCHM2UninsApp:
// See CHM2Unins.cpp for the implementation of this class
//

class CCHM2UninsApp : public CWinApp
{
public:
	CCHM2UninsApp();

	static BOOL CALLBACK searcher(HWND hWnd, LPARAM lParam);
// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CCHM2UninsApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CCHM2UninsApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CHM2UNINS_H__68045569_7AB8_48BE_9659_6FF8496C4CA8__INCLUDED_)

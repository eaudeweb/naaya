// CHM2.h : main header file for the CHM2 application
//

#if !defined(AFX_CHM2_H__496AF6A2_535A_4908_B68C_EA094E71FBEE__INCLUDED_)
#define AFX_CHM2_H__496AF6A2_535A_4908_B68C_EA094E71FBEE__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CCHM2App:
// See CHM2.cpp for the implementation of this class
//

class CCHM2App : public CWinApp
{
public:
	CCHM2App();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CCHM2App)
	public:
	virtual BOOL InitInstance();
	virtual int ExitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CCHM2App)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
private:
	BOOL CanRunInstaller(CString& strError);
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CHM2_H__496AF6A2_535A_4908_B68C_EA094E71FBEE__INCLUDED_)

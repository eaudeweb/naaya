// PTKInstaller.h : main header file for the PTKINSTALLER application
//

#if !defined(AFX_PTKINSTALLER_H__3FFFA2E7_880A_4EA5_A242_CBB6F02F5B26__INCLUDED_)
#define AFX_PTKINSTALLER_H__3FFFA2E7_880A_4EA5_A242_CBB6F02F5B26__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CPTKInstallerApp:
// See PTKInstaller.cpp for the implementation of this class
//

class CPTKInstallerApp : public CWinApp
{
public:
	CPTKInstallerApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPTKInstallerApp)
	public:
	virtual BOOL InitInstance();
	virtual int ExitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CPTKInstallerApp)
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

#endif // !defined(AFX_PTKINSTALLER_H__3FFFA2E7_880A_4EA5_A242_CBB6F02F5B26__INCLUDED_)

#if !defined(AFX_INSTALLPAGE_H__67C87480_7FC0_48C1_9497_5F6AA7CCE7CA__INCLUDED_)
#define AFX_INSTALLPAGE_H__67C87480_7FC0_48C1_9497_5F6AA7CCE7CA__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// InstallPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CInstallPage dialog

class CInstallPage : public CNewWizPage
{
// Construction
public:
	CInstallPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CInstallPage)
	enum { IDD = IDW_INSTALL };
	CButton	m_chkStart;
	CStatic	m_InstallInfoText;
	CStatic	m_InstallationText;
	CProgressCtrl	m_InstallationProgessText;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CInstallPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
public:
    BOOL StartInstallation(CString);
    BOOL StartProgram(CString, CString, CString, CStringArray&, int = SW_SHOWNORMAL);
    
    //installation
    BOOL CopyNecessaryFiles(CStringArray&);
    BOOL ModifyConfigurationFiles(CStringArray&);
	BOOL RunScripts(CStringArray&);
	BOOL CleanUp(CStringArray&);
    BOOL CreateShortcuts(CStringArray&);
	void UpdateRegistryEnvironment(CStringArray&);
protected:
	BOOL OnWizardFinish();

	// Generated message map functions
	//{{AFX_MSG(CInstallPage)
	virtual BOOL OnInitDialog();
	afx_msg void OnTimer(UINT nIDEvent);
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_INSTALLPAGE_H__67C87480_7FC0_48C1_9497_5F6AA7CCE7CA__INCLUDED_)

// PTKInstallerDlg.h : header file
//

#if !defined(AFX_PTKINSTALLERDLG_H__4B687947_091E_4FD4_8DBB_3F8559A4D47B__INCLUDED_)
#define AFX_PTKINSTALLERDLG_H__4B687947_091E_4FD4_8DBB_3F8559A4D47B__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "NewWizDialog.h"
#include "WizardData.h"
#include "ServiceManager.h"

/////////////////////////////////////////////////////////////////////////////
// CPTKInstallerDlg dialog

class CPTKInstallerDlg : public CNewWizDialog
{
// Construction
public:
	CFont m_fontTitle;
	CWizardData* m_pWizardData;
	CServiceManager* m_pServiceManager;
	CPTKInstallerDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CPTKInstallerDlg)
	enum { IDD = IDD_PTKINSTALLER_DIALOG };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPTKInstallerDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CPTKInstallerDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_PTKINSTALLERDLG_H__4B687947_091E_4FD4_8DBB_3F8559A4D47B__INCLUDED_)

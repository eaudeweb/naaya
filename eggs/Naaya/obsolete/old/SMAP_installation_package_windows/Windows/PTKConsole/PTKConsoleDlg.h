// PTKConsoleDlg.h : header file
//

#if !defined(AFX_PTKCONSOLEDLG_H__627832CE_6318_4167_97D0_C50F2BF3B9C9__INCLUDED_)
#define AFX_PTKCONSOLEDLG_H__627832CE_6318_4167_97D0_C50F2BF3B9C9__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "ConsoleTabCtrl.h"
#include "ServiceManager.h"

/////////////////////////////////////////////////////////////////////////////
// CPTKConsoleDlg dialog

class CPTKConsoleDlg : public CDialog
{
// Construction
public:
	CServiceManager* m_pServiceManager;

	CPTKConsoleDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CPTKConsoleDlg)
	enum { IDD = IDD_PTKCONSOLE_DIALOG };
	CConsoleTabCtrl	m_tabConsoleTabCtrl;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPTKConsoleDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;
	CBrush m_Brush; // brush for white background
	CFont m_fontTitle;	// font for dialog title

	// Generated message map functions
	//{{AFX_MSG(CPTKConsoleDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg HBRUSH OnCtlColor(CDC* pDC, CWnd* pWnd, UINT nCtlColor);
	afx_msg LRESULT OnAreYouMe(WPARAM, LPARAM);
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_PTKCONSOLEDLG_H__627832CE_6318_4167_97D0_C50F2BF3B9C9__INCLUDED_)

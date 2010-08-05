// CHM2ConsoleDlg.h : header file
//

#if !defined(AFX_CHM2CONSOLEDLG_H__BDB88F3E_20E0_4B3D_900E_8ABE7A9532D8__INCLUDED_)
#define AFX_CHM2CONSOLEDLG_H__BDB88F3E_20E0_4B3D_900E_8ABE7A9532D8__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "CHM2TabCtrl.h"
#include "ServiceManager.h"

/////////////////////////////////////////////////////////////////////////////
// CCHM2ConsoleDlg dialog

class CCHM2ConsoleDlg : public CDialog
{
// Construction
public:
	CServiceManager* m_pServiceManager;

	CCHM2ConsoleDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CCHM2ConsoleDlg)
	enum { IDD = IDD_CHM2CONSOLE_DIALOG };
	CCHM2TabCtrl	m_tabCHM2TabCtrl;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CCHM2ConsoleDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;
	CBrush m_Brush; // brush for white background
	CFont m_fontTitle;	// font for dialog title

	// Generated message map functions
	//{{AFX_MSG(CCHM2ConsoleDlg)
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

#endif // !defined(AFX_CHM2CONSOLEDLG_H__BDB88F3E_20E0_4B3D_900E_8ABE7A9532D8__INCLUDED_)

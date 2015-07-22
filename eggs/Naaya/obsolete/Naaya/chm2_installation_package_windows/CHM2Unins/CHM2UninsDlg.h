// CHM2UninsDlg.h : header file
//

#if !defined(AFX_CHM2UNINSDLG_H__09F7D271_7592_435F_B486_A8C47572C4F8__INCLUDED_)
#define AFX_CHM2UNINSDLG_H__09F7D271_7592_435F_B486_A8C47572C4F8__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

/////////////////////////////////////////////////////////////////////////////
// CCHM2UninsDlg dialog

class CCHM2UninsDlg : public CDialog
{
// Construction
public:
	CCHM2UninsDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CCHM2UninsDlg)
	enum { IDD = IDD_CHM2UNINS_DIALOG };
	CEdit	m_edtSummary;
	CProgressCtrl	m_prgUninstall;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CCHM2UninsDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;
	CBrush m_Brush; // brush for white background
	CFont m_fontTitle;	// font for dialog title

	BOOL m_bUninstallOK;

	CString m_strApplicationPath;
	CString m_strZopePath;
	CString m_strInstancePath;
	CString m_strBinPath;
	CString m_strBackupPath;

	CString m_strStartMenuFolderPath;

	CString m_strRegApplicationKey;

	// Generated message map functions
	//{{AFX_MSG(CCHM2UninsDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	virtual void OnOK();
	virtual void OnCancel();
	afx_msg HBRUSH OnCtlColor(CDC* pDC, CWnd* pWnd, UINT nCtlColor);
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
public:
	void UpdateSummary(CString strText);
	BOOL StopUninstallServices(CString& strError);
	BOOL DeleteShortcuts(CString& strError);
	BOOL BackupFiles(CString& strError);
	BOOL DeleteNecessaryFiles(CString& strError);
	BOOL DeleteRegistry(CString& strError);
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CHM2UNINSDLG_H__09F7D271_7592_435F_B486_A8C47572C4F8__INCLUDED_)

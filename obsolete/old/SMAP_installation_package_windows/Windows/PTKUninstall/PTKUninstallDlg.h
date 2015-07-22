// PTKUninstallDlg.h : header file
//

#if !defined(AFX_PTKUNINSTALLDLG_H__DD875020_2910_45E2_9770_596319FB6193__INCLUDED_)
#define AFX_PTKUNINSTALLDLG_H__DD875020_2910_45E2_9770_596319FB6193__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

/////////////////////////////////////////////////////////////////////////////
// CPTKUninstallDlg dialog

class CPTKUninstallDlg : public CDialog
{
// Construction
public:
	CPTKUninstallDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CPTKUninstallDlg)
	enum { IDD = IDD_PTKUNINSTALL_DIALOG };
	CEdit	m_edtSummary;
	CProgressCtrl	m_prgUninstall;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPTKUninstallDlg)
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
	//{{AFX_MSG(CPTKUninstallDlg)
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

#endif // !defined(AFX_PTKUNINSTALLDLG_H__DD875020_2910_45E2_9770_596319FB6193__INCLUDED_)

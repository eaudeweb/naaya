#if !defined(AFX_ZEUDLG_H__A9285B65_FCB0_4BF6_A0CC_520288EA8B40__INCLUDED_)
#define AFX_ZEUDLG_H__A9285B65_FCB0_4BF6_A0CC_520288EA8B40__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// ZEUDlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CZEUDlg dialog

class CZEUDlg : public CDialog
{
// Construction
public:
	CZEUDlg(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CZEUDlg)
	enum { IDD = IDD_ZEU_DIALOG };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CZEUDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CZEUDlg)
	virtual BOOL OnInitDialog();
	virtual void OnOK();
	afx_msg void OnDeleteZEU();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
private:
	CString m_strInstancePath;
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ZEUDLG_H__A9285B65_FCB0_4BF6_A0CC_520288EA8B40__INCLUDED_)

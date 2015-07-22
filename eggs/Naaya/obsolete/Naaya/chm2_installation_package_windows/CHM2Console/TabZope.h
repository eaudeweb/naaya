#if !defined(AFX_TABZOPE_H__BBFE3762_6BA2_47B9_A851_7CA995BAFF8A__INCLUDED_)
#define AFX_TABZOPE_H__BBFE3762_6BA2_47B9_A851_7CA995BAFF8A__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// TabZope.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CTabZope dialog

class CTabZope : public CDialog
{
// Construction
public:
	CTabZope(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CTabZope)
	enum { IDD = IDD_TAB_ZOPE };
	CButton	m_btnApply;
	CComboBox	m_cbxStartType;
	CEdit	m_edtPath;
	CStatic	m_stcName;
	CStatic	m_stcDisplay;
	CButton	m_btnStart;
	CButton	m_btnStop;
	CStatic	m_stcStatus;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CTabZope)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	ITEMDATA m_itemData;
	void GetServiceData();
	void SetCurSelStartupType();

	// Generated message map functions
	//{{AFX_MSG(CTabZope)
	virtual void OnOK();
	virtual void OnCancel();
	virtual BOOL OnInitDialog();
	afx_msg void OnTimer(UINT nIDEvent);
	afx_msg void OnShowWindow(BOOL bShow, UINT nStatus);
	afx_msg void OnSelchangeStarttypeCombo();
	afx_msg void OnApplyButton();
	afx_msg void OnEmergencyUser();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_TABZOPE_H__BBFE3762_6BA2_47B9_A851_7CA995BAFF8A__INCLUDED_)

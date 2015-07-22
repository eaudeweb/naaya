#if !defined(AFX_INSTALLPATHPAGE_H__D5EF8E96_C7DF_43CE_88CF_5984CEB35E23__INCLUDED_)
#define AFX_INSTALLPATHPAGE_H__D5EF8E96_C7DF_43CE_88CF_5984CEB35E23__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// InstallPathPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CInstallPathPage dialog

class CInstallPathPage : public CNewWizPage
{
// Construction
public:
	CInstallPathPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CInstallPathPage)
	enum { IDD = IDW_INSTALLPATH };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CInstallPathPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
private:
	unsigned __int64 m_n64Available;
	void SetTexts(CString);
protected:
	void OnOK();
	LRESULT OnWizardNext();

	// Generated message map functions
	//{{AFX_MSG(CInstallPathPage)
	virtual BOOL OnInitDialog();
	afx_msg void OnInstallpathBrowseButton();
	afx_msg void OnKillfocusInstallpathPathEdit();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_INSTALLPATHPAGE_H__D5EF8E96_C7DF_43CE_88CF_5984CEB35E23__INCLUDED_)

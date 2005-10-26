#if !defined(AFX_INSTALLPATHPAGE_H__FF267087_6F08_47EB_86D8_D8E8F160B413__INCLUDED_)
#define AFX_INSTALLPATHPAGE_H__FF267087_6F08_47EB_86D8_D8E8F160B413__INCLUDED_

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
	afx_msg void OnInstallpathBrowseButton();
	virtual BOOL OnInitDialog();
	afx_msg void OnKillfocusInstallpathPathEdit();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_INSTALLPATHPAGE_H__FF267087_6F08_47EB_86D8_D8E8F160B413__INCLUDED_)

#if !defined(AFX_PARAMETERSPAGE_H__EC40CF0B_B68C_41F9_96F3_675913EF51A0__INCLUDED_)
#define AFX_PARAMETERSPAGE_H__EC40CF0B_B68C_41F9_96F3_675913EF51A0__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// ParametersPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CParametersPage dialog

class CParametersPage : public CNewWizPage
{
// Construction
public:
	CParametersPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CParametersPage)
	enum { IDD = IDW_PARAMETERS };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CParametersPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnOK();
	LRESULT OnWizardNext();

	// Generated message map functions
	//{{AFX_MSG(CParametersPage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_PARAMETERSPAGE_H__EC40CF0B_B68C_41F9_96F3_675913EF51A0__INCLUDED_)

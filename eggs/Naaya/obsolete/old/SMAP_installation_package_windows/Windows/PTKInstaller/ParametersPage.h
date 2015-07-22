#if !defined(AFX_PARAMETERS_H__F2F93F78_15D2_4C4D_A910_AA296B0F401B__INCLUDED_)
#define AFX_PARAMETERS_H__F2F93F78_15D2_4C4D_A910_AA296B0F401B__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// Parameters.h : header file
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
	//{{AFX_VIRTUAL(CParameters)
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

#endif // !defined(AFX_PARAMETERS_H__F2F93F78_15D2_4C4D_A910_AA296B0F401B__INCLUDED_)

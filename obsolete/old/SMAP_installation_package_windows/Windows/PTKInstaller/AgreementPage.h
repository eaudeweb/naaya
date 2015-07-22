#if !defined(AFX_AGREEMENTPAGE_H__F65CED0D_77E3_4EE2_9941_9A21D572A3DF__INCLUDED_)
#define AFX_AGREEMENTPAGE_H__F65CED0D_77E3_4EE2_9941_9A21D572A3DF__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// AgreementPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CAgreementPage dialog

class CAgreementPage : public CNewWizPage
{
// Construction
public:
	CAgreementPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CAgreementPage)
	enum { IDD = IDW_AGREEMENT };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAgreementPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnOK();
	LRESULT OnWizardNext();

	// Generated message map functions
	//{{AFX_MSG(CAgreementPage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_AGREEMENTPAGE_H__F65CED0D_77E3_4EE2_9941_9A21D572A3DF__INCLUDED_)

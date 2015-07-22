#if !defined(AFX_FINISHPAGE_H__E451E169_AD94_4FD8_97AF_C92AFABDD9FE__INCLUDED_)
#define AFX_FINISHPAGE_H__E451E169_AD94_4FD8_97AF_C92AFABDD9FE__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// FinishPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CFinishPage dialog

class CFinishPage : public CNewWizPage
{
// Construction
public:
	CFinishPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CFinishPage)
	enum { IDD = IDW_FINISH };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CFinishPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnSetActive();
	void OnOK();

	// Generated message map functions
	//{{AFX_MSG(CFinishPage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_FINISHPAGE_H__E451E169_AD94_4FD8_97AF_C92AFABDD9FE__INCLUDED_)

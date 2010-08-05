#if !defined(AFX_WELCOMEPAGE_H__5B51FC48_BC03_46C2_A80A_9ADAA1BFB997__INCLUDED_)
#define AFX_WELCOMEPAGE_H__5B51FC48_BC03_46C2_A80A_9ADAA1BFB997__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// WelcomePage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CWelcomePage dialog

class CWelcomePage : public CNewWizPage
{
// Construction
public:
	CWelcomePage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CWelcomePage)
	enum { IDD = IDW_WELCOME };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CWelcomePage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnOK();

	// Generated message map functions
	//{{AFX_MSG(CWelcomePage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_WELCOMEPAGE_H__5B51FC48_BC03_46C2_A80A_9ADAA1BFB997__INCLUDED_)

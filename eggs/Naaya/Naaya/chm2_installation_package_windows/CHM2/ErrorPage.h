#if !defined(AFX_ERRORPAGE_H__0C7517D2_8B24_4D83_A317_EE52DC1ED688__INCLUDED_)
#define AFX_ERRORPAGE_H__0C7517D2_8B24_4D83_A317_EE52DC1ED688__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// ErrorPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CErrorPage dialog

class CErrorPage : public CNewWizPage
{
// Construction
public:
	CString m_strError;
	CErrorPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CErrorPage)
	enum { IDD = IDW_ERROR };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CErrorPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CErrorPage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ERRORPAGE_H__0C7517D2_8B24_4D83_A317_EE52DC1ED688__INCLUDED_)

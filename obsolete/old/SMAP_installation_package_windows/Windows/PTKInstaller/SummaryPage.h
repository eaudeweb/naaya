#if !defined(AFX_SUMMARYPAGE_H__C47F8443_B236_48FF_8FC6_1837E70CF2F0__INCLUDED_)
#define AFX_SUMMARYPAGE_H__C47F8443_B236_48FF_8FC6_1837E70CF2F0__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// SummaryPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CSummaryPage dialog

class CSummaryPage : public CNewWizPage
{
// Construction
public:
	CSummaryPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CSummaryPage)
	enum { IDD = IDW_SUMMARY };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CSummaryPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnSetActive();
	void OnOK();

	// Generated message map functions
	//{{AFX_MSG(CSummaryPage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_SUMMARYPAGE_H__C47F8443_B236_48FF_8FC6_1837E70CF2F0__INCLUDED_)

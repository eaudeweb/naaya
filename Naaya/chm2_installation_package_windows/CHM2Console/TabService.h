#if !defined(AFX_TABSERVICE_H__BFA47D2E_131E_41EB_9A72_860D67E7EB37__INCLUDED_)
#define AFX_TABSERVICE_H__BFA47D2E_131E_41EB_9A72_860D67E7EB37__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// TabService.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CTabService dialog

class CTabService : public CDialog
{
// Construction
public:
	CTabService(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CTabService)
	enum { IDD = IDD_TAB_SERVICE };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CTabService)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CTabService)
		// NOTE: the ClassWizard will add member functions here
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_TABSERVICE_H__BFA47D2E_131E_41EB_9A72_860D67E7EB37__INCLUDED_)

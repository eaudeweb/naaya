#if !defined(AFX_TABSERVICE_H__528DEEB1_9F17_4B77_94AE_72CDCC6DEBC2__INCLUDED_)
#define AFX_TABSERVICE_H__528DEEB1_9F17_4B77_94AE_72CDCC6DEBC2__INCLUDED_

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

#endif // !defined(AFX_TABSERVICE_H__528DEEB1_9F17_4B77_94AE_72CDCC6DEBC2__INCLUDED_)

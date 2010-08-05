#if !defined(AFX_TABABOUT_H__7713A481_7E91_4333_8B86_B7821E0A83BF__INCLUDED_)
#define AFX_TABABOUT_H__7713A481_7E91_4333_8B86_B7821E0A83BF__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// TabAbout.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CTabAbout dialog

class CTabAbout : public CDialog
{
// Construction
public:
	CTabAbout(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CTabAbout)
	enum { IDD = IDD_TAB_ABOUT };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CTabAbout)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CTabAbout)
		// NOTE: the ClassWizard will add member functions here
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_TABABOUT_H__7713A481_7E91_4333_8B86_B7821E0A83BF__INCLUDED_)

#if !defined(AFX_CONSOLETABCTRL_H__266173E9_5A91_453E_AE7E_BB27E937A1AD__INCLUDED_)
#define AFX_CONSOLETABCTRL_H__266173E9_5A91_453E_AE7E_BB27E937A1AD__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// ConsoleTabCtrl.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CConsoleTabCtrl window

class CConsoleTabCtrl : public CTabCtrl
{
// Construction
public:
	CConsoleTabCtrl();

	CDialog *m_tabPages[3];
	int m_tabCurrent;
	int m_nNumberOfPages;

// Attributes
public:

// Operations
public:
	void Init();
	void SetRectangle();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CConsoleTabCtrl)
	//}}AFX_VIRTUAL

// Implementation
public:
	virtual ~CConsoleTabCtrl();

	// Generated message map functions
protected:
	//{{AFX_MSG(CConsoleTabCtrl)
	afx_msg void OnLButtonDown(UINT nFlags, CPoint point);
	//}}AFX_MSG

	DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CONSOLETABCTRL_H__266173E9_5A91_453E_AE7E_BB27E937A1AD__INCLUDED_)

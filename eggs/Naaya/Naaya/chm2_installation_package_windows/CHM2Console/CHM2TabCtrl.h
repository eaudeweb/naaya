#if !defined(AFX_CHM2TABCTRL_H__9961AF80_6985_42F5_8291_722C74203F69__INCLUDED_)
#define AFX_CHM2TABCTRL_H__9961AF80_6985_42F5_8291_722C74203F69__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// CHM2TabCtrl.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CCHM2TabCtrl window

class CCHM2TabCtrl : public CTabCtrl
{
// Construction
public:
	CCHM2TabCtrl();

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
	//{{AFX_VIRTUAL(CCHM2TabCtrl)
	//}}AFX_VIRTUAL

// Implementation
public:
	virtual ~CCHM2TabCtrl();

	// Generated message map functions
protected:
	//{{AFX_MSG(CCHM2TabCtrl)
	afx_msg void OnLButtonDown(UINT nFlags, CPoint point);
	//}}AFX_MSG

	DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CHM2TABCTRL_H__9961AF80_6985_42F5_8291_722C74203F69__INCLUDED_)

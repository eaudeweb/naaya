#if !defined(AFX_PORTALLOGOSPAGE_H__DAC32158_BB00_4116_AAC2_46B0A63EBC58__INCLUDED_)
#define AFX_PORTALLOGOSPAGE_H__DAC32158_BB00_4116_AAC2_46B0A63EBC58__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// PortalLogosPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CPortalLogosPage dialog

class CPortalLogosPage : public CNewWizPage
{
// Construction
public:
	CPortalLogosPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CPortalLogosPage)
	enum { IDD = IDW_PORTALLOGOS };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPortalLogosPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnOK();
	LRESULT OnWizardNext();

	// Generated message map functions
	//{{AFX_MSG(CPortalLogosPage)
	virtual BOOL OnInitDialog();
	afx_msg void OnLogoBrowseButton();
	afx_msg void OnLogobisBrowseButton();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_PORTALLOGOSPAGE_H__DAC32158_BB00_4116_AAC2_46B0A63EBC58__INCLUDED_)

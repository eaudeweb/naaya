#if !defined(AFX_PORTALADMINISTRATIVEPAGE_H__1A450D7C_2D34_44EF_B8EA_FB0FEB4FC021__INCLUDED_)
#define AFX_PORTALADMINISTRATIVEPAGE_H__1A450D7C_2D34_44EF_B8EA_FB0FEB4FC021__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// PortalAdministrativePage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CPortalAdministrativePage dialog

class CPortalAdministrativePage : public CNewWizPage
{
// Construction
public:
	CPortalAdministrativePage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CPortalAdministrativePage)
	enum { IDD = IDW_PORTALADMINISTRATIVE };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPortalAdministrativePage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnOK();
	LRESULT OnWizardNext();

	// Generated message map functions
	//{{AFX_MSG(CPortalAdministrativePage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_PORTALADMINISTRATIVEPAGE_H__1A450D7C_2D34_44EF_B8EA_FB0FEB4FC021__INCLUDED_)

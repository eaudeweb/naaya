#if !defined(AFX_ADMINISTRATIVEPAGE_H__D9D1BE12_2E8A_4FD2_88FC_98725D4064A5__INCLUDED_)
#define AFX_ADMINISTRATIVEPAGE_H__D9D1BE12_2E8A_4FD2_88FC_98725D4064A5__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// AdministrativePage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CAdministrativePage dialog

class CAdministrativePage : public CNewWizPage
{
// Construction
public:
	CAdministrativePage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CAdministrativePage)
	enum { IDD = IDW_ADMINISTRATIVE };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAdministrativePage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnOK();
	LRESULT OnWizardNext();

	// Generated message map functions
	//{{AFX_MSG(CAdministrativePage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ADMINISTRATIVEPAGE_H__D9D1BE12_2E8A_4FD2_88FC_98725D4064A5__INCLUDED_)

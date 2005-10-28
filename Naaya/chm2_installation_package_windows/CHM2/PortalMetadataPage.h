#if !defined(AFX_PORTALMETADATAPAGE_H__65E462B5_3926_48AD_87BA_58DEBE2C2E85__INCLUDED_)
#define AFX_PORTALMETADATAPAGE_H__65E462B5_3926_48AD_87BA_58DEBE2C2E85__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// PortalMetadataPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CPortalMetadataPage dialog

class CPortalMetadataPage : public CNewWizPage
{
// Construction
public:
	CPortalMetadataPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CPortalMetadataPage)
	enum { IDD = IDW_PORTALMETADATA };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPortalMetadataPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnOK();
	LRESULT OnWizardNext();

	// Generated message map functions
	//{{AFX_MSG(CPortalMetadataPage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_PORTALMETADATAPAGE_H__65E462B5_3926_48AD_87BA_58DEBE2C2E85__INCLUDED_)

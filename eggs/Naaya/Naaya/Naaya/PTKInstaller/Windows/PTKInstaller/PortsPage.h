#if !defined(AFX_PORTSPAGE_H__619D877B_7AC5_4DCF_BD58_DF1361C5BFEF__INCLUDED_)
#define AFX_PORTSPAGE_H__619D877B_7AC5_4DCF_BD58_DF1361C5BFEF__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// PortsPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CPortsPage dialog

class CPortsPage : public CNewWizPage
{
// Construction
public:
	CPortsPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CPortsPage)
	enum { IDD = IDW_PORTS };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CPortsPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnOK();
	LRESULT OnWizardNext();

	// Generated message map functions
	//{{AFX_MSG(CPortsPage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_PORTSPAGE_H__619D877B_7AC5_4DCF_BD58_DF1361C5BFEF__INCLUDED_)

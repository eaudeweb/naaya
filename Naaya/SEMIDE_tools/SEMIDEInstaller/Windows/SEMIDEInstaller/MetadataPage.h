#if !defined(AFX_METADATAPAGE_H__ED7C0443_A33F_4673_AAC0_9AE137507313__INCLUDED_)
#define AFX_METADATAPAGE_H__ED7C0443_A33F_4673_AAC0_9AE137507313__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// MetadataPage.h : header file
//

#include "NewWizPage.h"

/////////////////////////////////////////////////////////////////////////////
// CMetadataPage dialog

class CMetadataPage : public CNewWizPage
{
// Construction
public:
	CMetadataPage(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CMetadataPage)
	enum { IDD = IDW_METADATA };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMetadataPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	void OnOK();
	LRESULT OnWizardNext();

	// Generated message map functions
	//{{AFX_MSG(CMetadataPage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_METADATAPAGE_H__ED7C0443_A33F_4673_AAC0_9AE137507313__INCLUDED_)

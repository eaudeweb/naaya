// ErrorPage.cpp : implementation file
//

#include "stdafx.h"
#include "PTKInstaller.h"
#include "ErrorPage.h"
#include "PTKInstallerDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CErrorPage dialog


CErrorPage::CErrorPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CErrorPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CErrorPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CErrorPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CErrorPage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CErrorPage, CNewWizPage)
	//{{AFX_MSG_MAP(CErrorPage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CErrorPage message handlers

BOOL CErrorPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_ERROR_TITLE)->SetFont(&((CPTKInstallerDlg*)GetParent())->m_fontTitle, TRUE);
	GetDlgItem(IDC_ERROR_SUMMARY_EDIT)->SetWindowText(m_strError);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

// AgreementPage.cpp : implementation file
//

#include "stdafx.h"
#include "PTKInstaller.h"
#include "AgreementPage.h"
#include "PTKInstallerDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CAgreementPage dialog


CAgreementPage::CAgreementPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CAgreementPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CAgreementPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CAgreementPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAgreementPage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CAgreementPage, CNewWizPage)
	//{{AFX_MSG_MAP(CAgreementPage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CAgreementPage message handlers

BOOL CAgreementPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_AGREEMENT_TITLE)->SetFont(&((CPTKInstallerDlg*)GetParent())->m_fontTitle, TRUE);
	
	GetDlgItem(IDC_AGREEMENT_INFORMATION)->SetWindowText(CRString(IDS_AGREEMENT));

	CheckRadioButton(IDC_AGREEMENT_RB_ACCEPT, IDC_AGREEMENT_RB_DECLINE, IDC_AGREEMENT_RB_DECLINE);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CAgreementPage::OnOK()
{
	::SendMessage(((CPTKInstallerDlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

LRESULT CAgreementPage::OnWizardNext()
{
	if (IsDlgButtonChecked(IDC_AGREEMENT_RB_DECLINE))
	{
		AfxMessageBox(CRString(IDS_ACCEPT_AGREEMENT));
		return -1;
	}
	return 0;
}

// WelcomePage.cpp : implementation file
//

#include "stdafx.h"
#include "CHM2.h"
#include "WelcomePage.h"
#include "CHM2Dlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CWelcomePage dialog


CWelcomePage::CWelcomePage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CWelcomePage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CWelcomePage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CWelcomePage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CWelcomePage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CWelcomePage, CNewWizPage)
	//{{AFX_MSG_MAP(CWelcomePage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CWelcomePage message handlers

BOOL CWelcomePage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();

	GetDlgItem(IDC_WELCOME_TITLE)->SetFont(&((CCHM2Dlg*)GetParent())->m_fontTitle, TRUE);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CWelcomePage::OnOK()
{
	::SendMessage(((CCHM2Dlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

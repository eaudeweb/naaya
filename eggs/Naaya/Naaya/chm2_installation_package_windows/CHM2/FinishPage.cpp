// FinishPage.cpp : implementation file
//

#include "stdafx.h"
#include "CHM2.h"
#include "FinishPage.h"
#include "CHM2Dlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CFinishPage dialog


CFinishPage::CFinishPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CFinishPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CFinishPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CFinishPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CFinishPage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CFinishPage, CNewWizPage)
	//{{AFX_MSG_MAP(CFinishPage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CFinishPage message handlers

BOOL CFinishPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_FINISH_TITLE)->SetFont(&((CCHM2Dlg*)GetParent())->m_fontTitle, TRUE);

	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CFinishPage::OnSetActive()
{
    // set information
    CString strInformation;
    CString strBuffer;

	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;
    if (pWizardData->m_nRunAsService)
        strBuffer = CRString(IDS_RUN_SERVICE);
    else
        strBuffer = CRString(IDS_RUN_MANUAL);

	strInformation.Format(CRString(IDS_SUMMARY),
			pWizardData->m_strPath,
			pWizardData->m_strFullHostName,
			pWizardData->m_strHostIPAddress,
			pWizardData->m_strUsername,
			pWizardData->m_strAdministratorEmail,
			pWizardData->m_nZopeHTTPPort,
			pWizardData->m_nZopeFTPPort,
			pWizardData->m_nZopeWEBDAVPort,
			CRString(IDS_MENU_FOLDER_NAME),
			strBuffer);

	GetDlgItem(IDC_FINISH_SUMMARY_EDIT)->SetWindowText(strInformation);
}

void CFinishPage::OnOK()
{
	::SendMessage(((CCHM2Dlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

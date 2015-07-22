// SummaryPage.cpp : implementation file
//

#include "stdafx.h"
#include "ptkinstaller.h"
#include "SummaryPage.h"

#include "PTKInstallerDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CSummaryPage dialog


CSummaryPage::CSummaryPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CSummaryPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CSummaryPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CSummaryPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CSummaryPage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CSummaryPage, CNewWizPage)
	//{{AFX_MSG_MAP(CSummaryPage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CSummaryPage message handlers

BOOL CSummaryPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_SUMMARY_TITLE)->SetFont(&((CPTKInstallerDlg*)GetParent())->m_fontTitle, TRUE);

	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CSummaryPage::OnSetActive()
{
    // set information
    CString strInformation;
    CString strBuffer, strRunning, strLanguages;

	CWizardData* pWizardData = ((CPTKInstallerDlg*)GetParent())->m_pWizardData;
    if (pWizardData->m_nRunAsService)
        strRunning = CRString(IDS_RUN_SERVICE);
    else
        strRunning = CRString(IDS_RUN_MANUAL);

	for (int i=0; i<pWizardData->m_arrLanguagesSel.GetSize(); i++)
	{
		int x = pWizardData->m_arrLanguagesSel.GetAt(i);
		strBuffer.Format("%s [%s]",
			pWizardData->m_arrLanguagesNames.GetAt(x),
			pWizardData->m_arrLanguagesCodes.GetAt(x));
		strLanguages += strBuffer;
		if (i < pWizardData->m_arrLanguagesSel.GetSize()-1)
			strLanguages += ", ";
	}

	strInformation.Format(CRString(IDS_SUMMARY),
			pWizardData->m_strPath,
			pWizardData->m_strFullHostName,
			pWizardData->m_strHostIPAddress,
			pWizardData->m_strUsername,
			pWizardData->m_strAdministratorEmail,
			pWizardData->m_nZopeHTTPPort,
			pWizardData->m_strPortalTitle,
			pWizardData->m_strPortalSubtitle,
			pWizardData->m_strPortalPublisher,
			pWizardData->m_strPortalContributor,
			pWizardData->m_strPortalCreator,
			pWizardData->m_strPortalRights,
			strLanguages,
			pWizardData->m_strMailServerName,
			pWizardData->m_nMailServerPort,
			pWizardData->m_strDefaultFromAddress,
			CRString(IDS_MENU_FOLDER_NAME),
			strRunning);

	GetDlgItem(IDC_SUMMARY_EDIT)->SetWindowText(strInformation);
}

void CSummaryPage::OnOK()
{
	::SendMessage(((CPTKInstallerDlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

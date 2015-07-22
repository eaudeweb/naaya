// MetadataPage.cpp : implementation file
//

#include "stdafx.h"
#include "ptkinstaller.h"
#include "MetadataPage.h"

#include "PTKInstallerDlg.h"
#include "WizardToolz.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CMetadataPage dialog


CMetadataPage::CMetadataPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CMetadataPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CMetadataPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CMetadataPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CMetadataPage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CMetadataPage, CNewWizPage)
	//{{AFX_MSG_MAP(CMetadataPage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMetadataPage message handlers

BOOL CMetadataPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_PORTALMETADATA_TITLE)->SetFont(&((CPTKInstallerDlg*)GetParent())->m_fontTitle, TRUE);

	CWizardData* pWizardData = ((CPTKInstallerDlg*)GetParent())->m_pWizardData;

	GetDlgItem(IDC_PORTAL_TITLE)->SetWindowText(pWizardData->m_strPortalTitle);
	GetDlgItem(IDC_PORTAL_SUBTITLE)->SetWindowText(pWizardData->m_strPortalSubtitle);
	GetDlgItem(IDC_PORTAL_PUBLISHER)->SetWindowText(pWizardData->m_strPortalPublisher);
	GetDlgItem(IDC_PORTAL_CONTRIBUTOR)->SetWindowText(pWizardData->m_strPortalContributor);
	GetDlgItem(IDC_PORTAL_CREATOR)->SetWindowText(pWizardData->m_strPortalCreator);
	GetDlgItem(IDC_PORTAL_RIGHTS)->SetWindowText(pWizardData->m_strPortalRights);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CMetadataPage::OnOK()
{
	::SendMessage(((CPTKInstallerDlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

LRESULT CMetadataPage::OnWizardNext()
{
	CWizardToolz toolz;
	CString strPortalTitle, strPortalSubtitle, strPortalPublisher, strPortalContributor, strPortalCreator, strPortalRights;

	// load data from controls
	GetDlgItem(IDC_PORTAL_TITLE)->GetWindowText(strPortalTitle);
	GetDlgItem(IDC_PORTAL_SUBTITLE)->GetWindowText(strPortalSubtitle);
	GetDlgItem(IDC_PORTAL_PUBLISHER)->GetWindowText(strPortalPublisher);
	GetDlgItem(IDC_PORTAL_CONTRIBUTOR)->GetWindowText(strPortalContributor);
	GetDlgItem(IDC_PORTAL_CREATOR)->GetWindowText(strPortalCreator);
	GetDlgItem(IDC_PORTAL_RIGHTS)->GetWindowText(strPortalRights);

	// store data in wizard data
	CWizardData* pWizardData = ((CPTKInstallerDlg*)GetParent())->m_pWizardData;
	pWizardData->m_strPortalTitle = strPortalTitle;
	pWizardData->m_strPortalSubtitle = strPortalSubtitle;
	pWizardData->m_strPortalPublisher = strPortalPublisher;
	pWizardData->m_strPortalContributor = strPortalContributor;
	pWizardData->m_strPortalCreator = strPortalCreator;
	pWizardData->m_strPortalRights = strPortalRights;

	return 0;
}

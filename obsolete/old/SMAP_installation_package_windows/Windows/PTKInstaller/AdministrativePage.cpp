// AdministrativePage.cpp : implementation file
//

#include "stdafx.h"
#include "ptkinstaller.h"
#include "AdministrativePage.h"

#include "PTKInstallerDlg.h"
#include "WizardToolz.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CAdministrativePage dialog


CAdministrativePage::CAdministrativePage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CAdministrativePage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CAdministrativePage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CAdministrativePage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAdministrativePage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CAdministrativePage, CNewWizPage)
	//{{AFX_MSG_MAP(CAdministrativePage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CAdministrativePage message handlers

BOOL CAdministrativePage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_PORTALADMINISTRATIVE_TITLE)->SetFont(&((CPTKInstallerDlg*)GetParent())->m_fontTitle, TRUE);

	CWizardData* pWizardData = ((CPTKInstallerDlg*)GetParent())->m_pWizardData;

	CListBox* lstLanguages = (CListBox*)GetDlgItem(IDC_PORTAL_LANGUAGES);

	//load languages
	CString strBuf;
	for (int i=0;i < pWizardData->m_arrLanguagesNames.GetSize();i++)
	{
		strBuf.Format("%s [%s]", pWizardData->m_arrLanguagesNames.ElementAt(i), pWizardData->m_arrLanguagesCodes.ElementAt(i));
		lstLanguages->AddString(strBuf);
	}

	GetDlgItem(IDC_PORTAL_MAILSERVERNAME)->SetWindowText(pWizardData->m_strMailServerName);
	strBuf.Format("%d", pWizardData->m_nMailServerPort);
	GetDlgItem(IDC_PORTAL_MAILSERVERPORT)->SetWindowText(strBuf);
	GetDlgItem(IDC_PORTAL_DEFAULTFROMADDRESS)->SetWindowText(pWizardData->m_strDefaultFromAddress);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CAdministrativePage::OnOK()
{
	::SendMessage(((CPTKInstallerDlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

LRESULT CAdministrativePage::OnWizardNext()
{
	CWizardData* pWizardData = ((CPTKInstallerDlg*)GetParent())->m_pWizardData;
	CWizardToolz toolz;
	CString strPortalURL, strMailServerName, strMailServerPort, strDefaultFromAddress;
	int nMailServerPort, nCount;

	// load data from controls
	GetDlgItem(IDC_PORTAL_MAILSERVERNAME)->GetWindowText(strMailServerName);
	GetDlgItem(IDC_PORTAL_MAILSERVERPORT)->GetWindowText(strMailServerPort);
	GetDlgItem(IDC_PORTAL_DEFAULTFROMADDRESS)->GetWindowText(strDefaultFromAddress);

	CListBox* lstLanguages = (CListBox*)GetDlgItem(IDC_PORTAL_LANGUAGES);
	nCount = lstLanguages->GetSelCount();

	pWizardData->m_arrLanguagesSel.RemoveAll();
	pWizardData->m_arrLanguagesSel.SetSize(nCount);
	lstLanguages->GetSelItems(nCount, pWizardData->m_arrLanguagesSel.GetData()); 

	
	// verify that all fields have been filled
	if (strMailServerName == "" || strMailServerPort == "" || strDefaultFromAddress == "")
	{
		AfxMessageBox(IDS_REQUIREDFIELDS);
		return -1;
	}
	
	// convert to numbers
	nMailServerPort = atoi(strMailServerPort);

	// verify ports values
	// check that the ports are free at the time of installation
	if (nMailServerPort < 1 || nMailServerPort > 65535)
	{
		AfxMessageBox(CRString(IDS_MAILSERVERPORT_INVALID));
		return -1;
	}

	// store data in wizard data
	pWizardData->m_strMailServerName = strMailServerName;
	pWizardData->m_nMailServerPort = nMailServerPort;
	pWizardData->m_strDefaultFromAddress = strDefaultFromAddress;

	return 0;
}

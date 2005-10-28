// PortalAdministrativePage.cpp : implementation file
//

#include "stdafx.h"
#include "chm2.h"
#include "PortalAdministrativePage.h"

#include "CHM2Dlg.h"
#include "WizardToolz.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CPortalAdministrativePage dialog


CPortalAdministrativePage::CPortalAdministrativePage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CPortalAdministrativePage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CPortalAdministrativePage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CPortalAdministrativePage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CPortalAdministrativePage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CPortalAdministrativePage, CNewWizPage)
	//{{AFX_MSG_MAP(CPortalAdministrativePage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CPortalAdministrativePage message handlers

BOOL CPortalAdministrativePage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_PORTALADMINISTRATIVE_TITLE)->SetFont(&((CCHM2Dlg*)GetParent())->m_fontTitle, TRUE);

	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;

	GetDlgItem(IDC_PORTAL_URL)->SetWindowText(pWizardData->m_strPortalURL);
	
	CListBox* lstLanguages = (CListBox*)GetDlgItem(IDC_PORTAL_LANGUAGES);

	//load languages
	CString strBuf;
	for (int i=0;i < pWizardData->m_arrLanguagesNames.GetSize();i++)
	{
		strBuf.Format("%s [%s]", pWizardData->m_arrLanguagesNames.ElementAt(i), pWizardData->m_arrLanguagesCodes.ElementAt(i));
		lstLanguages->AddString(strBuf);
	}

	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CPortalAdministrativePage::OnOK()
{
	::SendMessage(((CCHM2Dlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

LRESULT CPortalAdministrativePage::OnWizardNext()
{
	CWizardToolz toolz;
	CString strPortalURL;

	// load data from controls
	GetDlgItem(IDC_PORTAL_URL)->GetWindowText(strPortalURL);

	// store data in wizard data
	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;
	pWizardData->m_strPortalURL = strPortalURL;

	return 0;
}

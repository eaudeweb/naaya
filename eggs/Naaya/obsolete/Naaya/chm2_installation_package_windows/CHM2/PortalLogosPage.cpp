// PortalLogosPage.cpp : implementation file
//

#include "stdafx.h"
#include "chm2.h"
#include "PortalLogosPage.h"

#include "CHM2Dlg.h"
#include "WizardToolz.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CPortalLogosPage dialog


CPortalLogosPage::CPortalLogosPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CPortalLogosPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CPortalLogosPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CPortalLogosPage::DoDataExchange(CDataExchange* pDX)
{
	CNewWizPage::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CPortalLogosPage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CPortalLogosPage, CNewWizPage)
	//{{AFX_MSG_MAP(CPortalLogosPage)
	ON_BN_CLICKED(IDC_LOGO_BROWSE_BUTTON, OnLogoBrowseButton)
	ON_BN_CLICKED(IDC_LOGOBIS_BROWSE_BUTTON, OnLogobisBrowseButton)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CPortalLogosPage message handlers

BOOL CPortalLogosPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_PORTALLOGOS_TITLE)->SetFont(&((CCHM2Dlg*)GetParent())->m_fontTitle, TRUE);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CPortalLogosPage::OnLogoBrowseButton() 
{
	//store current directory
    CString strCurrentDirectory;
	GetCurrentDirectory(1024, strCurrentDirectory.GetBuffer(1024));
    strCurrentDirectory.ReleaseBuffer();

	CFileDialog dlgFile(TRUE, NULL, NULL, OFN_HIDEREADONLY, CRString(IDS_DATASOURCE_IMAGEFILES), this);
	if( dlgFile.DoModal() == IDOK)
	{
		GetDlgItem(IDC_LOGO_PATH)->SetWindowText(dlgFile.GetPathName());
	}

	//restore current directory
	SetCurrentDirectory(strCurrentDirectory);
}

void CPortalLogosPage::OnLogobisBrowseButton() 
{
	//store current directory
    CString strCurrentDirectory;
	GetCurrentDirectory(1024, strCurrentDirectory.GetBuffer(1024));
    strCurrentDirectory.ReleaseBuffer();

	CFileDialog dlgFile(TRUE, NULL, NULL, OFN_HIDEREADONLY, CRString(IDS_DATASOURCE_IMAGEFILES), this);
	if( dlgFile.DoModal() == IDOK)
	{
		GetDlgItem(IDC_LOGOBIS_PATH)->SetWindowText(dlgFile.GetPathName());
	}

	//restore current directory
	SetCurrentDirectory(strCurrentDirectory);
}

void CPortalLogosPage::OnOK()
{
	::SendMessage(((CCHM2Dlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

LRESULT CPortalLogosPage::OnWizardNext()
{
	CWizardToolz toolz;
	CString strLogoPath, strLogoBisPath;

	// load data from controls
	GetDlgItem(IDC_LOGO_PATH)->GetWindowText(strLogoPath);
	GetDlgItem(IDC_LOGOBIS_PATH)->GetWindowText(strLogoBisPath);

	// store data in wizard data
	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;
	pWizardData->m_strLogoPath = strLogoPath;
	pWizardData->m_strLogoBisPath = strLogoBisPath;

	return 0;
}

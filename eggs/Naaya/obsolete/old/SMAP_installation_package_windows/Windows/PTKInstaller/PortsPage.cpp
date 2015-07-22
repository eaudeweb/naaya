// PortsPage.cpp : implementation file
//

#include "stdafx.h"
#include "ptkinstaller.h"
#include "PortsPage.h"

#include "PTKInstallerDlg.h"
#include "WizardToolz.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CPortsPage dialog


CPortsPage::CPortsPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CPortsPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CPortsPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CPortsPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CPortsPage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CPortsPage, CNewWizPage)
	//{{AFX_MSG_MAP(CPortsPage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CPortsPage message handlers

BOOL CPortsPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_PORTS_TITLE)->SetFont(&((CPTKInstallerDlg*)GetParent())->m_fontTitle, TRUE);

	GetDlgItem(IDC_PORTS_ZOPEHTTPPORT_EDIT)->SetWindowText(CRString(IDS_DEFAULT_ZOPEHTTPPORT));
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CPortsPage::OnOK()
{
	::SendMessage(((CPTKInstallerDlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

LRESULT CPortsPage::OnWizardNext()
{
	CWizardToolz toolz;
	CString strError;
	CString strZopeHTTPPort;
	int nZopeHTTPPort;

	// load data from controls
	GetDlgItem(IDC_PORTS_ZOPEHTTPPORT_EDIT)->GetWindowText(strZopeHTTPPort);

	// verify that all fields have been filled
	if (strZopeHTTPPort == "")
	{
		AfxMessageBox(IDS_REQUIREDFIELDS);
		return -1;
	}
	
	// convert to numbers
	nZopeHTTPPort = atoi(strZopeHTTPPort);

	// verify ports values
	// check that the ports are free at the time of installation
	if (nZopeHTTPPort < 1 || nZopeHTTPPort > 65535)
	{
		AfxMessageBox(CRString(IDS_ZOPEHTTPPORT_INVALID));
		return -1;
	}
	else
	{
		if (!toolz.TestPortAvailability(nZopeHTTPPort))
		{
			strError.Format(CRString(IDS_ZOPEHTTPPORT_OCCUPIED), nZopeHTTPPort);
			AfxMessageBox(strError);
			return -1;
		}
	}

	// store path in wizard data
	CWizardData* pWizardData = ((CPTKInstallerDlg*)GetParent())->m_pWizardData;
	pWizardData->m_nZopeHTTPPort = nZopeHTTPPort;

	return 0;
}

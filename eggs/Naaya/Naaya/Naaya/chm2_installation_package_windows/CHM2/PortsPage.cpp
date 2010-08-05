// PortsPage.cpp : implementation file
//

#include "stdafx.h"
#include "CHM2.h"
#include "PortsPage.h"

#include "CHM2Dlg.h"
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
	
	GetDlgItem(IDC_PORTS_TITLE)->SetFont(&((CCHM2Dlg*)GetParent())->m_fontTitle, TRUE);

	GetDlgItem(IDC_PORTS_ZOPEHTTPPORT_EDIT)->SetWindowText(CRString(IDS_DEFAULT_ZOPEHTTPPORT));
	//GetDlgItem(IDC_PORTS_ZOPEFTPPORT_EDIT)->SetWindowText(CRString(IDS_DEFAULT_ZOPEFTPPORT));
	//GetDlgItem(IDC_PORTS_ZOPEWEBDAVPORT_EDIT)->SetWindowText(CRString(IDS_DEFAULT_ZOPEWEBDAVPORT));
		
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CPortsPage::OnOK()
{
	::SendMessage(((CCHM2Dlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

LRESULT CPortsPage::OnWizardNext()
{
	CWizardToolz toolz;
	CString strError;
	CString strZopeHTTPPort, strZopeFTPPort, strZopeWEBDAVPort;
	int nZopeHTTPPort, nZopeFTPPort, nZopeWEBDAVPort;

	// load data from controls
	GetDlgItem(IDC_PORTS_ZOPEHTTPPORT_EDIT)->GetWindowText(strZopeHTTPPort);
	//GetDlgItem(IDC_PORTS_ZOPEFTPPORT_EDIT)->GetWindowText(strZopeFTPPort);
	//GetDlgItem(IDC_PORTS_ZOPEWEBDAVPORT_EDIT)->GetWindowText(strZopeWEBDAVPort);

	// verify that all fields have been filled
	if (strZopeHTTPPort == "")
	{
		AfxMessageBox(IDS_REQUIREDFIELDS);
		return -1;
	}
	
	// convert to numbers
	nZopeHTTPPort = atoi(strZopeHTTPPort);
	//nZopeFTPPort = atoi(strZopeFTPPort);
	//nZopeWEBDAVPort = atoi(strZopeWEBDAVPort);

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
	/*if (nZopeFTPPort < 1 || nZopeFTPPort > 65535)
	{
		AfxMessageBox(CRString(IDS_ZOPEFTPPORT_INVALID));
		return -1;
	}
	else
	{
		if (!toolz.TestPortAvailability(nZopeFTPPort))
		{
			strError.Format(CRString(IDS_ZOPEFTPPORT_OCCUPIED), nZopeFTPPort);
			AfxMessageBox(strError);
			return -1;
		}
	}
	if (nZopeWEBDAVPort < 1 || nZopeWEBDAVPort > 65535)
	{
		AfxMessageBox(CRString(IDS_ZOPEWEBDAVPORT_INVALID));
		return -1;
	}
	else
	{
		if (!toolz.TestPortAvailability(nZopeWEBDAVPort))
		{
			strError.Format(CRString(IDS_ZOPEWEBDAVPORT_OCCUPIED), nZopeWEBDAVPort);
			AfxMessageBox(strError);
			return -1;
		}
	}*/

	// store path in wizard data
	CWizardData* pWizardData = ((CCHM2Dlg*)GetParent())->m_pWizardData;
	pWizardData->m_nZopeHTTPPort = nZopeHTTPPort;
	//pWizardData->m_nZopeFTPPort = nZopeFTPPort;
	//pWizardData->m_nZopeWEBDAVPort = nZopeWEBDAVPort;

	return 0;
}

// Parameters.cpp : implementation file
//

#include "stdafx.h"
#include "PTKInstaller.h"
#include "ParametersPage.h"

#include "PTKInstallerDlg.h"
#include "WizardToolz.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CParametersPage dialog


CParametersPage::CParametersPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CParametersPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CParametersPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CParametersPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CParametersPage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CParametersPage, CNewWizPage)
	//{{AFX_MSG_MAP(CParametersPage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CParametersPage message handlers

BOOL CParametersPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();
	
	GetDlgItem(IDC_PARAMETERS_TITLE)->SetFont(&((CPTKInstallerDlg*)GetParent())->m_fontTitle, TRUE);
	
	// get host name and IP
	CString strHostName;
    int nIpField0, nIpField1, nIpField2, nIpField3;
    CWizardToolz::GetHostInfos(strHostName, nIpField0, nIpField1, nIpField2, nIpField3);
    if (strHostName != "")
    {
        GetDlgItem(IDC_PARAMETERS_FULLHOSTNAME_EDIT)->SetWindowText(strHostName);
        ((CIPAddressCtrl*)GetDlgItem(IDC_PARAMETERS_HOSTIDADDRESS_IPADDRESS))->SetAddress(nIpField0, nIpField1, nIpField2, nIpField3);
    }
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CParametersPage::OnOK()
{
	::SendMessage(((CPTKInstallerDlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

LRESULT CParametersPage::OnWizardNext()
{
	CWizardToolz toolz;
	CString strFullHostName, strHostIPAddress, strUsername, strPassword, strConfirmPassword, strAdministratorEmail;
    BYTE nField1, nField2, nField3, nField4;

	// load data from controls
	GetDlgItem(IDC_PARAMETERS_FULLHOSTNAME_EDIT)->GetWindowText(strFullHostName);
	((CIPAddressCtrl*)GetDlgItem(IDC_PARAMETERS_HOSTIDADDRESS_IPADDRESS))->GetAddress(nField1, nField2, nField3, nField4);
    strHostIPAddress.Format("%d.%d.%d.%d", nField1, nField2, nField3, nField4);
	GetDlgItem(IDC_PARAMETERS_FULLHOSTNAME_EDIT)->GetWindowText(strFullHostName);
	GetDlgItem(IDC_PARAMETERS_USERNAME_EDIT)->GetWindowText(strUsername);
	GetDlgItem(IDC_PARAMETERS_PASSWORD_EDIT)->GetWindowText(strPassword);
	GetDlgItem(IDC_PARAMETERS_CONFIRMPASSWORD_EDIT)->GetWindowText(strConfirmPassword);
	GetDlgItem(IDC_PARAMETERS_ADMINEMAIL_EDIT)->GetWindowText(strAdministratorEmail);

	// verify that all fields have been filled
	if (strFullHostName == "" || strHostIPAddress == "" || strUsername == "" ||
		strPassword == "" || strConfirmPassword == "" || strAdministratorEmail == "")
	{
		AfxMessageBox(IDS_REQUIREDFIELDS);
		return -1;
	}

	// check username and password are only letters and numbers
	if (!toolz.isAlphanumeric(strUsername))
	{
		AfxMessageBox(IDS_USERNAME_ALPHANUMERIC);
		return -1;
	}
	if (!toolz.isAlphanumeric(strPassword))
	{
		AfxMessageBox(IDS_PASSWORD_ALPHANUMERIC);
		return -1;
	}

	// check passwords
	if (strPassword != strConfirmPassword)
	{
		AfxMessageBox(IDS_PASSWORDS);
		return -1;
	}

	// store path in wizard data
	CWizardData* pWizardData = ((CPTKInstallerDlg*)GetParent())->m_pWizardData;
	pWizardData->m_strFullHostName = strFullHostName;
	pWizardData->m_strHostIPAddress = strHostIPAddress;
	pWizardData->m_strUsername = strUsername;
	pWizardData->m_strPassword = strPassword;
	pWizardData->m_strAdministratorEmail = strAdministratorEmail;

	return 0;
}

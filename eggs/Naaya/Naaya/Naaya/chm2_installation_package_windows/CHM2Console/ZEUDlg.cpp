// ZEUDlg.cpp : implementation file
//

#include "stdafx.h"
#include "CHM2Console.h"
#include "ZEUDlg.h"

#include "ConsoleToolz.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CZEUDlg dialog


CZEUDlg::CZEUDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CZEUDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CZEUDlg)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT

	// read zope path from registry
	CConsoleToolz toolz;
	CString strRegString = "SOFTWARE\\" +
		CRString(IDS_REGCOMPANY) + "\\" + 
		CRString(IDS_REGAPPLICATION) + "\\";
    toolz.CTReadRegistryKey(strRegString, "Instance path", m_strInstancePath);
}


void CZEUDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CZEUDlg)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CZEUDlg, CDialog)
	//{{AFX_MSG_MAP(CZEUDlg)
	ON_BN_CLICKED(IDC_DELETE_ZEU_BUTTON, OnDeleteZEU)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CZEUDlg message handlers

BOOL CZEUDlg::OnInitDialog() 
{
	CDialog::OnInitDialog();
	
	CConsoleToolz toolz;
	GetDlgItem(IDC_DELETE_ZEU_BUTTON)->EnableWindow(toolz.CTExistsFile(m_strInstancePath + "\\access"));
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CZEUDlg::OnOK() 
{
	CConsoleToolz toolz;

	// load data from controls
	CString strUsername, strPassword, strConfirmPassword;
	GetDlgItem(IDC_USERNAME_EDIT)->GetWindowText(strUsername);
	GetDlgItem(IDC_PASSWORD_EDIT)->GetWindowText(strPassword);
	GetDlgItem(IDC_CONFIRMPASSWORD_EDIT)->GetWindowText(strConfirmPassword);

	// check values
	if (strUsername == "" || strPassword == "" || strConfirmPassword == "")
	{
		AfxMessageBox(CRString(IDS_FIELDS_MANDATORY));
		return;
	}
	// check username and password are only letters and numbers
	if (!toolz.isAlphanumeric(strUsername))
	{
		AfxMessageBox(IDS_USERNAME_ALPHANUMERIC);
		return;
	}
	if (!toolz.isAlphanumeric(strPassword))
	{
		AfxMessageBox(IDS_PASSWORD_ALPHANUMERIC);
		return;
	}
	// check passwords
	if (strPassword != strConfirmPassword)
	{
		AfxMessageBox(IDS_PASSWORDS_MATCH);
		return;
	}
	CString strAccessFilePath, strAccessFileContent;
	strAccessFilePath.Format("%s\\access", m_strInstancePath);
	strAccessFileContent.Format("%s:%s", strUsername, strPassword);
	if (!toolz.CTWriteToFile(strAccessFilePath, strAccessFileContent))
	{
		CString strError;
		strError.Format(CRString(IDS_EMERGENCYUSER_FAILED), strAccessFilePath);
		AfxMessageBox(strError);
	}
	else
	{
		AfxMessageBox(IDS_EMERGENCYUSER_CREATED, MB_OK | MB_ICONINFORMATION);
	}
	
	// enable/disable delete button
	GetDlgItem(IDC_DELETE_ZEU_BUTTON)->EnableWindow(toolz.CTExistsFile(m_strInstancePath + "\\access"));
}

void CZEUDlg::OnDeleteZEU() 
{
	CConsoleToolz toolz;
	CString strAccessFilePath;
	strAccessFilePath.Format("%s\\access", m_strInstancePath);
	int nRet = toolz.CTDeleteFile(strAccessFilePath);
	if (0 == nRet)
	{
		AfxMessageBox(IDS_EMERGENCYUSER_DELETED, MB_OK | MB_ICONINFORMATION);
	}
	else
	{
		CString strError;
		strError.Format(CRString(IDS_DELETE_EMERGENCYUSER_FAILED), strAccessFilePath);
		AfxMessageBox(strError);
	}
	
	// enable/disable delete button
	GetDlgItem(IDC_DELETE_ZEU_BUTTON)->EnableWindow(toolz.CTExistsFile(m_strInstancePath + "\\access"));
}

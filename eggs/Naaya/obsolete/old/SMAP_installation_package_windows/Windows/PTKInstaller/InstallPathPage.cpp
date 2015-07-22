// InstallPathPage.cpp : implementation file
//

#include "stdafx.h"
#include "PTKInstaller.h"
#include "InstallPathPage.h"
#include "PTKInstallerDlg.h"
#include "WizardToolz.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CInstallPathPage dialog


CInstallPathPage::CInstallPathPage(CWnd* pParent /*=NULL*/)
	: CNewWizPage(CInstallPathPage::IDD, pParent)
{
	//{{AFX_DATA_INIT(CInstallPathPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CInstallPathPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CInstallPathPage)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CInstallPathPage, CNewWizPage)
	//{{AFX_MSG_MAP(CInstallPathPage)
	ON_BN_CLICKED(IDC_INSTALLPATH_BROWSE_BUTTON, OnInstallpathBrowseButton)
	ON_EN_KILLFOCUS(IDC_INSTALLPATH_PATH_EDIT, OnKillfocusInstallpathPathEdit)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CInstallPathPage message handlers

BOOL CInstallPathPage::OnInitDialog() 
{
	CNewWizPage::OnInitDialog();

	GetDlgItem(IDC_INSTALLPATH_TITLE)->SetFont(&((CPTKInstallerDlg*)GetParent())->m_fontTitle, TRUE);

    CString strPath = CRString(IDS_INSTALLATION_DEFAULT_PATH);
	SetTexts(strPath);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CInstallPathPage::OnInstallpathBrowseButton() 
{
	CString strPath = CWizardToolz::BrowseForFolder(this->m_hWnd, "Browse", 0);
	if (strPath!="")
    {
	    SetTexts(strPath);
    }	
}

void CInstallPathPage::OnKillfocusInstallpathPathEdit() 
{
	CString strPath;
    ((CEdit*)GetDlgItem(IDC_INSTALLPATH_PATH_EDIT))->GetWindowText(strPath);
	SetTexts(strPath);
}

void CInstallPathPage::OnOK()
{
	::SendMessage(((CPTKInstallerDlg*)GetParent())->m_hWnd, WM_COMMAND, MAKEWPARAM(ID_WIZNEXT, BN_CLICKED), (LPARAM)NULL);
}

LRESULT CInstallPathPage::OnWizardNext()
{
	CWizardToolz toolz;

	// get path
	CString strPath;
    GetDlgItem(IDC_INSTALLPATH_PATH_EDIT)->GetWindowText(strPath);

    // verify that the installation path is valid
    if (!toolz.InternalExistsFolder(strPath))
    {
		if (IDOK == MessageBox(CRString(IDS_CREATEDIRECTORY_QUESTION), CRString(IDS_CREATEDIRECTORY), MB_OKCANCEL | MB_ICONQUESTION))
		{
			// verify that the available space is enough
			if (m_n64Available < ((CPTKInstallerDlg*)GetParent())->m_pWizardData->m_n64SpaceRequired)
			{
				AfxMessageBox(CRString(IDS_NOTENOUGHSPACE));
				return -1;
			}
            // create directory;
            if (!toolz.InternalCreateChainFolders(strPath))
            {
				MessageBox(CRString(IDS_ERROR_CREATE_DIR), CRString(IDS_CREATEDIRECTORY), MB_OK | MB_ICONWARNING);
                return -1;
            }
        }
        else
        {
			MessageBox(CRString(IDS_INVALIDPATH), CRString(IDS_CREATEDIRECTORY), MB_OK | MB_ICONWARNING);
            return -1;
        }
    }

	// store path in wizard data
	((CPTKInstallerDlg*)GetParent())->m_pWizardData->m_strPath = strPath;

	return 0;
}

void CInstallPathPage::SetTexts(CString strPath)
{
	GetDlgItem(IDC_INSTALLPATH_PATH_EDIT)->SetWindowText(strPath);

	// set labels
    CString strText;
    CString strDriveUpper = strPath.Left(1);
    strDriveUpper.MakeUpper();
    strText.Format(CRString(IDS_AVAILABLESPACE), strDriveUpper);
    GetDlgItem(IDC_INSTALLPATH_AVAILABLESPACE_LABEL)->SetWindowText(strText);
    strText.Format(CRString(IDS_REQUIREDSPACE), strDriveUpper);
    GetDlgItem(IDC_INSTALLPATH_REQUIREDSPACE_LABEL)->SetWindowText(strText);

	// set available space
	strText = CWizardToolz::GetFreeSpaceForADrive(strPath.Left(3), m_n64Available);
	strText += " MB";
    GetDlgItem(IDC_INSTALLPATH_AVAILABLESPACE_VALUE)->SetWindowText(strText);
	strText = ((CPTKInstallerDlg*)GetParent())->m_pWizardData->m_strSpaceRequired;
	strText += " MB";
	GetDlgItem(IDC_INSTALLPATH_REQUIREDSPACE_VALUE)->SetWindowText(strText);
}

// CHM2.cpp : Defines the class behaviors for the application.
//

#include "stdafx.h"
#include "CHM2.h"
#include "CHM2Dlg.h"

#include "WizardToolz.h"
#include "WizardData.h"
#include "ServiceManager.h"

#include "ErrorPage.h"
#include "WelcomePage.h"
#include "AgreementPage.h"
#include "InstallPathPage.h"
#include "ParametersPage.h"
#include "PortsPage.h"
#include "PortalMetadataPage.h"
#include "PortalLogosPage.h"
#include "PortalAdministrativePage.h"
#include "FinishPage.h"
#include "InstallPage.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CCHM2App

BEGIN_MESSAGE_MAP(CCHM2App, CWinApp)
	//{{AFX_MSG_MAP(CCHM2App)
		// NOTE - the ClassWizard will add and remove mapping macros here.
		//    DO NOT EDIT what you see in these blocks of generated code!
	//}}AFX_MSG
	ON_COMMAND(ID_HELP, CWinApp::OnHelp)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CCHM2App construction

CCHM2App::CCHM2App()
{
	// TODO: add construction code here,
	// Place all significant initialization in InitInstance
}

/////////////////////////////////////////////////////////////////////////////
// The one and only CCHM2App object

CCHM2App theApp;

/////////////////////////////////////////////////////////////////////////////
// CCHM2App initialization

BOOL CCHM2App::InitInstance()
{
    if (FAILED(CoInitialize(NULL)))
    {
        ::MessageBox(NULL,"Error : CoInitialize(NULL)","What ?",MB_OK);
        // error handling
    }

	AfxEnableControlContainer();

	// Standard initialization
	// If you are not using these features and wish to reduce the size
	//  of your final executable, you should remove from the following
	//  the specific initialization routines you do not need.

#ifdef _AFXDLL
	Enable3dControls();			// Call this when using MFC in a shared DLL
#else
	Enable3dControlsStatic();	// Call this when linking to MFC statically
#endif

	// first check that current user is an Administrator on this machine
	BOOL bIsAdministrator = CWizardToolz().RunningAsAdministrator();

	CCHM2Dlg dlg;
	m_pMainWnd = &dlg;

	// create wizard data container
	CWizardData* pWizardData = new CWizardData();
	pWizardData->m_bIsCurrentUserAdministrator = bIsAdministrator;
	dlg.m_pWizardData = pWizardData;

	// create service manager 
	CServiceManager* pServiceManager = new CServiceManager();
	dlg.m_pServiceManager = pServiceManager;

	if (bIsAdministrator)
	{
		CString strError;
		if (CanRunInstaller(strError))
		{
			// we can run the installer

			// create and add wizard pages
			CWelcomePage WelcomePage;
			CAgreementPage AgreementPage;
			CInstallPathPage InstallPathPage;
			CParametersPage ParametersPage;
			CPortsPage PortsPage;
			CPortalMetadataPage PortalMetadataPage;
			CPortalLogosPage PortalLogosPage;
			CPortalAdministrativePage PortalAdministrativePage;
			CFinishPage FinishPage;
			CInstallPage InstallPage;

			dlg.AddPage(&WelcomePage, CWelcomePage::IDD);
			dlg.AddPage(&AgreementPage, CAgreementPage::IDD);
			dlg.AddPage(&InstallPathPage, CInstallPathPage::IDD);
			dlg.AddPage(&ParametersPage, CParametersPage::IDD);
			dlg.AddPage(&PortsPage, CPortsPage::IDD);
			dlg.AddPage(&PortalMetadataPage, CPortalMetadataPage::IDD);
			dlg.AddPage(&PortalLogosPage, CPortalLogosPage::IDD);
			dlg.AddPage(&PortalAdministrativePage, CPortalAdministrativePage::IDD);
			dlg.AddPage(&FinishPage, CFinishPage::IDD);
			dlg.AddPage(&InstallPage, CInstallPage::IDD);

			// start wizard
			int nRet = dlg.DoModal();
		}
		else
		{
			// cannot run the installer, just display the error page
			
			// create and add the error page
			CErrorPage ErrorPage;
			ErrorPage.m_strError = strError;

			dlg.AddPage(&ErrorPage, CErrorPage::IDD);

			// before display dialog invalidate some controls
			dlg.m_bErrorPage = TRUE;

			// start wizard
			int nRet = dlg.DoModal();
		}
	}
	else
	{
		// cannot run the installer, just display the error page
		
		// create and add the error page
		CErrorPage ErrorPage;
		ErrorPage.m_strError = CRString(IDS_ABORT_WIZARD_MESSAGE);

		dlg.AddPage(&ErrorPage, CErrorPage::IDD);

		// before display dialog invalidate some controls
		dlg.m_bErrorPage = TRUE;

		// start wizard
		int nRet = dlg.DoModal();
	}

	// Since the dialog has been closed, return FALSE so that we exit the
	//  application, rather than start the application's message pump.
	return FALSE;
}

BOOL CCHM2App::CanRunInstaller(CString& strError)
{
	BOOL bRet = TRUE;

	CWizardToolz toolz;
	CServiceManager servicemanager;

	CString strBuffer;

	// 1. check that services are not registered
	strError = "";
	if (servicemanager.SMIsServiceInstalled(CRString(IDS_SERVICE_NAME_ZOPE)))
	{
		bRet = FALSE;
		strBuffer.Format(CRString(IDS_SERVICE_ALREADY_INSTALLED), CRString(IDS_SERVICE_NAME_ZOPE));
		strError += strBuffer;
	}

	// 2. check that no key in the registry
	if (!strError.IsEmpty())
		strError += "\r\n";
	CString strRegString = "SOFTWARE\\" +
		CRString(IDS_REGCOMPANY) + "\\" + 
		CRString(IDS_REGAPPLICATION) + "\\";

	if (toolz.ExistsRegistryKey(strRegString))
	{
		bRet = FALSE;
		strBuffer.Format(CRString(IDS_REGISTRY_TELLS), strRegString);
		strError += strBuffer;
	}

	// 3. check that no entry in folder menu
	if (!strError.IsEmpty())
		strError += "\r\n";
	CString strStartMenuFolder;
	char szBuffer[_MAX_PATH];
	::SHGetSpecialFolderPath(NULL, szBuffer, CSIDL_COMMON_PROGRAMS, 0);
	strStartMenuFolder.Format("%s\\%s", szBuffer, CRString(IDS_MENU_FOLDER_NAME));

	if (toolz.InternalExistsFolder(strStartMenuFolder))
	{
		bRet = FALSE;
		strBuffer.Format(CRString(IDS_SHORTCUT_ALREADY_EXISTS), strStartMenuFolder);
		strError += strBuffer;
	}
	
	return bRet;
}

int CCHM2App::ExitInstance() 
{
	CoUninitialize();
	
	return CWinApp::ExitInstance();
}

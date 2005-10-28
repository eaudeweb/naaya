// WizardData.cpp: implementation of the CWizardData class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "CHM2.h"
#include "WizardData.h"

#ifdef _DEBUG
#undef THIS_FILE
static char THIS_FILE[]=__FILE__;
#define new DEBUG_NEW
#endif

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CWizardData::CWizardData()
{
	// InstallPath page
	m_strPath = "";
	m_n64SpaceRequired = 90*1024*1024;
	m_strSpaceRequired = "90";

	// Parameters page
	m_strFullHostName = "";
	m_strHostIPAddress = "";
	m_strUsername = "";
	m_strPassword = "";
	m_strAdministratorEmail = "";

	// Ports page
	m_nZopeHTTPPort = -1;
	m_nZopeFTPPort = -1;
	m_nZopeWEBDAVPort = -1;

	// Run as service default
	m_nRunAsService = 1;

	// Portal metadata
	m_strPortalTitle = "";
	m_strPortalSubtitle = "";
	m_strPortalPublisher = "EEA";
	m_strPortalContributor = "EC CHM";
	m_strPortalCreator = "EC CHM";
	m_strPortalRights = "EEA";
}

CWizardData::~CWizardData()
{

}

// WizardData.cpp: implementation of the CWizardData class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "PTKInstaller.h"
#include "WizardData.h"

#include <fstream.h>

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
	m_n64SpaceRequired = 80*1024*1024;
	m_strSpaceRequired = "80";

	// Parameters page
	m_strFullHostName = "";
	m_strHostIPAddress = "";
	m_strUsername = "";
	m_strPassword = "";
	m_strAdministratorEmail = "";

	// Ports page
	m_nZopeHTTPPort = -1;

	// Run as service default
	m_nRunAsService = 1;

	// Portal metadata
	m_strPortalTitle = "";
	m_strPortalSubtitle = "";
	m_strPortalPublisher = "";
	m_strPortalContributor = "";
	m_strPortalCreator = "";
	m_strPortalRights = "";


	// Portal administrative
	//process languages file path
    // get current folder path
    CString strCurrentDirectory;
	GetCurrentDirectory(1024, strCurrentDirectory.GetBuffer(1024));
    strCurrentDirectory.ReleaseBuffer();
    CString strZopeFolder = CRString(IDS_FOLDER_ZOPE);

	// load languages codes and names
	ifstream languagesfile (strCurrentDirectory + strZopeFolder + "\\bin\\Lib\\site-packages\\itools\\i18n\\languages.txt");
	CString strLine, strLanguageCode, strLanguageName;
	int nPos;
	if (languagesfile.is_open())
	{
		while (!languagesfile.eof())
		{
			languagesfile.getline(strLine.GetBuffer(100), 100);
			strLine.ReleaseBuffer();
			strLine.TrimLeft();
			strLine.TrimRight();
			if (strLine != "" && strLine[0] != '#')
			{
				nPos = strLine.Find(" ");
				strLanguageCode = strLine.Left(nPos);
				strLanguageName = strLine.Right(strLine.GetLength()-nPos-1);
				if (strLanguageCode != "en")
				{
					if (strLanguageCode != "ar")
					{
						if (strLanguageCode != "fr")
						{
							//don't load Arabic, French and English languages, are the default ones
							m_arrLanguagesCodes.Add(strLanguageCode);
							m_arrLanguagesNames.Add(strLanguageName);
						}
					}
				}
			}
			
		}
	}
	m_strMailServerName = "localhost";
	m_nMailServerPort = 25;
	m_strDefaultFromAddress = "";
}

CWizardData::~CWizardData()
{

}

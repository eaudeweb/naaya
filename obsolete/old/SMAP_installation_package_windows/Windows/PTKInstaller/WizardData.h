// WizardData.h: interface for the CWizardData class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_WIZARDDATA_H__43ED010B_6D44_4951_86F6_0E3816AF10CD__INCLUDED_)
#define AFX_WIZARDDATA_H__43ED010B_6D44_4951_86F6_0E3816AF10CD__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class CWizardData  
{
public:
	CWizardData();
	virtual ~CWizardData();

public:
	BOOL m_bIsCurrentUserAdministrator;

	// InstallPath page
	CString m_strPath;
    unsigned __int64 m_n64SpaceRequired;
	CString m_strSpaceRequired;

	// Parameters page
	CString m_strFullHostName;
	CString m_strHostIPAddress;
	CString m_strUsername;
	CString m_strPassword;
	CString m_strAdministratorEmail;

	// Ports page
	int m_nZopeHTTPPort;

	// Run page
	int m_nRunAsService;

	// Portal metadata page
	CString m_strPortalTitle;
	CString m_strPortalSubtitle;
	CString m_strPortalPublisher;
	CString m_strPortalContributor;
	CString m_strPortalCreator;
	CString m_strPortalRights;

	// Portal administrative page
	CStringArray m_arrLanguagesCodes;
	CStringArray m_arrLanguagesNames;
	CArray<int, int> m_arrLanguagesSel;
	CString m_strMailServerName;
	int m_nMailServerPort;
	CString m_strDefaultFromAddress;

	// Other
    unsigned __int64 m_n64TotalSize;
    unsigned __int64 m_n64PieceSize;
};

#endif // !defined(AFX_WIZARDDATA_H__43ED010B_6D44_4951_86F6_0E3816AF10CD__INCLUDED_)

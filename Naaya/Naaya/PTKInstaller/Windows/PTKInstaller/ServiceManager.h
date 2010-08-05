// ServiceManager.h: interface for the CServiceManager class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_SERVICEMANAGER_H__985C926E_1B96_4DC7_BF62_2351D616CFA8__INCLUDED_)
#define AFX_SERVICEMANAGER_H__985C926E_1B96_4DC7_BF62_2351D616CFA8__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class CServiceManager  
{
public:
	CServiceManager();
	virtual ~CServiceManager();

public:
	void QueryService(CString strServiceName, IN OUT ITEMDATA *item);
	void QueryServiceByDisplay(CString strDisplayName, IN OUT ITEMDATA *item);

	BOOL SMIsServiceInstalled(CString strName);
	BOOL SMInstallService(CString strName, CString strDisplay, CString strPath);
	void SMUninstallService(CString strName);
	void SMStartService(CString strName);
	void SMStopService(CString strName);

	void SMQueryServiceStatus(CString strName, SERVICE_STATUS& status);
	void SMGetServiceStatusMeaning(IN ITEMDATA *item, CString& strStatus);
	BOOL SMGetServiceStopStatus(IN ITEMDATA *item);
	BOOL SMGetServiceStartStatus(IN ITEMDATA *item);
};

#endif // !defined(AFX_SERVICEMANAGER_H__985C926E_1B96_4DC7_BF62_2351D616CFA8__INCLUDED_)

// ServiceManager.h: interface for the CServiceManager class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_SERVICEMANAGER_H__9982D849_989B_4DEF_AE6A_D9FDC40C4BD2__INCLUDED_)
#define AFX_SERVICEMANAGER_H__9982D849_989B_4DEF_AE6A_D9FDC40C4BD2__INCLUDED_

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

	BOOL SMInstallService(CString strName, CString strDisplay, CString strPath);
	void SMUninstallService(CString strName);
	void SMStartService(CString strName);
	void SMStopService(CString strName);

	void SMQueryServiceStatus(CString strName, SERVICE_STATUS& status);
	void SMGetServiceStatusMeaning(IN ITEMDATA *item, CString& strStatus);
	BOOL SMGetServiceStopStatus(IN ITEMDATA *item);
	BOOL SMGetServiceStartStatus(IN ITEMDATA *item);
	BOOL SMChangeServiceConfig(CString strName, DWORD dwStartupType, CString& strError);
};

#endif // !defined(AFX_SERVICEMANAGER_H__9982D849_989B_4DEF_AE6A_D9FDC40C4BD2__INCLUDED_)

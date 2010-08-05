// ServiceManager.cpp: implementation of the CServiceManager class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "CHM2.h"
#include "ServiceManager.h"

#ifdef _DEBUG
#undef THIS_FILE
static char THIS_FILE[]=__FILE__;
#define new DEBUG_NEW
#endif

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CServiceManager::CServiceManager()
{

}

CServiceManager::~CServiceManager()
{

}

void CServiceManager::QueryService(CString strServiceName, IN OUT ITEMDATA *item)
{

	SC_HANDLE schSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);

	LPQUERY_SERVICE_CONFIG lpqscBuf; 
    LPSERVICE_DESCRIPTION lpqscBuf2;
    DWORD dwBytesNeeded; 
	
    // Open a handle to the service. 
	
    SC_HANDLE schService = OpenService( 
        schSCManager,           // SCManager database 
        strServiceName,           // name of service 
        SERVICE_QUERY_CONFIG);  // need QUERY access 

    if (schService == NULL) 
        TRACE("OpenService"); 
	
    // Allocate a buffer for the configuration information. 
	
    lpqscBuf = (LPQUERY_SERVICE_CONFIG) LocalAlloc(LPTR, 4096); 
    if (lpqscBuf == NULL) 
        TRACE("LocalAlloc"); 
	
    lpqscBuf2 = (LPSERVICE_DESCRIPTION) LocalAlloc(LPTR, 4096); 
    if (lpqscBuf2 == NULL) 
        TRACE("LocalAlloc"); 
	
    // Get the configuration information. 
	
    if (! QueryServiceConfig( 
        schService, 
        lpqscBuf, 
        4096, 
        &dwBytesNeeded) ) 
    {
        TRACE("QueryServiceConfig"); 
    }
	
    if (! QueryServiceConfig2( 
        schService, 
        SERVICE_CONFIG_DESCRIPTION,
        (LPBYTE)lpqscBuf2,
        4096, 
        &dwBytesNeeded) ) 
    {
        TRACE("QueryServiceConfig2"); 
		int nError = GetLastError();
		switch(nError) {
		case ERROR_ACCESS_DENIED: 
			TRACE("The handle does not have the SERVICE_QUERY_CONFIG access right.\n");
			break;
		case ERROR_INSUFFICIENT_BUFFER:
			TRACE("There is more service configuration information than would fit into the lpBuffer buffer. The number of bytes required to get all the information is returned in the pcbBytesNeeded parameter. Nothing is written to lpBuffer. \n");
			break;
		case ERROR_INVALID_HANDLE:
			TRACE("The specified handle is invalid. \n");
			break;
		}
			
    }
	
    // set the configuration information. 

	item->strServiceName	= strServiceName;
	item->strDisplayName	= lpqscBuf->lpDisplayName;
	item->nStartupType		= lpqscBuf->dwStartType;
	item->strBinaryPath		= lpqscBuf->lpBinaryPathName;

	item->strDescription	= lpqscBuf2->lpDescription;
	
    LocalFree(lpqscBuf); 
    LocalFree(lpqscBuf2);	
}

void CServiceManager::QueryServiceByDisplay(CString strDisplayName, IN OUT ITEMDATA *item)
{
	SC_HANDLE schSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);

	LPQUERY_SERVICE_CONFIG lpqscBuf; 
    LPSERVICE_DESCRIPTION lpqscBuf2;
	LPSERVICE_STATUS lpServiceStatus;
	
    DWORD dwBytesNeeded; 
	
	TCHAR strServiceName[128];
	DWORD dwSize = 128;
    // Open a handle to the service. 
	BOOL bRet = GetServiceKeyName(
		schSCManager,
		strDisplayName,
		strServiceName,
		&dwSize);
	
	if(!bRet)
		return;
	
    SC_HANDLE schService = OpenService( 
        schSCManager,           // SCManager database 
        strServiceName,           // name of service 
        SERVICE_QUERY_CONFIG|SERVICE_QUERY_STATUS);  // need QUERY access 
	
    if (schService == NULL) {
        TRACE("OpenService");
		return;
	}
	
    // Allocate a buffer for the configuration information. 
	
    lpqscBuf = (LPQUERY_SERVICE_CONFIG) LocalAlloc(LPTR, 4096); 
    if (lpqscBuf == NULL) 
        TRACE("LocalAlloc 1"); 
	
    lpqscBuf2 = (LPSERVICE_DESCRIPTION) LocalAlloc(LPTR, 4096); 
    if (lpqscBuf2 == NULL) 
        TRACE("LocalAlloc 2"); 

	lpServiceStatus = (LPSERVICE_STATUS) LocalAlloc(LPTR, sizeof(SERVICE_STATUS));
    if (lpServiceStatus == NULL) 
        TRACE("LocalAlloc 3"); 
	
	
    // Get the configuration information. 
	
    if (! QueryServiceConfig( 
        schService, 
        lpqscBuf, 
        4096, 
        &dwBytesNeeded) ) 
    {
        TRACE("QueryServiceConfig"); 
    }
	
    if (! QueryServiceConfig2( 
        schService, 
        SERVICE_CONFIG_DESCRIPTION,
        (LPBYTE)lpqscBuf2,
        4096, 
        &dwBytesNeeded) ) 
    {
        TRACE("QueryServiceConfig2"); 
		int nError = GetLastError();
		switch(nError) {
		case ERROR_ACCESS_DENIED: 
			TRACE("The handle does not have the SERVICE_QUERY_CONFIG access right.\n");
			break;
		case ERROR_INSUFFICIENT_BUFFER:
			TRACE("There is more service configuration information than would fit into the lpBuffer buffer. The number of bytes required to get all the information is returned in the pcbBytesNeeded parameter. Nothing is written to lpBuffer. \n");
			break;
		case ERROR_INVALID_HANDLE:
			TRACE("The specified handle is invalid. \n");
			break;
		}
		
    }

	if(!QueryServiceStatus(schService,lpServiceStatus))
	{
		int nError = GetLastError();
		switch(nError)
		{
		case ERROR_ACCESS_DENIED: 
			TRACE("The handle does not have the SERVICE_QUERY_STATUS access right.\n");
			break;
		case ERROR_INVALID_HANDLE: 
			TRACE("The handle is invalid.\n");
			break;
		default:
			TRACE("QueryServiceStatus unknown error");
		}			
	}
	
    // set the configuration information. 
	
	item->strServiceName	= strServiceName;
	item->strDisplayName	= lpqscBuf->lpDisplayName;
	item->nStartupType		= lpqscBuf->dwStartType;
	item->strBinaryPath		= lpqscBuf->lpBinaryPathName;
	
	item->strDescription	= lpqscBuf2->lpDescription;

	item->nStatus			= lpServiceStatus->dwCurrentState;
	item->dwControlsAccepted= lpServiceStatus->dwControlsAccepted;
		
    LocalFree(lpqscBuf); 
    LocalFree(lpqscBuf2);	
	LocalFree(lpServiceStatus);

	CloseServiceHandle(schService);
}

void CServiceManager::SMGetServiceStatusMeaning(IN ITEMDATA *item, CString& strStatus)
{
	switch (item->nStatus)
	{
		case SERVICE_STOPPED : 
			 strStatus = "The service is not running.";
			 break;
		case SERVICE_START_PENDING : 
			 strStatus = "The service is starting.";
			 break;
		case SERVICE_STOP_PENDING:   
			 strStatus = "The service is stopping.";
			 break;
		case SERVICE_RUNNING:
			 strStatus = "The service is running.";
			 break;
		case SERVICE_CONTINUE_PENDING:
			 strStatus = "The service continue is pending.";
			 break;
		case SERVICE_PAUSE_PENDING:
			 strStatus = "The service pause is pending.";
			 break;
		case SERVICE_PAUSED:
			 strStatus = "The service is paused.";
			 break;
		default: 
			 strStatus = "Status Unknown";
			 break;
	}
}

BOOL CServiceManager::SMGetServiceStopStatus(IN ITEMDATA *item)
{
	if (item->nStatus == SERVICE_RUNNING)
		return TRUE;
	else
		return FALSE;
}

BOOL CServiceManager::SMGetServiceStartStatus(IN ITEMDATA *item)
{
	if (item->nStatus == SERVICE_STOPPED)
		return TRUE;
	else
		return FALSE;
}

BOOL CServiceManager::SMInstallService(CString strName, CString strDisplay, CString strPath)
{
	BOOL bRet = TRUE;

	SC_HANDLE schSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
	SC_HANDLE hService = CreateService(
		schSCManager,
		strName,
		strDisplay,
		SERVICE_ALL_ACCESS,
		SERVICE_WIN32_OWN_PROCESS,
		SERVICE_AUTO_START,
		SERVICE_ERROR_IGNORE,
		strPath,
		NULL, NULL, NULL, NULL, NULL);

	if (hService == NULL)
		bRet = FALSE;

	CloseServiceHandle(hService);
	CloseServiceHandle(schSCManager);

	return bRet;
}

void CServiceManager::SMUninstallService(CString strName)
{
	SC_HANDLE schSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    SC_HANDLE hService = OpenService(schSCManager, strName, SERVICE_STOP | DELETE);

    if (hService == NULL)
        return;

    // first stop the service
    SERVICE_STATUS status;
    ControlService(hService, SERVICE_CONTROL_STOP, &status);

	// uninstall the service
    DeleteService(hService);
    
	CloseServiceHandle(hService);
	CloseServiceHandle(schSCManager);
} 

void CServiceManager::SMStartService(CString strName)
{
	SC_HANDLE schSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    SC_HANDLE hService = OpenService(schSCManager, strName, SERVICE_START);

    if (hService == NULL)
        return;

    StartService(hService, 0, NULL);

    CloseServiceHandle(hService);
	CloseServiceHandle(schSCManager);
}

void CServiceManager::SMStopService(CString strName)
{
	SC_HANDLE schSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    SC_HANDLE hService = OpenService(schSCManager, strName, SERVICE_STOP);

    if (hService == NULL)
        return;

    SERVICE_STATUS status;
    ControlService(hService, SERVICE_CONTROL_STOP, &status);
    
	CloseServiceHandle(hService);
	CloseServiceHandle(schSCManager);
}

BOOL CServiceManager::SMIsServiceInstalled(CString strName)
{
	BOOL bRet = TRUE;

	SC_HANDLE schSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    SC_HANDLE hService = OpenService(schSCManager, strName, SERVICE_QUERY_STATUS);

    if (hService == NULL)
    {
		// the service doesn't exits
		bRet = FALSE;
	}

	CloseServiceHandle(hService);
	CloseServiceHandle(schSCManager);

	return bRet;
}

void CServiceManager::SMQueryServiceStatus(CString strName, SERVICE_STATUS& status)
{
	SC_HANDLE schSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    SC_HANDLE hService = OpenService(schSCManager, strName, SERVICE_QUERY_STATUS);

    if (hService == NULL)
        return;

	QueryServiceStatus(hService,&status);

	CloseServiceHandle(hService);
	CloseServiceHandle(schSCManager);
}

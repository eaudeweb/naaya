// ConsoleToolz.cpp: implementation of the CConsoleToolz class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "PTKConsole.h"
#include "ConsoleToolz.h"
#include <malloc.h>

#ifdef _DEBUG
#undef THIS_FILE
static char THIS_FILE[]=__FILE__;
#define new DEBUG_NEW
#endif

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CConsoleToolz::CConsoleToolz()
{

}

CConsoleToolz::~CConsoleToolz()
{

}

BOOL CConsoleToolz::RunningAsAdministrator()
{
	BOOL   fAdmin;
    HANDLE  hThread;
    TOKEN_GROUPS *ptg = NULL;
    DWORD  cbTokenGroups;
    DWORD  dwGroup;
    PSID   psidAdmin;

    SID_IDENTIFIER_AUTHORITY SystemSidAuthority= SECURITY_NT_AUTHORITY;

    // First we must open a handle to the access token for this thread.
    if (!OpenThreadToken(GetCurrentThread(), TOKEN_QUERY, FALSE, &hThread))
    {
        if (GetLastError() == ERROR_NO_TOKEN)
        {
            // If the thread does not have an access token, we'll examine the
            // access token associated with the process.
            if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &hThread))
                return ( FALSE);
        }
        else 
            return ( FALSE);
    }

    // Then we must query the size of the group information associated with
    // the token. Note that we expect a FALSE result from GetTokenInformation
    // because we've given it a NULL buffer. On exit cbTokenGroups will tell
    // the size of the group information.
    if (GetTokenInformation(hThread, TokenGroups, NULL, 0, &cbTokenGroups))
        return (FALSE);

    // Here we verify that GetTokenInformation failed for lack of a large
    // enough buffer.
    if (GetLastError() != ERROR_INSUFFICIENT_BUFFER)
        return (FALSE);

    // Now we allocate a buffer for the group information.
    // Since _alloca allocates on the stack, we don't have
    // to explicitly deallocate it. That happens automatically
    // when we exit this function.
    if (!(ptg = (TOKEN_GROUPS *)_alloca ( cbTokenGroups))) 
        return (FALSE);

    // Now we ask for the group information again.
    // This may fail if an administrator has added this account
    // to an additional group between our first call to
    // GetTokenInformation and this one.
    if (!GetTokenInformation(hThread, TokenGroups, ptg, cbTokenGroups, &cbTokenGroups))
        return (FALSE);

    // Now we must create a System Identifier for the Admin group.
    if (!AllocateAndInitializeSid(&SystemSidAuthority, 2,
            SECURITY_BUILTIN_DOMAIN_RID, DOMAIN_ALIAS_RID_ADMINS,
            0, 0, 0, 0, 0, 0, &psidAdmin))
        return ( FALSE);

    // Finally we'll iterate through the list of groups for this access
    // token looking for a match against the SID we created above.
    fAdmin= FALSE;

    for ( dwGroup= 0; dwGroup < ptg->GroupCount; dwGroup++)
    {
        if ( EqualSid ( ptg->Groups[dwGroup].Sid, psidAdmin))
        {
            fAdmin = TRUE;
            break;
        }
    }

    // Before we exit we must explicity deallocate the SID we created.
    FreeSid (psidAdmin);

    return (fAdmin);
}

void CConsoleToolz::CTReadRegistryKey(CString strRegString, CString strKeyName, CString& strKeyValue)
{
   HKEY hKey;
   char strSn[1024] = "";
   DWORD dwBufLen = 1024;
   LONG lRet;
   if(RegOpenKeyEx(HKEY_LOCAL_MACHINE,
               TEXT(strRegString),
               0,
               KEY_QUERY_VALUE,
               &hKey) != ERROR_SUCCESS)
       return;
   lRet = RegQueryValueEx(hKey,
       TEXT(strKeyName),
       NULL,
       NULL,
       (LPBYTE)strSn,
       &dwBufLen);

   RegCloseKey(hKey);
   strKeyValue.Format("%s", strSn);
}

void CConsoleToolz::CTCreateRegistryKey(CString strRegString, CString strKeyName, CString strKeyValue)
{
   HKEY hKey;
   char* strSn = strKeyValue.GetBuffer(strKeyValue.GetLength());
   strKeyValue.ReleaseBuffer();
   DWORD dwBufLen = strlen(strSn);
   DWORD dwDisposition;
   LONG lRet;
   if(RegOpenKeyEx(HKEY_LOCAL_MACHINE,
               TEXT(strRegString),
               0,
               KEY_SET_VALUE,
               &hKey) != ERROR_SUCCESS)
   {
             if (RegCreateKeyEx(HKEY_LOCAL_MACHINE,
               TEXT(strRegString),
               0,
               TEXT(""),
               REG_OPTION_NON_VOLATILE,
               STANDARD_RIGHTS_WRITE | KEY_SET_VALUE | KEY_CREATE_SUB_KEY,
               NULL,
               &hKey,
               &dwDisposition) != ERROR_SUCCESS)
           return;
       RegCloseKey(hKey);
       if(RegOpenKeyEx(HKEY_LOCAL_MACHINE,
               TEXT(strRegString),
               0,
               KEY_SET_VALUE,
               &hKey) != ERROR_SUCCESS)
           return;
   }
 
   lRet = RegSetValueEx(hKey,
       TEXT(strKeyName),
       NULL,
       REG_SZ,
       (LPBYTE)strSn,
       dwBufLen);
	RegCloseKey(hKey);
}

BOOL CConsoleToolz::CTExistsFile(CString strPath)
{
    HANDLE hFile;
    WIN32_FIND_DATA fileInfo;
    BOOL bRes = FALSE;

    hFile = FindFirstFile(strPath, &fileInfo);
	if (hFile != INVALID_HANDLE_VALUE)
		if (fileInfo.dwFileAttributes != FILE_ATTRIBUTE_DIRECTORY)
			bRes = TRUE;
    FindClose(hFile);
    return bRes;
}

BOOL CConsoleToolz::CTWriteToFile(CString name, CString content)
{
    FILE * stream;
    if ((stream = fopen((LPCTSTR)name, "w+t")) != NULL)
    {
		fwrite(content, sizeof(char), content.GetLength(), stream);
        fclose(stream);
    }
    return TRUE;
}

int CConsoleToolz::CTDeleteFile(CString strFile)
{
    int err = ::DeleteFile(strFile);
    if (err == 0)
        return ::GetLastError();
    return 0;
}

BOOL CConsoleToolz::isAlphanumeric(CString strString)
{
	char c;
	for (int i=0; i<strString.GetLength(); i++)
	{
		c = strString.GetAt(i);
		if (!((c>=48 && c<=57) || (c>=65 && c<=90) || (c>=97 && c<=122)))
			return FALSE;
	}
	return TRUE;
}

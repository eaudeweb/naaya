// WizardToolz.cpp: implementation of the CWizardToolz class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "PTKUninstall.h"
#include "WizardToolz.h"

#include <malloc.h>
#include <Shlwapi.h>

#ifdef _DEBUG
#undef THIS_FILE
static char THIS_FILE[]=__FILE__;
#define new DEBUG_NEW
#endif

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

CWizardToolz::CWizardToolz()
{
    m_wndProgressBar = NULL;
    m_n64CurrentSize = 0;
}

CWizardToolz::~CWizardToolz()
{
    if (m_wndProgressBar)
        m_wndProgressBar = NULL;
}

BOOL CWizardToolz::RunningAsAdministrator()
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

BOOL CWizardToolz::UTReadRegistryKey(CString strRegString, CString strKeyName, CString& strKeyValue)
{
   HKEY hKey;
   char strSn[1024] = "";
   DWORD dwBufLen = 1024;

   // try open key
   if(RegOpenKeyEx(HKEY_LOCAL_MACHINE,
               TEXT(strRegString),
               0,
               KEY_QUERY_VALUE,
               &hKey) != ERROR_SUCCESS)
       return FALSE;

   // get key data
   if (RegQueryValueEx(hKey,
       TEXT(strKeyName),
       NULL,
       NULL,
       (LPBYTE)strSn,
       &dwBufLen) != ERROR_SUCCESS)
	   return FALSE;

   // close key
   RegCloseKey(hKey);

   // save value in a string
   strKeyValue.Format("%s", strSn);

   return TRUE;
}

BOOL CWizardToolz::UTDeleteRegistryKey(CString strKeyName, CString& strError)
{
	if (SHDeleteKey(HKEY_LOCAL_MACHINE, strKeyName) != ERROR_SUCCESS)
	{
		strError.Format(CRString(IDS_FAILED_DELETE_REGKEY), strKeyName);
		return FALSE;
	}

	return TRUE;
}

BOOL CWizardToolz::UTDeleteRegistryValue(CString strKeyName, CString strKeyValue, CString& strError)
{
	if (SHDeleteValue(HKEY_LOCAL_MACHINE, strKeyName, strKeyValue) != ERROR_SUCCESS)
	{
		strError.Format(CRString(IDS_FAILED_DELETE_REGKEY), strKeyName + "\\" + strKeyValue);
		return FALSE;
	}

	return TRUE;
}

unsigned long CWizardToolz::getFolderSize(CString &folderName)
{
	char buffer[1024];
	unsigned long size;
	::GetCurrentDirectory(1024, buffer);

	int ret = ::SetCurrentDirectory(folderName);
	if(ret == 0)
		size = 0;
	else
		size = internalGetFolderSize("init");

	::SetCurrentDirectory(buffer);
	return size;
}

unsigned long CWizardToolz::internalGetFolderSize(CString status)
{
	static unsigned long size;
	if(status == "init")
		size = 0;

	WIN32_FIND_DATA fd;
	HANDLE handle = ::FindFirstFile("*.*", &fd);

	if(handle != INVALID_HANDLE_VALUE){
		do{
			if(fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY){
				CString folderName = fd.cFileName;
				if(folderName != "." && folderName != ".."){
					::SetCurrentDirectory(fd.cFileName);
					internalGetFolderSize();
					::SetCurrentDirectory("..");
				}
			}
			else{
				size += fd.nFileSizeLow;
			}
		} while(::FindNextFile(handle, &fd));
	}
	::FindClose(handle);
	return size;
}

BOOL CWizardToolz::InternalExistsFolder(CString strPath)
{
    HANDLE hFile;
    WIN32_FIND_DATA fileInfo;
    BOOL bRes = FALSE;

    hFile = FindFirstFile(strPath, &fileInfo);
    if (fileInfo.dwFileAttributes == FILE_ATTRIBUTE_DIRECTORY)
        bRes = TRUE;
    FindClose(hFile);
    return bRes;
}

int CWizardToolz::InternalCreateFolder(CString name)
{
    int err = ::CreateDirectory(name, NULL);
    if(err == 0)
        return ::GetLastError();
    return 0;
}

int CWizardToolz::RecDeleteFolder(CString strFolder)
{
	WIN32_FIND_DATA fd;
    HANDLE hp;
	int ret=0;
	char name1[256];
    char *cp;
	
	sprintf(name1, "%s\\*.*", strFolder);
    hp = ::FindFirstFile(name1, &fd);
    if(!hp || hp == INVALID_HANDLE_VALUE)
        return(ret);
    // iterate through all folder content
    do
    {
		cp = fd.cFileName;
        if(cp[1]==0 && *cp=='.')
            continue;
        else if(cp[2]==0 && *cp=='.' && cp[1]=='.')
            continue;
        sprintf(name1,"%s\\%s", strFolder, fd.cFileName);
		if(fd.dwFileAttributes&FILE_ATTRIBUTE_READONLY)
		{
			SetFileAttributes(name1,fd.dwFileAttributes&~FILE_ATTRIBUTE_READONLY);
		}
		if(fd.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)
		{
			TakeOwnership(name1);
			SetPermission(name1,"everyone",GENERIC_ALL);
			RecDeleteFolder(name1);
		}
		else
		{
			TakeOwnership(name1);
			SetPermission(name1,"everyone",GENERIC_ALL);
			DeleteFile(name1);

            // update the progress bar
            UpdateProgressBar(fd.nFileSizeLow);

			// process events
			DoEvents();
		}

    }
    while(FindNextFile(hp,&fd));
	FindClose(hp);
	if(fd.dwFileAttributes&FILE_ATTRIBUTE_READONLY)
	{
		SetFileAttributes(strFolder, fd.dwFileAttributes&~FILE_ATTRIBUTE_READONLY);
	}
	if(RemoveDirectory(strFolder))
	{
		printf("success\n");
		ret=1;
	}	
	else
	{
		printf("error %d\n",GetLastError());
	}
	return(ret);
}

int CWizardToolz::InternalCopyFile(CString srcFile, CString destFile)
{
    int err = ::CopyFile(srcFile, destFile, TRUE);		
    if(err == 0)
        return ::GetLastError();
    return 0;
}

int CWizardToolz::InternalOverwriteFile(CString srcFile, CString destFile)
{
    int err = ::CopyFile(srcFile, destFile, FALSE);		
    if(err == 0)
        return ::GetLastError();
    return 0;
}

BOOL CWizardToolz::TakeOwnership(CString strFile)
{
	int file[256];
	char error[256];
	DWORD description;
	SECURITY_DESCRIPTOR sd;
	SECURITY_INFORMATION info_owner=OWNER_SECURITY_INFORMATION;
		
	TOKEN_USER *owner = (TOKEN_USER*)file;
	HANDLE token;
	
	
	InitializeSecurityDescriptor(&sd,SECURITY_DESCRIPTOR_REVISION);
	if(OpenProcessToken(GetCurrentProcess(),TOKEN_READ | TOKEN_ADJUST_PRIVILEGES,&token))
	{
		//To Get the Current Process Token & opening it to adjust the previleges
		if(SetPrivilege(token,SE_TAKE_OWNERSHIP_NAME,FALSE))
		{
			//Enabling the privilege
			if(GetTokenInformation(token,TokenUser,owner,sizeof(file),&description))
			{
				//Get the information on the opened token
				if(SetSecurityDescriptorOwner(&sd,owner->User.Sid,FALSE))
				{
					//replace any owner information present on the security descriptor
					if(SetFileSecurity(strFile,info_owner,&sd))
						return(TRUE);
					else
					{
						// Call GetLastError to determine whether the function succeeded.
						sprintf(error,"Error in SetFileSecurity Error No : %d",GetLastError());
						MessageBox(NULL,error,NULL,MB_OK);
					}//SetFileSecurity
				}
				else
				{
					sprintf(error,"Error in SetSecurityDescriptorOwner Error No : %d",GetLastError());
					MessageBox(NULL,error,NULL,MB_OK);
				}//SetSecurityDescriptorOwner
			}
			else
			{
				sprintf(error,"Error in GetTokenInformation Error No : %d",GetLastError());
				MessageBox(NULL,error,NULL,MB_OK);
			}//GetTokenInformation
		}
		else
		{
			sprintf(error,"Error in SetPrivilege No : %d",GetLastError());
			MessageBox(NULL,error,NULL,MB_OK);
		}//SetPrivilege
	}
	else
	{
		sprintf(error,"Error in OpenProcessToken No : %d",GetLastError());
		MessageBox(NULL,error,NULL,MB_OK);
	}//OpenProcessToken

	SetPrivilege(token,SE_TAKE_OWNERSHIP_NAME,TRUE);//Disabling the set previlege

	return(FALSE);
}

BOOL CWizardToolz::SetPrivilege(HANDLE hToken,LPCTSTR lpszPrivilege,BOOL bChange)
{
	TOKEN_PRIVILEGES tp;
	LUID luid;
	BOOL bReturnValue = FALSE;

	if (lpszPrivilege != NULL && !bChange)
	{
		if (LookupPrivilegeValue( 
			NULL,            // lookup privilege on local system
			lpszPrivilege,   // privilege to lookup 
			&luid )) 
		{      // receives LUID of privilege
			tp.PrivilegeCount = 1;
			tp.Privileges[0].Luid = luid;
			tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
		}
	}

	AdjustTokenPrivileges(hToken,bChange,&tp,
		sizeof(TOKEN_PRIVILEGES), 
		(PTOKEN_PRIVILEGES) NULL,
		(PDWORD) NULL);  
	// Call GetLastError to determine whether the function succeeded.
	
	if (GetLastError() == ERROR_SUCCESS) 
	{ 
		bReturnValue = TRUE;
	} 
	 
	return bReturnValue;
} 

BOOL CWizardToolz::SetPermission(LPCTSTR lpszFile, LPCTSTR lpszAccess, DWORD dwAccessMask)
{
	int buff[512];
	char domain[512];
	char error[256];
	
	DWORD domain_size=sizeof(domain);
	DWORD acl_size;

	SECURITY_DESCRIPTOR sd1;
	SECURITY_INFORMATION info_dacl=DACL_SECURITY_INFORMATION;
	PSID sid = (PSID*)buff;
	ACL *acl;
	SID_NAME_USE sidname;
	DWORD sid_size=sizeof(buff);
	
	InitializeSecurityDescriptor(&sd1,SECURITY_DESCRIPTOR_REVISION);
	//to get the SID 
	if(LookupAccountName(NULL,lpszAccess,sid,&sid_size,domain,&domain_size,&sidname))
	{
		acl_size=sizeof(ACL)+sizeof(ACCESS_ALLOWED_ACE)-sizeof(DWORD)+GetLengthSid(buff);
		acl = (ACL *)malloc(acl_size);
		//To calculate the size of an ACL, 
		InitializeAcl(acl,acl_size,ACL_REVISION);

		if(AddAccessAllowedAce(acl,ACL_REVISION,dwAccessMask,sid))
		{
			if(SetSecurityDescriptorDacl(&sd1,TRUE,acl,FALSE))
			{
				if(SetFileSecurity(lpszFile,info_dacl,&sd1))
					return(TRUE);
				else
				{
					sprintf(error,"Error in SetFileSecurity Error No : %d",GetLastError());
					MessageBox(NULL,error,NULL,MB_OK);
				}//SetFileSecurity
			}
			else
			{
				sprintf(error,"Error in SetSecurityDescriptorDacl Error No : %d",GetLastError());
				MessageBox(NULL,error,NULL,MB_OK);
			}//SetSecurityDescriptorDacl
		}
		else
		{
			sprintf(error,"Error in AddAccessAllowedAce Error No : %d",GetLastError());
			MessageBox(NULL,error,NULL,MB_OK);
		}//AddAccessAllowedAce
	}
	else
	{
		sprintf(error,"Error in LookupAccountName No : %d",GetLastError());
		MessageBox(NULL,error,NULL,MB_OK);
	}//LookupAccountName

	free(acl);
	return(FALSE);
}

void CWizardToolz::UpdateProgressBar(unsigned long nSize)
{
    m_n64CurrentSize += nSize;
    if (m_n64CurrentSize>m_n64PieceSize)
    {
        m_wndProgressBar->SetPos(m_wndProgressBar->GetPos()+1);
        m_n64CurrentSize = m_n64CurrentSize - m_n64PieceSize;
    }
}

void CWizardToolz::DoEvents()
{
	MSG msg;
	while (::PeekMessage(&msg, NULL, 0, 0, 0))
	{
		if (::GetMessage(&msg, NULL, 0, 0))
		{
			::TranslateMessage(&msg);
			::DispatchMessage(&msg);
		}
		else
		{
			break;
		}
	}
}

void CWizardToolz::UTCreateRegistryKey(CString strRegString, CString strKeyName, CString strKeyValue)
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

// WizardToolz.cpp: implementation of the CWizardToolz class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "PTKInstaller.h"
#include "WizardToolz.h"
#include <afxsock.h>
#include <malloc.h>
#include <intshcut.h>

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

BOOL CWizardToolz::IsCorrectWindowsVersion()
{
	BOOL bRet = TRUE;
	OSVERSIONINFO ovi = { sizeof ovi };

	// determine OS and load appropriate library
	GetVersionEx( &ovi );
	if ( ovi.dwPlatformId == VER_PLATFORM_WIN32_WINDOWS && ovi.dwMajorVersion == 5)
		bRet = FALSE;

	return bRet;
}

BOOL CWizardToolz::TestPortAvailability(UINT nPortNumber)
{
	// Returns true if the port is available, false
	// if there's another application listening on that port
	BOOL nRetCode = TRUE;

	AfxSocketInit();
	CSocket Client;
	// Cannot create a socket on this port
	if(!Client.Create(nPortNumber))
		nRetCode = FALSE;
	// Otherwise close the socket
	else
		Client.Close();

	return nRetCode;
}

CString CWizardToolz::BrowseForFolder(HWND hWnd, LPCSTR plszTitle, UINT nFlags)
{
	CString strResult = "";
 
	LPMALLOC lpMalloc;  // pointer to IMalloc

	if (::SHGetMalloc(&lpMalloc) != NOERROR)
		return strResult; // failed to get allocator

	char szDisplayName[_MAX_PATH];
	char szBuffer[_MAX_PATH];

	BROWSEINFO browseInfo;
	browseInfo.hwndOwner = hWnd;
	// set root at Desktop
	browseInfo.pidlRoot = NULL; 
	browseInfo.pszDisplayName = szDisplayName;
	browseInfo.lpszTitle = plszTitle;   // passed in
	//browseInfo.ulFlags = nFlags;   // also passed in
	browseInfo.ulFlags = BIF_EDITBOX  | BIF_VALIDATE | BIF_RETURNONLYFSDIRS;   // also passed in
	browseInfo.lpfn = NULL;      // not used
	browseInfo.lParam = 0;      // not used   

	LPITEMIDLIST lpItemIDList;

	if ((lpItemIDList = ::SHBrowseForFolder(&browseInfo)) != NULL){
		// Get the path of the selected folder from the
		// item ID list.
		if (::SHGetPathFromIDList(lpItemIDList, szBuffer))
		{
			// At this point, szBuffer contains the path 
			// the user chose.
			if (szBuffer[0] == '\0')
			{
				// SHGetPathFromIDList failed, or
				// SHBrowseForFolder failed.
				AfxMessageBox("Error getting folder",
				MB_ICONSTOP|MB_OK);
				return strResult;
			}

			// We have a path in szBuffer!
			// Return it.
			strResult = szBuffer;
			return strResult;
		}
		else
		{
			AfxMessageBox("Error getting folder",
			MB_ICONSTOP|MB_OK);
			return strResult; // strResult is empty 
		}
		lpMalloc->Free(lpItemIDList);
		lpMalloc->Release();      
	}

	// If we made it this far, SHBrowseForFolder failed.
	return strResult;
}

CString CWizardToolz::GetFreeSpaceForADrive(CString strDrive,unsigned __int64& i64Space)
{
	unsigned __int64 i64FreeBytesToCaller,
                       i64TotalBytes,
                       i64FreeBytes;

	GetDiskFreeSpaceEx (strDrive,  (PULARGE_INTEGER)&i64FreeBytesToCaller,
                (PULARGE_INTEGER)&i64TotalBytes,
                (PULARGE_INTEGER)&i64FreeBytes);
	i64Space = i64FreeBytes;
	char strSpace[1024];
	_i64toa(i64FreeBytes*100/(1024*1024), strSpace, 10);

    //format the string 
    CString strSpaceFormat = strSpace;
    int iLen = strSpaceFormat.GetLength();
    strSpaceFormat = strSpaceFormat.Left(iLen - 2) + "." + strSpaceFormat.Right(2);
	return strSpaceFormat;

}

void CWizardToolz::GetProxyAndPort(CString& strProxy, CString& strPort)
{
    HKEY hKey;
	// Read the Proxy string from the Registry
    if (RegOpenKeyEx(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings", 0, KEY_QUERY_VALUE, &hKey) == ERROR_SUCCESS)
    {
        unsigned char strValue[1024];
        unsigned long ilen = 1024;
        if (RegQueryValueEx(hKey, "ProxyServer" , NULL, &ilen,  strValue, &ilen) == ERROR_SUCCESS)
        {
            CString strValueEx = strValue;
            // The form can be: 
            //      HOST:PORT if the settings are the same for all protocols
            //      PROTOCOL=HOST:PORT;etc...
            int iHTTPpointStart = strValueEx.Find("http=");
            if (iHTTPpointStart != -1)
            {
                // lookup the setting for HTTP
                int iHTTPpointEnd = strValueEx.Find(';', iHTTPpointStart + 1);
                strValueEx = strValueEx.Mid(iHTTPpointStart + 5, iHTTPpointEnd - iHTTPpointStart - 5);
            }
            int ipoint = strValueEx.Find(":");
            if (ipoint < 0)
            {
                strProxy = strValueEx;
                strPort = "";
                return;
            }
			// Get the server name and the port from the value
            strProxy = strValueEx.Left(ipoint);
            strPort = strValueEx.Right(strValueEx.GetLength() - ipoint -1);
        }
    }

}

void CWizardToolz::GetHostInfos(CString& strHostName, int& nIpField0, int& nIpField1, int& nIpField2, int& nIpField3)
{
    char szHostName[256];

    WSADATA wsaData;
    HOSTENT *pHP;
    SOCKADDR_IN myaddr;
    myaddr.sin_family = AF_INET;

    if (SOCKET_ERROR != WSAStartup(0x202, &wsaData)) 
    {
        gethostname(szHostName, 256);
        pHP = gethostbyname(szHostName);
        memcpy((char FAR *)&(myaddr.sin_addr), pHP->h_addr, pHP->h_length);
        
        strHostName = szHostName;
        nIpField0 = myaddr.sin_addr.S_un.S_un_b.s_b1;
        nIpField1 = myaddr.sin_addr.S_un.S_un_b.s_b2;
        nIpField2 = myaddr.sin_addr.S_un.S_un_b.s_b3;
        nIpField3 = myaddr.sin_addr.S_un.S_un_b.s_b4;

        WSACleanup();
    }
    else
    {
        strHostName = "";
        nIpField0 = nIpField1 = nIpField2 = nIpField3 = 0;
    }
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

BOOL CWizardToolz::RecCopyFolder(CString strSource, CString strDestination, CStringArray& arrLog)
{
    char buffer[1024];
    GetCurrentDirectory(1024, buffer);

    // copy folder
    SetCurrentDirectory(strSource);
    if (!InternalRecCopyFolder(strSource, strDestination, arrLog))
    {
        return FALSE;
    }
    SetCurrentDirectory(buffer);

    // add to log
    CString strBuffer;
    strBuffer.Format(CRString(IDS_COPY_DIRECTORY), strDestination);
    arrLog.Add(strBuffer);

    return TRUE;
}

BOOL CWizardToolz::InternalRecCopyFolder(CString src, CString dest, CStringArray& arrLog)
{
    WIN32_FIND_DATA fd;
    HANDLE handle = ::FindFirstFile("*.*", &fd);

    if(handle != INVALID_HANDLE_VALUE)
    {
        // iterate through all folder content
        do
        {
            // if it is a folder, then create it
            // if it is a file, then copy it
            if(fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
            {
                // create folder, ignore . and ..
                CString folderName = fd.cFileName;
                if(folderName != "." && folderName != "..")
                {
                    CString srcFolder = src + "\\" + fd.cFileName;
                    CString destFolder = dest + "\\" + fd.cFileName;
                    ::SetCurrentDirectory(fd.cFileName);
                    if (InternalCreateFolder(destFolder) == 0)
                    {
                        /*
                        // update label
                        CDiGIRInstallDlg dlgInstall;
                        CString strTmp = "From ";   
                        strTmp += fd.cFileName;
                        strTmp += "  to  ";
                        strTmp += fd.cFileName;
                        dlgInstall.m_InstallationFiles.SetWindowText(strTmp);
                        */
                        InternalRecCopyFolder(srcFolder, destFolder, arrLog);
                    }
                    else
                    {
                        // add to log
                        CString strBuffer;
                        strBuffer.Format(CRString(IDS_FAILED_COPY_DIRECTORY), destFolder);
                        arrLog.Add(strBuffer);
                        return FALSE;
                        
                    }
                    ::SetCurrentDirectory("..");

                    // add to log
                    CString strBuffer;
                    strBuffer.Format(CRString(IDS_COPY_DIRECTORY), destFolder);
                    arrLog.Add(strBuffer);
                }
            }
            // file
            else
            {
                // copy file
                CString srcFile = src + "\\" + fd.cFileName;
                CString destFile = dest + "\\" + fd.cFileName;
                int ret = InternalCopyFile(srcFile, destFile);
                if (ret != 0)
                {
                    // add to log
                    CString strBuffer;
                    strBuffer.Format(CRString(IDS_FAILED_COPY_FILE), destFile);
                    arrLog.Add(strBuffer);
                    return FALSE;
                }

                // update progress bar
                UpdateProgressBar(fd.nFileSizeLow);

				// process events
				DoEvents();
            }
        } while(::FindNextFile(handle, &fd));
    }
    ::FindClose(handle);

    return TRUE;
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

BOOL CWizardToolz::InternalExistsFile(CString strPath)
{
    HANDLE hFile;
    WIN32_FIND_DATA fileInfo;
    BOOL bRes = FALSE;

    hFile = FindFirstFile(strPath, &fileInfo);
    if (fileInfo.dwFileAttributes != FILE_ATTRIBUTE_DIRECTORY)
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

int CWizardToolz::InternalCreateChainFolders(CString strPath)
{
    CStringArray arrDirs;
    BOOL bRes;
    int i;
    CString strBuffer;

    if (InternalExistsFolder(strPath))
        return 1;

    arrDirs.RemoveAll();
    for (i=0; i<strPath.GetLength(); i++)
    {
        if (strPath.GetAt(i) != '\\')
            strBuffer += strPath.GetAt(i);
        else
        {
            arrDirs.Add(strBuffer);
            strBuffer += "\\";
        }
        if (i == strPath.GetLength()-1)
            arrDirs.Add(strBuffer);
    }


    for (i=1; i<arrDirs.GetSize(); i++)
    {
        strBuffer = arrDirs.GetAt(i);
        bRes = InternalCreateFolder(strBuffer);
        if (bRes)
            SetFileAttributes(strPath, FILE_ATTRIBUTE_NORMAL);
    }
    arrDirs.RemoveAll();

    if (InternalExistsFolder(strPath))
        return 1;
    else
        return 0;
}

BOOL CWizardToolz::InternalCreateFile(CString name)
{
    HANDLE hFile;

    hFile = CreateFile(name,   // open file
        GENERIC_WRITE,                // open for writing 
        0,                            // do not share 
        NULL,                         // no security 
        CREATE_ALWAYS,                  // open or create 
        FILE_ATTRIBUTE_NORMAL,        // normal file 
        NULL);                        // no attr. template 

    if (hFile == INVALID_HANDLE_VALUE) 
    { 
        return FALSE;
    }

    CloseHandle(hFile);
    return TRUE;
}

int CWizardToolz::InternalCopyFile(CString srcFile, CString destFile)
{
    int err = ::CopyFile(srcFile, destFile, TRUE);		
    if(err == 0)
        return ::GetLastError();
	else
		::SetFileAttributes(destFile,FILE_ATTRIBUTE_NORMAL);
    return 0;
}

int CWizardToolz::InternalOverwriteFile(CString srcFile, CString destFile)
{
    int err = ::CopyFile(srcFile, destFile, FALSE);		
    if(err == 0)
        return ::GetLastError();
    return 0;
}

int CWizardToolz::InternalMoveFile(CString srcFile, CString destFile)
{
    int err = ::MoveFile(srcFile, destFile);		
    if(err == 0)
        return ::GetLastError();
    return 0;
}

int CWizardToolz::InternalDeleteFile(CString strFile)
{
    int err = ::DeleteFile(strFile);
    if (err == 0)
        return ::GetLastError();
    return 0;
}

BOOL CWizardToolz::InternalWriteToFile(CString name, CStringArray& arrLog)
{
    FILE * stream;
    if ((stream = fopen((LPCTSTR)name, "a+t")) != NULL)
    {
        CString strLogItem;
        for (int i=0; i<arrLog.GetSize(); i++)
        {
            strLogItem = arrLog.ElementAt(i);
            fwrite( strLogItem , sizeof( char ), strLogItem.GetLength(), stream );
            fwrite( "\n" , sizeof( char ), 1, stream );
        }
        fclose(stream);
    }

    return TRUE;
}

BOOL CWizardToolz::ReadFileContent(CString strFile, CString& strFileContent, CStringArray& arrLog)
{
    HANDLE hFile;

    DWORD  dwBytesRead; 
 
    char buff[1024];

    strFileContent = "";

    hFile = CreateFile(strFile,     // open file
        GENERIC_READ,                 // open for reading 
        0,                            // do not share 
        NULL,                         // no security 
        OPEN_EXISTING,                // existing file only 
        FILE_ATTRIBUTE_NORMAL,        // normal file 
        NULL);                        // no attr. template 

    if (hFile == INVALID_HANDLE_VALUE) 
    { 
        CString strBuffer;
        strBuffer.Format(CRString(IDS_ERROR_OPEN_FILE), strFile);
        arrLog.Add(strBuffer);
        return FALSE;
    }

    do
    {
        if (ReadFile(hFile, buff, 1024, &dwBytesRead, NULL))
        {
            buff[dwBytesRead] = '\0';
            strFileContent += buff;
        }
    } while (dwBytesRead == 1024); 
    
    CloseHandle(hFile);

    return TRUE;
}

BOOL CWizardToolz::WriteFileContent(CString strFile, CString strFileContent, CStringArray& arrLog)
{
    HANDLE hFile;

    DWORD dwBytesWritten;

    hFile = CreateFile(strFile,   // open file
        GENERIC_WRITE,                // open for writing 
        0,                            // do not share 
        NULL,                         // no security 
        CREATE_ALWAYS,                // open or create 
        FILE_ATTRIBUTE_NORMAL,        // normal file 
        NULL);                        // no attr. template 

    if (hFile == INVALID_HANDLE_VALUE) 
    { 
        CString strBuffer;
        strBuffer.Format(CRString(IDS_ERROR_OPEN_FILE), strFile);
        arrLog.Add(strBuffer);
        return FALSE;
    }
    
    WriteFile(hFile, strFileContent, (DWORD)strFileContent.GetLength(), &dwBytesWritten, NULL); 

    CloseHandle(hFile);

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

BOOL CWizardToolz::CreateShortcut(CString strFileDirectory, CString strFilePath, CString strDestPath)
{
    BOOL bRet = FALSE;
    IShellLink* psl;

	if (SUCCEEDED(CoCreateInstance(CLSID_ShellLink,
							NULL,
							CLSCTX_INPROC_SERVER,
							IID_IShellLink,
							(LPVOID*) &psl))
					)
    {
        IPersistFile* ppf;

        // set file path
        psl->SetPath(strFilePath);

        // set the working directory
        psl->SetWorkingDirectory(strFileDirectory);
        
        // set icon
        //psl->SetIconLocation(strFileDirectory + "\\digir.ico", 0);

        // minimize windowd when starts
        psl->SetShowCmd(SW_SHOWNORMAL);

		if (SUCCEEDED(psl->QueryInterface( IID_IPersistFile, (LPVOID *) &ppf)))
		{

			WORD wsz[MAX_PATH];
			MultiByteToWideChar(CP_ACP, 
								MB_PRECOMPOSED, 
								strDestPath, 
								-1, 
								wsz,
								MAX_PATH);

			if ( SUCCEEDED ( ppf->Save(wsz, TRUE) ) )
				bRet = TRUE;

			ppf->Release();
		}
		psl->Release();
	}
	return bRet;
}

BOOL CWizardToolz::CreateInternetShortcut(LPCSTR pszURL, LPCSTR pszURLfilename, LPCSTR szDescription,LPCTSTR szIconFile,int nIndex)
{
	BOOL bRet = FALSE;
	HRESULT hres;
	IUniformResourceLocator* pHook;

	if (SUCCEEDED (hres = CoCreateInstance (CLSID_InternetShortcut, NULL, CLSCTX_INPROC_SERVER, 
		IID_IUniformResourceLocator, (void **)&pHook))
		)
	 {
	  IPersistFile *ppf;
	  IShellLink *psl;

	  // Query IShellLink for the IPersistFile interface for 
	  hres = pHook->QueryInterface (IID_IPersistFile, (void **)&ppf);
	  hres = pHook->QueryInterface (IID_IShellLink, (void **)&psl);

	  if (SUCCEEDED (hres))
	  { 
	   WORD wsz [MAX_PATH]; // buffer for Unicode string

	   // Set the path to the shortcut target.
	   pHook->SetURL(pszURL,0);

	   hres = psl->SetIconLocation(szIconFile,nIndex);

	   if (SUCCEEDED (hres))
	   {
		// Set the description of the shortcut.
		hres = psl->SetDescription (szDescription);

		if (SUCCEEDED (hres))
		{
		 // Ensure that the string consists of ANSI characters.
		 MultiByteToWideChar (CP_ACP, 0, pszURLfilename, -1, wsz, MAX_PATH);

		 // Save the shortcut via the IPersistFile::Save member function.
		 hres = ppf->Save (wsz, TRUE);
		}
	   }

	   // Release the pointer to IPersistFile.
	   ppf->Release ();
	   psl->Release ();
	  }

	  // Release the pointer to IShellLink.
	  pHook->Release ();
	
	  bRet = TRUE;
	 }
	 return bRet;
}

void CWizardToolz::UpdateProgressBar(unsigned long nSize)
{
    m_n64CurrentSize += nSize;
    if (m_n64CurrentSize>m_pWizardData->m_n64PieceSize)
    {
        m_wndProgressBar->SetPos(m_wndProgressBar->GetPos()+1);
        m_n64CurrentSize = m_n64CurrentSize - m_pWizardData->m_n64PieceSize;
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

/*******************************************************************************
* FUNCTION : TakeOwnership
* PURPOSE  : This function is used to take the Owneship of a specified file
* RETURNS  : TRUE, if the function succeeds, else FALSE
********************************************************************************/
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

/*******************************************************************************
* FUNCTION : SetPrivilege
* PURPOSE : This function is used to enable or disable the privileges of a user
* INPUT    : hToken       :handle of the user token
*            lpszPrivilege:name of the privilege to be set
*            bChange      :if this flag is FALSE, then it enables the specified
*                          privilege. Otherwise It disables all privileges.
* RETURNS  : TRUE, if the function succeeds, else FALSE
********************************************************************************/
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

/*******************************************************************************
* FUNCTION : SetPermission
* PURPOSE : This function is used to the Permissions of a file
* INPUT    : lpszFile	  :name of the file for which permissions are to be set
*            lpszAccess   :Access rights for the specified file.
*            dwAccessMask :access rights to be granted to the specified SID              
* RETURNS  : TRUE, if the function succeeds, else FALSE
********************************************************************************/
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

BOOL CWizardToolz::isAlphanumeric(CString strString)
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

HANDLE CWizardToolz::launchViaShellExecute(LPCTSTR program, LPCTSTR args, LPCTSTR directory, int nShow)
{
    HANDLE hProcess = NULL;
    SHELLEXECUTEINFO shellInfo;
    ::ZeroMemory(&shellInfo, sizeof(shellInfo));
    shellInfo.cbSize = sizeof(shellInfo);
    shellInfo.nShow = nShow;
    shellInfo.fMask = SEE_MASK_FLAG_NO_UI | SEE_MASK_NOCLOSEPROCESS;
    shellInfo.lpFile = program;
    shellInfo.lpParameters = args;
    shellInfo.lpDirectory = directory;
    if(::ShellExecuteEx(&shellInfo))
		hProcess = shellInfo.hProcess;
    return hProcess;
}

BOOL CWizardToolz::ExistsRegistryKey(CString strKeyName)
{
	HKEY hKey;
	char strSn[1024] = "";
	DWORD dwBufLen = 1024;

    // try open key
    if(RegOpenKeyEx(HKEY_LOCAL_MACHINE,
               TEXT(strKeyName),
               0,
               KEY_QUERY_VALUE,
               &hKey) != ERROR_SUCCESS)
       return FALSE;

    // close key
    RegCloseKey(hKey);

	return TRUE;
}

BOOL CWizardToolz::ReadRegistryKey(CString strRegString, CString strKeyName, CString& strKeyValue)
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

void CWizardToolz::CreateRegistryKey(CString strRegString, CString strKeyName, CString strKeyValue)
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
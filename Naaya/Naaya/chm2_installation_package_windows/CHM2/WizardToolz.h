// WizardToolz.h: interface for the CWizardToolz class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_WIZARDTOOLZ_H__5D40CB45_AD3C_40F7_831C_70290C64C17E__INCLUDED_)
#define AFX_WIZARDTOOLZ_H__5D40CB45_AD3C_40F7_831C_70290C64C17E__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "WizardData.h"

class CWizardToolz  
{
public:
	CWizardToolz();
	virtual ~CWizardToolz();

public:
	BOOL IsCorrectWindowsVersion();
	BOOL TestPortAvailability(UINT);
    BOOL RunningAsAdministrator();
    BOOL TakeOwnership(CString strFile);
    BOOL SetPrivilege(HANDLE hToken,LPCTSTR lpszPrivilege,BOOL bChange);
    BOOL SetPermission(LPCTSTR lpszFile, LPCTSTR lpszAccess, DWORD dwAccessMask);	
	BOOL CreateShortcut(CString, CString, CString);
	BOOL CreateInternetShortcut(LPCSTR, LPCSTR, LPCSTR, LPCTSTR = NULL,int = -1);

	static CString BrowseForFolder(HWND, LPCSTR, UINT);
	static CString GetFreeSpaceForADrive(CString, unsigned __int64&);
    static void GetProxyAndPort(CString& strProxy, CString& strPort);
    static void GetHostInfos(CString&, int&, int&, int&, int&);

    BOOL RecCopyFolder(CString, CString, CStringArray&);
    BOOL InternalRecCopyFolder(CString, CString, CStringArray&);
	BOOL InternalExistsFile(CString);
	BOOL InternalExistsFolder(CString);
    int InternalCreateFolder(CString);
    int InternalCreateChainFolders(CString);
	int RecDeleteFolder(CString);
	BOOL InternalCreateFile(CString);
	int InternalCopyFile(CString, CString);
	int InternalOverwriteFile(CString, CString);
	int InternalMoveFile(CString srcFile, CString destFile);
	int InternalDeleteFile(CString);
	BOOL InternalWriteToFile(CString, CStringArray&);
    BOOL ReadFileContent(CString, CString&, CStringArray&);
    BOOL WriteFileContent(CString, CString, CStringArray&);

    unsigned long getFolderSize(CString&);
    unsigned long internalGetFolderSize(CString status = "");

	void UpdateProgressBar(unsigned long);
	void DoEvents();

	BOOL isAlphanumeric(CString);

	HANDLE launchViaShellExecute(LPCTSTR, LPCTSTR, LPCTSTR, int);

	BOOL ExistsRegistryKey(CString strKeyName);
	BOOL ReadRegistryKey(CString, CString, CString&);
	void CreateRegistryKey(CString, CString, CString);

public:
    CWizardData* m_pWizardData;
    CProgressCtrl* m_wndProgressBar;
    unsigned __int64 m_n64CurrentSize;
};

#endif // !defined(AFX_WIZARDTOOLZ_H__5D40CB45_AD3C_40F7_831C_70290C64C17E__INCLUDED_)

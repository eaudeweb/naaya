// UninsToolz.h: interface for the CUninsToolz class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_UNINSTOOLZ_H__E6033ABC_CC8D_416E_9E74_3061541412A7__INCLUDED_)
#define AFX_UNINSTOOLZ_H__E6033ABC_CC8D_416E_9E74_3061541412A7__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class CUninsToolz  
{
public:
	CUninsToolz();
	virtual ~CUninsToolz();

public:
    BOOL RunningAsAdministrator();
	BOOL TakeOwnership(CString strFile);
	BOOL SetPrivilege(HANDLE hToken,LPCTSTR lpszPrivilege,BOOL bChange);
	BOOL SetPermission(LPCTSTR lpszFile, LPCTSTR lpszAccess, DWORD dwAccessMask);

	BOOL UTReadRegistryKey(CString strRegString, CString strKeyName, CString& strKeyValue);
	BOOL UTDeleteRegistryKey(CString strKeyName, CString& strError);
	BOOL UTDeleteRegistryValue(CString strKeyName, CString strKeyValue, CString& strError);
	void UTCreateRegistryKey(CString strRegString, CString strKeyName, CString strKeyValue);

    unsigned long getFolderSize(CString&);
    unsigned long internalGetFolderSize(CString status = "");
	BOOL InternalExistsFolder(CString strPath);
	int InternalCreateFolder(CString name);
	int RecDeleteFolder(CString strFolder);
	int InternalCopyFile(CString srcFile, CString destFile);
	int InternalOverwriteFile(CString srcFile, CString destFile);

	void UpdateProgressBar(unsigned long nSize);
	void DoEvents();
public:
    CProgressCtrl* m_wndProgressBar;
    unsigned __int64 m_n64CurrentSize;
	unsigned __int64 m_n64TotalSize;
	unsigned __int64 m_n64PieceSize;
};

#endif // !defined(AFX_UNINSTOOLZ_H__E6033ABC_CC8D_416E_9E74_3061541412A7__INCLUDED_)

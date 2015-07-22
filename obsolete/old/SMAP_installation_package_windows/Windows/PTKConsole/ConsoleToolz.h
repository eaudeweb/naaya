// ConsoleToolz.h: interface for the CConsoleToolz class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_CONSOLETOOLZ_H__5A6BE5BA_0332_4F4D_A3D9_8ACC56809092__INCLUDED_)
#define AFX_CONSOLETOOLZ_H__5A6BE5BA_0332_4F4D_A3D9_8ACC56809092__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class CConsoleToolz  
{
public:
	CConsoleToolz();
	virtual ~CConsoleToolz();

public:
	BOOL RunningAsAdministrator();
	void CTCreateRegistryKey(CString, CString, CString);
	void CTReadRegistryKey(CString, CString, CString&);
	BOOL CTExistsFile(CString strPath);
	BOOL CTWriteToFile(CString name, CString content);
	int CTDeleteFile(CString strFile);
	BOOL isAlphanumeric(CString strString);
};

#endif // !defined(AFX_CONSOLETOOLZ_H__5A6BE5BA_0332_4F4D_A3D9_8ACC56809092__INCLUDED_)

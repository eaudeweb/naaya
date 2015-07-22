// TabAbout.cpp : implementation file
//

#include "stdafx.h"
#include "PTKConsole.h"
#include "TabAbout.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CTabAbout dialog


CTabAbout::CTabAbout(CWnd* pParent /*=NULL*/)
	: CDialog(CTabAbout::IDD, pParent)
{
	//{{AFX_DATA_INIT(CTabAbout)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CTabAbout::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CTabAbout)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CTabAbout, CDialog)
	//{{AFX_MSG_MAP(CTabAbout)
		// NOTE: the ClassWizard will add message map macros here
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CTabAbout message handlers

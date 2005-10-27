// TabService.cpp : implementation file
//

#include "stdafx.h"
#include "CHM2Console.h"
#include "TabService.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CTabService dialog


CTabService::CTabService(CWnd* pParent /*=NULL*/)
	: CDialog(CTabService::IDD, pParent)
{
	//{{AFX_DATA_INIT(CTabService)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CTabService::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CTabService)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CTabService, CDialog)
	//{{AFX_MSG_MAP(CTabService)
		// NOTE: the ClassWizard will add message map macros here
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CTabService message handlers

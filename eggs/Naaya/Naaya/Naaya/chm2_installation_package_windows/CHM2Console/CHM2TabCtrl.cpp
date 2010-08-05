// CHM2TabCtrl.cpp : implementation file
//

#include "stdafx.h"
#include "CHM2Console.h"
#include "CHM2TabCtrl.h"

#include "TabService.h"
#include "TabZope.h"
#include "TabAbout.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CCHM2TabCtrl

CCHM2TabCtrl::CCHM2TabCtrl()
{
	m_tabPages[0] = new CTabService;
	m_tabPages[1] = new CTabZope;
	m_tabPages[2] = new CTabAbout;

	m_nNumberOfPages = 3;
}

CCHM2TabCtrl::~CCHM2TabCtrl()
{
	for(int nCount=0; nCount < m_nNumberOfPages; nCount++)
	{
		delete m_tabPages[nCount];
	}
}

void CCHM2TabCtrl::Init()
{
	m_tabCurrent = 0;

	m_tabPages[0]->Create(IDD_TAB_SERVICE, this);
	m_tabPages[1]->Create(IDD_TAB_ZOPE, this);
	m_tabPages[2]->Create(IDD_TAB_ABOUT, this);
	
	m_tabPages[0]->ShowWindow(SW_SHOW);
	m_tabPages[1]->ShowWindow(SW_HIDE);
	m_tabPages[2]->ShowWindow(SW_HIDE);

	SetRectangle();
}

void CCHM2TabCtrl::SetRectangle()
{
	CRect tabRect, itemRect;
	int nX, nY, nXc, nYc;

	GetClientRect(&tabRect);
	GetItemRect(0, &itemRect);

	nX=itemRect.left;
	nY=itemRect.bottom+1;
	nXc=tabRect.right-itemRect.left-1;
	nYc=tabRect.bottom-nY-1;

	m_tabPages[0]->SetWindowPos(&wndTop, nX, nY, nXc, nYc, SWP_SHOWWINDOW);
	for(int nCount=1; nCount < m_nNumberOfPages; nCount++){
		m_tabPages[nCount]->SetWindowPos(&wndTop, nX, nY, nXc, nYc, SWP_HIDEWINDOW);
	}
}

BEGIN_MESSAGE_MAP(CCHM2TabCtrl, CTabCtrl)
	//{{AFX_MSG_MAP(CCHM2TabCtrl)
	ON_WM_LBUTTONDOWN()
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CCHM2TabCtrl message handlers

void CCHM2TabCtrl::OnLButtonDown(UINT nFlags, CPoint point) 
{
	CTabCtrl::OnLButtonDown(nFlags, point);

	if(m_tabCurrent != GetCurFocus()){
		m_tabPages[m_tabCurrent]->ShowWindow(SW_HIDE);
		m_tabCurrent=GetCurFocus();
		m_tabPages[m_tabCurrent]->ShowWindow(SW_SHOW);
		m_tabPages[m_tabCurrent]->SetFocus();
	}
}

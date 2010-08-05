// TabZope.cpp : implementation file
//

#include "stdafx.h"
#include "PTKConsole.h"
#include "TabZope.h"

#include "PTKConsoleDlg.h"
#include "ServiceManager.h"
#include "ZEUDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CTabZope dialog


CTabZope::CTabZope(CWnd* pParent /*=NULL*/)
	: CDialog(CTabZope::IDD, pParent)
{
	//{{AFX_DATA_INIT(CTabZope)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CTabZope::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CTabZope)
	DDX_Control(pDX, IDC_APPLY_BUTTON, m_btnApply);
	DDX_Control(pDX, IDC_STARTTYPE_COMBO, m_cbxStartType);
	DDX_Control(pDX, IDC_PATH_EDIT, m_edtPath);
	DDX_Control(pDX, IDC_NAME_STATIC, m_stcName);
	DDX_Control(pDX, IDC_DISPLAY_STATIC, m_stcDisplay);
	DDX_Control(pDX, IDOK, m_btnStart);
	DDX_Control(pDX, IDCANCEL, m_btnStop);
	DDX_Control(pDX, IDC_STATUS_STATIC, m_stcStatus);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CTabZope, CDialog)
	//{{AFX_MSG_MAP(CTabZope)
	ON_WM_TIMER()
	ON_WM_SHOWWINDOW()
	ON_CBN_SELCHANGE(IDC_STARTTYPE_COMBO, OnSelchangeStarttypeCombo)
	ON_BN_CLICKED(IDC_APPLY_BUTTON, OnApplyButton)
	ON_BN_CLICKED(ID_EMERGENCYUSER, OnEmergencyUser)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CTabZope message handlers

void CTabZope::OnOK() 
{
	((CPTKConsoleDlg*)GetParent())->m_pServiceManager->SMStartService(CRString(IDS_SERVICE_NAME_ZOPE));
}

void CTabZope::OnCancel() 
{
	((CPTKConsoleDlg*)GetParent())->m_pServiceManager->SMStopService(CRString(IDS_SERVICE_NAME_ZOPE));
}

BOOL CTabZope::OnInitDialog() 
{
	CDialog::OnInitDialog();
	
	// empty controls values
	m_stcName.SetWindowText("");
	m_stcDisplay.SetWindowText("");
	m_edtPath.SetWindowText("");
	m_stcStatus.SetWindowText("");
	m_btnStart.EnableWindow(FALSE);
	m_btnStop.EnableWindow(FALSE);

	// add items to combo
	m_cbxStartType.AddString("Automatic");	// index == 0
	m_cbxStartType.AddString("Manual");		// index == 1

	// disable apply button
	m_btnApply.EnableWindow(FALSE);

	SetTimer(1, 500, 0);

	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CTabZope::OnTimer(UINT nIDEvent) 
{
	CDialog::OnTimer(nIDEvent);

	// get information about the Zope service
	GetServiceData();

	// setservice startup type
	if (m_cbxStartType.GetCurSel() == CB_ERR)
	{
		SetCurSelStartupType();
	}
}

void CTabZope::OnShowWindow(BOOL bShow, UINT nStatus) 
{
	if (bShow == TRUE)
	{
		GetServiceData();

		SetCurSelStartupType();
	}

	CDialog::OnShowWindow(bShow, nStatus);
}

void CTabZope::OnSelchangeStarttypeCombo() 
{
	m_btnApply.EnableWindow(TRUE);
}

void CTabZope::OnApplyButton() 
{
	CServiceManager* pServiceManager = ((CPTKConsoleDlg*)GetParent())->m_pServiceManager;
	CString strError;

	// change service type
	int nStartupType = (m_cbxStartType.GetCurSel()==1) ? SERVICE_DEMAND_START:SERVICE_AUTO_START;
	BOOL bResult = pServiceManager->SMChangeServiceConfig(CRString(IDS_SERVICE_NAME_ZOPE), nStartupType, strError);
	if (!bResult)
	{
		AfxMessageBox(strError);
	}

	GetServiceData();
	
	SetCurSelStartupType();
}

void CTabZope::GetServiceData()
{
	CServiceManager* pServiceManager = ((CPTKConsoleDlg*)GetParent())->m_pServiceManager;

	// get Zope service information
	pServiceManager->QueryService(CRString(IDS_SERVICE_NAME_ZOPE), &m_itemData);
	pServiceManager->QueryServiceByDisplay(CRString(IDS_SERVICE_DISPLAY_ZOPE), &m_itemData);
	CString strServiceStatus;
	pServiceManager->SMGetServiceStatusMeaning(&m_itemData, strServiceStatus);

	// update dialog controls
	m_stcName.SetWindowText(m_itemData.strServiceName);
	m_stcDisplay.SetWindowText(m_itemData.strDisplayName);
	m_edtPath.SetWindowText(m_itemData.strBinaryPath);
	m_stcStatus.SetWindowText(strServiceStatus);
	m_btnStart.EnableWindow(pServiceManager->SMGetServiceStartStatus(&m_itemData));
	m_btnStop.EnableWindow(pServiceManager->SMGetServiceStopStatus(&m_itemData));
}

void CTabZope::SetCurSelStartupType()
{
	switch (m_itemData.nStartupType)
	{
		case SERVICE_AUTO_START:
			m_cbxStartType.SetCurSel(0);
			break;
		case SERVICE_DEMAND_START:
			m_cbxStartType.SetCurSel(1);
			break;
		default:
			m_cbxStartType.SetCurSel(-1);
	}
	m_btnApply.EnableWindow(FALSE);
}

void CTabZope::OnEmergencyUser() 
{
	CZEUDlg dlg;
	dlg.DoModal();
}

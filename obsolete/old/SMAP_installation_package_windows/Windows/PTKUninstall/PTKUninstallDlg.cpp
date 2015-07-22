// PTKUninstallDlg.cpp : implementation file
//

#include "stdafx.h"
#include "PTKUninstall.h"
#include "PTKUninstallDlg.h"

#include "WizardToolz.h"
#include "ServiceManager.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CAboutDlg dialog used for App About

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// Dialog Data
	//{{AFX_DATA(CAboutDlg)
	enum { IDD = IDD_ABOUTBOX };
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAboutDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	//{{AFX_MSG(CAboutDlg)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
	//{{AFX_DATA_INIT(CAboutDlg)
	//}}AFX_DATA_INIT
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAboutDlg)
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
	//{{AFX_MSG_MAP(CAboutDlg)
		// No message handlers
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CPTKUninstallDlg dialog

CPTKUninstallDlg::CPTKUninstallDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CPTKUninstallDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CPTKUninstallDlg)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);

	m_bUninstallOK = FALSE;

	m_Brush.CreateSolidBrush(RGB(255, 255, 255));

	m_fontTitle.CreateFont(-14, 0, 0, 0, 
		FW_BOLD, FALSE, FALSE, 0, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, 
		CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH, _T("MS Sans Serif"));
}

void CPTKUninstallDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CPTKUninstallDlg)
	DDX_Control(pDX, IDC_UNINSTALL_SUMMARY_EDIT, m_edtSummary);
	DDX_Control(pDX, IDC_UNINSTALL_PROGRESS, m_prgUninstall);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CPTKUninstallDlg, CDialog)
	//{{AFX_MSG_MAP(CPTKUninstallDlg)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_WM_CTLCOLOR()
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CPTKUninstallDlg message handlers

BOOL CPTKUninstallDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		CString strAboutMenu;
		strAboutMenu.LoadString(IDS_ABOUTBOX);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	GetDlgItem(IDC_TITLE)->SetFont(&m_fontTitle, TRUE);

	// load data and build summary
	CWizardToolz toolz;
	CString strRegString = "SOFTWARE\\" +
		CRString(IDS_REGCOMPANY) + "\\" + 
		CRString(IDS_REGAPPLICATION) + "\\";
	CString strApplicationFolderPath;

	toolz.UTReadRegistryKey(strRegString, CRString(IDS_REGAPPLICATIONPATH), strApplicationFolderPath);
	m_strZopePath = strApplicationFolderPath + CRString(IDS_FOLDER_ZOPE);
	m_strInstancePath = strApplicationFolderPath + CRString(IDS_FOLDER_INSTANCE);
	m_strBinPath = strApplicationFolderPath + CRString(IDS_FOLDER_BIN);
	m_strBackupPath = strApplicationFolderPath + CRString(IDS_FOLDER_BACKUP);

	// get the folder in Start Menu -> Programs 
	char szBuffer[_MAX_PATH];
	::SHGetSpecialFolderPath(NULL, szBuffer, CSIDL_COMMON_PROGRAMS, 0);
	m_strStartMenuFolderPath.Format("%s\\%s", szBuffer, CRString(IDS_MENU_FOLDER_NAME));

	// build key name
	m_strRegApplicationKey = "SOFTWARE\\" +
		CRString(IDS_REGCOMPANY) + "\\" + 
		CRString(IDS_REGAPPLICATION);

	CString strSummary, strBuffer;

	// intro text
	strSummary += CRString(IDS_UNINSTALL_INFO);

	// remove services info
	strSummary += CRString(IDS_STOPREMOVE_SERVICES);
	strBuffer.Format(CRString(IDS_STOPREMOVE_SERVICE), CRString(IDS_SERVICE_NAME_ZOPE));
	strSummary += strBuffer;

	// backup data
	strBuffer.Format(CRString(IDS_BACKUP_FILES), m_strBackupPath);
	strSummary += strBuffer;
	strBuffer.Format(CRString(IDS_BACKUP_FILE), m_strZopePath + "\\var\\data.fs");
	strSummary += strBuffer;

	// remove folders info
	strSummary += CRString(IDS_REMOVE_FOLDERS);
	strBuffer.Format(CRString(IDS_REMOVE_FOLDER), m_strZopePath);
	strSummary += strBuffer;
	strBuffer.Format(CRString(IDS_REMOVE_FOLDER), m_strInstancePath);
	strSummary += strBuffer;
	strBuffer.Format(CRString(IDS_REMOVE_FOLDER), m_strBinPath);
	strSummary += strBuffer;

	// remove shortcuts
	strBuffer.Format(CRString(IDS_REMOVE_SHORTCUTS), m_strStartMenuFolderPath);
	strSummary += strBuffer;

	// remove from registry
	strBuffer.Format(CRString(IDS_REMOVE_REGKEY), m_strRegApplicationKey);
	strSummary += strBuffer;

	strBuffer.Format(CRString(IDS_REMOVE_REGKEY), "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment\\ANTIWORDHOME");
	strSummary += strBuffer;

	m_edtSummary.SetWindowText(strSummary);
	
	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CPTKUninstallDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialog::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CPTKUninstallDlg::OnPaint() 
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, (WPARAM) dc.GetSafeHdc(), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

// The system calls this to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CPTKUninstallDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

void CPTKUninstallDlg::OnOK() 
{
	if (!m_bUninstallOK)
	{
		// PERFORM UNINSTALL
		GetDlgItem(IDCANCEL)->EnableWindow(FALSE);
		GetDlgItem(IDOK)->EnableWindow(FALSE);
		m_edtSummary.SetWindowText("");

		// start uninstall
		UpdateSummary("The uninstall started...\r\n");

		CString strError;

		// stop and uninstall services
		UpdateSummary("\r\nStop and remove services...\r\n");
		if (!StopUninstallServices(strError))
		{
			//UpdateSummary(strError);
		}

		// backup files
		UpdateSummary("\r\nBackup files...\r\n");
		if (!BackupFiles(strError))
		{
			UpdateSummary("\t" + strError);
		}

		// delete files from HDD
		UpdateSummary("\r\nDelete files...\r\n");
		if (!DeleteNecessaryFiles(strError))
		{
			UpdateSummary(strError);
		}

		// delete from Start Menu folder
		UpdateSummary("\r\nDelete shortcuts...\r\n");
		if (!DeleteShortcuts(strError))
		{
			UpdateSummary("\t" + strError);
		}

		// delete from registry
		UpdateSummary("\r\nDelete key from registry...\r\n");
		if (!DeleteRegistry(strError))
		{
			UpdateSummary("\t" + strError);
		}

		UpdateSummary("\r\nThe uninstall is completed.");

		MessageBox(CRString(IDS_UNINSTALL_COMPLETE), CRString(IDS_BOX_CAPTION), MB_OK | MB_ICONINFORMATION);

		// do not close the dialog yet
		m_bUninstallOK = TRUE;
		GetDlgItem(IDCANCEL)->DestroyWindow();
		GetDlgItem(IDOK)->SetWindowText("Exit");
		GetDlgItem(IDOK)->EnableWindow(TRUE);
		GetDlgItem(IDOK)->SetFocus();

		return;
	}
	else
	{
		CDialog::OnOK();
	}
}

void CPTKUninstallDlg::OnCancel() 
{
	if (!m_bUninstallOK)
	{
		int nRet = MessageBox(CRString(IDS_CANCEL_UNINSTALL), CRString(IDS_BOX_CAPTION), MB_OKCANCEL);
	
		if (nRet == IDOK)
			CDialog::OnCancel();
	}
	else
	{
		CDialog::OnCancel();
	}
}

HBRUSH CPTKUninstallDlg::OnCtlColor(CDC* pDC, CWnd* pWnd, UINT nCtlColor) 
{
	HBRUSH hbr = CDialog::OnCtlColor(pDC, pWnd, nCtlColor);
	
	int nDlgID = pWnd->GetDlgCtrlID();

	if (nDlgID == IDC_TOP || nDlgID == IDC_TITLE)
	{
		pDC->SetTextColor(RGB(0, 0, 0));
		pDC->SetBkMode(TRANSPARENT);
	    hbr = m_Brush;
    }
	
	return hbr;
}

void CPTKUninstallDlg::UpdateSummary(CString strText)
{
	CString strBuffer;
	m_edtSummary.GetWindowText(strBuffer);
	m_edtSummary.SetWindowText(strBuffer + strText);
	m_edtSummary.LineScroll(m_edtSummary.GetLineCount());
}

BOOL CPTKUninstallDlg::StopUninstallServices(CString& strError)
{
	CServiceManager serviceManager;
	CString strBuffer, strZopeError;
	
	strBuffer.Format(CRString(IDS_STOPREMOVE_SERVICE), CRString(IDS_SERVICE_NAME_ZOPE));
	UpdateSummary(strBuffer);
	BOOL bZope = serviceManager.SMUninstallService(CRString(IDS_SERVICE_NAME_ZOPE), strZopeError);
	if (!bZope)
	{	// an error
		UpdateSummary("\t\t" + strZopeError);
	}

	if (!bZope)
	{
		strError = "";
		if (strZopeError != "")
			strError = strError + strZopeError;
		return FALSE;
	}
	else
		return TRUE;
}

BOOL CPTKUninstallDlg::DeleteShortcuts(CString& strError)
{
	CWizardToolz toolz;
	
	if (!toolz.RecDeleteFolder(m_strStartMenuFolderPath))
	{
		strError.Format(CRString(IDS_FAILED_DELETE_FOLDER), m_strStartMenuFolderPath);
		return FALSE;	
	}

	return TRUE;
}

BOOL CPTKUninstallDlg::BackupFiles(CString& strError)
{
	CWizardToolz toolz;

	// create backup directory
	if (!toolz.InternalExistsFolder(m_strBackupPath))
	{
		if(toolz.InternalCreateFolder(m_strBackupPath))
		{
			strError.Format(CRString(IDS_FAILED_CREATE_DIRECTORY), m_strBackupPath);
			return FALSE;
		}
	}

	// backup data.fs
	if (toolz.InternalOverwriteFile(m_strInstancePath + "\\var\\data.fs", m_strBackupPath + "\\data.fs"))
	{
		strError.Format(CRString(IDS_FAILED_CREATE_FILE), m_strBackupPath + "\\data.fs");
        return FALSE;
	}

	return TRUE;
}

BOOL CPTKUninstallDlg::DeleteNecessaryFiles(CString& strError)
{
	CWizardToolz toolz;
	toolz.m_wndProgressBar = &m_prgUninstall;
	CString strBuffer;

    // first compute total files size
    unsigned __int64 n64TotalSize = 0;
	n64TotalSize += toolz.getFolderSize(m_strZopePath);
	n64TotalSize += toolz.getFolderSize(m_strInstancePath);
	n64TotalSize += toolz.getFolderSize(m_strBinPath);
    toolz.m_n64TotalSize = n64TotalSize;
    toolz.m_n64PieceSize = n64TotalSize/100;

	// delete files
	strBuffer.Format(CRString(IDS_REMOVE_FOLDER), m_strZopePath);
	UpdateSummary(strBuffer);
	if (!toolz.RecDeleteFolder(m_strZopePath))
	{
		strBuffer.Format(CRString(IDS_FAILED_DELETE_FOLDER), m_strZopePath);
		UpdateSummary("\t\t" + strBuffer);
	}

	strBuffer.Format(CRString(IDS_REMOVE_FOLDER), m_strInstancePath);
	UpdateSummary(strBuffer);
	if (!toolz.RecDeleteFolder(m_strInstancePath))
	{
		strBuffer.Format(CRString(IDS_FAILED_DELETE_FOLDER), m_strInstancePath);
		UpdateSummary("\t\t" + strBuffer);
	}

	strBuffer.Format(CRString(IDS_REMOVE_FOLDER), m_strBinPath);
	UpdateSummary(strBuffer);
	if(!toolz.RecDeleteFolder(m_strBinPath))
	{
		strBuffer.Format(CRString(IDS_FAILED_DELETE_FOLDER), m_strBinPath);
		UpdateSummary("\t\t" + strBuffer);
	}

	return TRUE;
}

BOOL CPTKUninstallDlg::DeleteRegistry(CString& strError)
{
	CWizardToolz toolz;
	
	if (!toolz.UTDeleteRegistryKey(m_strRegApplicationKey, strError))
		return FALSE;
	else
	{
		CString strRegSystemEnvironment = "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment\\";
	
		// delete ANDTIOWORDHOME
		if (!toolz.UTDeleteRegistryValue(strRegSystemEnvironment, "ANTIWORDHOME", strError))
			return FALSE;

		// delete converters from Path
		CString strRegPath;
		toolz.UTReadRegistryKey(strRegSystemEnvironment, "Path", strRegPath);
		strRegPath.Replace(";" + m_strBinPath + "\\converters\\antiword", "");
		strRegPath.Replace(";" + m_strBinPath + "\\converters\\xlHtml", "");
		strRegPath.Replace(";" + m_strBinPath + "\\converters\\pdftohtml", "");
		toolz.UTCreateRegistryKey(strRegSystemEnvironment, "Path", strRegPath);
	}

	return TRUE;
}

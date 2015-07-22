; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=CInstallPage
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "ptkinstaller.h"
LastPage=0

ClassCount=15
Class1=CAgreementPage
Class2=CErrorPage
Class3=CInstallPathPage
Class4=CNewWizDialog
Class5=CNewWizPage
Class6=CParametersPage
Class7=CPTKInstallerApp
Class8=CAboutDlg
Class9=CPTKInstallerDlg
Class10=CWelcomePage

ResourceCount=13
Resource1=IDD_PTKINSTALLER_DIALOG
Resource2=IDW_WELCOME
Resource3=IDW_AGREEMENT
Resource4=IDW_INSTALLPATH
Resource5=IDW_PORTS
Resource6=IDW_SUMMARY
Resource7=IDD_ABOUTBOX
Class11=CPortsPage
Resource8=IDW_PORTALADMINISTRATIVE
Class12=CMetadataPage
Resource9=IDW_METADATA
Resource10=IDW_ERROR
Class13=CAdministrativePage
Resource11=IDW_ADMINISTRATIVE
Class14=CSummaryPage
Resource12=IDW_PARAMETERS
Class15=CInstallPage
Resource13=IDW_INSTALL

[CLS:CAgreementPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=AgreementPage.h
ImplementationFile=AgreementPage.cpp

[CLS:CErrorPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=ErrorPage.h
ImplementationFile=ErrorPage.cpp

[CLS:CInstallPathPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=InstallPathPage.h
ImplementationFile=InstallPathPage.cpp

[CLS:CNewWizDialog]
Type=0
BaseClass=CDialog
HeaderFile=NewWizDialog.h
ImplementationFile=NewWizDialog.cpp

[CLS:CNewWizPage]
Type=0
BaseClass=CDialog
HeaderFile=NewWizPage.h
ImplementationFile=NewWizPage.cpp

[CLS:CParametersPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=ParametersPage.h
ImplementationFile=ParametersPage.cpp

[CLS:CPTKInstallerApp]
Type=0
BaseClass=CWinApp
HeaderFile=PTKInstaller.h
ImplementationFile=PTKInstaller.cpp

[CLS:CAboutDlg]
Type=0
BaseClass=CDialog
HeaderFile=PTKInstallerDlg.cpp
ImplementationFile=PTKInstallerDlg.cpp
LastObject=CAboutDlg

[CLS:CPTKInstallerDlg]
Type=0
BaseClass=CNewWizDialog
HeaderFile=PTKInstallerDlg.h
ImplementationFile=PTKInstallerDlg.cpp

[CLS:CWelcomePage]
Type=0
BaseClass=CNewWizPage
HeaderFile=WelcomePage.h
ImplementationFile=WelcomePage.cpp

[DLG:IDW_AGREEMENT]
Type=1
Class=CAgreementPage
ControlCount=5
Control1=IDC_AGREEMENT_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_AGREEMENT_INFORMATION,edit,1352665092
Control4=IDC_AGREEMENT_RB_ACCEPT,button,1342177289
Control5=IDC_AGREEMENT_RB_DECLINE,button,1342177289

[DLG:IDW_ERROR]
Type=1
Class=CErrorPage
ControlCount=4
Control1=IDC_ERROR_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_ERROR_SUMMARY_EDIT,edit,1352665092
Control4=IDC_STATIC,static,1342308352

[DLG:IDW_INSTALLPATH]
Type=1
Class=CInstallPathPage
ControlCount=10
Control1=IDC_INSTALLPATH_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC,static,1342308352
Control4=IDC_STATIC,static,1342308352
Control5=IDC_INSTALLPATH_PATH_EDIT,edit,1350631552
Control6=IDC_INSTALLPATH_BROWSE_BUTTON,button,1342242816
Control7=IDC_INSTALLPATH_AVAILABLESPACE_LABEL,static,1342308352
Control8=IDC_INSTALLPATH_AVAILABLESPACE_VALUE,static,1342308352
Control9=IDC_INSTALLPATH_REQUIREDSPACE_LABEL,static,1342308352
Control10=IDC_INSTALLPATH_REQUIREDSPACE_VALUE,static,1342308352

[DLG:IDW_PARAMETERS]
Type=1
Class=CParametersPage
ControlCount=15
Control1=IDC_PARAMETERS_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC,static,1342308352
Control4=IDC_STATIC,static,1342308352
Control5=IDC_PARAMETERS_FULLHOSTNAME_EDIT,edit,1350631552
Control6=IDC_STATIC,static,1342308352
Control7=IDC_PARAMETERS_HOSTIDADDRESS_IPADDRESS,SysIPAddress32,1342242816
Control8=IDC_STATIC,static,1342308352
Control9=IDC_PARAMETERS_USERNAME_EDIT,edit,1350631552
Control10=IDC_STATIC,static,1342308352
Control11=IDC_PARAMETERS_PASSWORD_EDIT,edit,1350631584
Control12=IDC_STATIC,static,1342308352
Control13=IDC_PARAMETERS_CONFIRMPASSWORD_EDIT,edit,1350631584
Control14=IDC_STATIC,static,1342308352
Control15=IDC_PARAMETERS_ADMINEMAIL_EDIT,edit,1350631552

[DLG:IDD_ABOUTBOX]
Type=1
Class=CAboutDlg
ControlCount=4
Control1=IDC_STATIC,static,1342177283
Control2=IDC_STATIC,static,1342308480
Control3=IDC_STATIC,static,1342308352
Control4=IDOK,button,1342373889

[DLG:IDD_PTKINSTALLER_DIALOG]
Type=1
Class=CPTKInstallerDlg
ControlCount=5
Control1=IDCANCEL,button,1342242816
Control2=ID_WIZFINISH,button,1342242816
Control3=ID_WIZNEXT,button,1342242816
Control4=ID_WIZBACK,button,1342242816
Control5=IDC_SHEETRECT,static,1342177298

[DLG:IDW_WELCOME]
Type=1
Class=CWelcomePage
ControlCount=5
Control1=IDC_STATIC,static,1342177294
Control2=IDC_WELCOME_TITLE,static,1342308352
Control3=IDC_STATIC,static,1342308352
Control4=IDC_STATIC,static,1342308352
Control5=IDC_STATIC,static,1342308352

[DLG:IDW_PORTS]
Type=1
Class=CPortsPage
ControlCount=5
Control1=IDC_PORTS_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC,static,1342308352
Control4=IDC_PORTS_ZOPEHTTPPORT_EDIT,edit,1350639744
Control5=IDC_STATIC,static,1342308352

[CLS:CPortsPage]
Type=0
HeaderFile=PortsPage.h
ImplementationFile=PortsPage.cpp
BaseClass=CDialog
Filter=D
LastObject=CPortsPage
VirtualFilter=dWC

[DLG:IDW_METADATA]
Type=1
Class=CMetadataPage
ControlCount=15
Control1=IDC_PORTALMETADATA_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC,static,1342308352
Control4=IDC_STATIC,static,1342308352
Control5=IDC_STATIC,static,1342308352
Control6=IDC_STATIC,static,1342308352
Control7=IDC_STATIC,static,1342308352
Control8=IDC_STATIC,static,1342308352
Control9=IDC_PORTAL_TITLE,edit,1350631552
Control10=IDC_PORTAL_SUBTITLE,edit,1350631552
Control11=IDC_PORTAL_PUBLISHER,edit,1350631552
Control12=IDC_PORTAL_CONTRIBUTOR,edit,1350631552
Control13=IDC_PORTAL_CREATOR,edit,1350631552
Control14=IDC_PORTAL_RIGHTS,edit,1350631552
Control15=IDC_STATIC,static,1342308352

[CLS:CMetadataPage]
Type=0
HeaderFile=MetadataPage.h
ImplementationFile=MetadataPage.cpp
BaseClass=CDialog
Filter=D
LastObject=CMetadataPage
VirtualFilter=dWC

[DLG:IDW_ADMINISTRATIVE]
Type=1
Class=CAdministrativePage
ControlCount=12
Control1=IDC_STATIC,static,1342177294
Control2=IDC_PORTALADMINISTRATIVE_TITLE,static,1342308352
Control3=IDC_STATIC,static,1342308352
Control4=IDC_STATIC,static,1342308352
Control5=IDC_PORTAL_LANGUAGES,listbox,1352728841
Control6=IDC_STATIC,static,1342308352
Control7=IDC_STATIC,static,1342308352
Control8=IDC_PORTAL_MAILSERVERNAME,edit,1350631552
Control9=IDC_STATIC,static,1342308352
Control10=IDC_PORTAL_MAILSERVERPORT,edit,1350639744
Control11=IDC_STATIC,static,1342308352
Control12=IDC_PORTAL_DEFAULTFROMADDRESS,edit,1350631552

[DLG:IDW_PORTALADMINISTRATIVE]
Type=1
Class=?
ControlCount=12
Control1=IDC_STATIC,static,1342177294
Control2=IDC_PORTALADMINISTRATIVE_TITLE,static,1342308352
Control3=IDC_STATIC,static,1342308352
Control4=IDC_STATIC,static,1342308352
Control5=IDC_PORTAL_LANGUAGES,listbox,1352728841
Control6=IDC_STATIC,static,1342308352
Control7=IDC_STATIC,static,1342308352
Control8=IDC_PORTAL_MAILSERVERNAME,edit,1350631552
Control9=IDC_STATIC,static,1342308352
Control10=IDC_PORTAL_MAILSERVERPORT,edit,1350639744
Control11=IDC_STATIC,static,1342308352
Control12=IDC_PORTAL_DEFAULTFROMADDRESS,edit,1350631552

[CLS:CAdministrativePage]
Type=0
HeaderFile=AdministrativePage.h
ImplementationFile=AdministrativePage.cpp
BaseClass=CDialog
Filter=D
LastObject=CAdministrativePage
VirtualFilter=dWC

[DLG:IDW_SUMMARY]
Type=1
Class=CSummaryPage
ControlCount=4
Control1=IDC_SUMMARY_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_SUMMARY_EDIT,edit,1353713668
Control4=IDC_STATIC,static,1342308352

[CLS:CSummaryPage]
Type=0
HeaderFile=SummaryPage.h
ImplementationFile=SummaryPage.cpp
BaseClass=CDialog
Filter=D
LastObject=CSummaryPage
VirtualFilter=dWC

[DLG:IDW_INSTALL]
Type=1
Class=CInstallPage
ControlCount=6
Control1=IDC_INSTALL_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC_INFO,static,1342308352
Control4=IDC_PROGRESS_INSTALLATION,msctls_progress32,1350565888
Control5=IDC_STATIC_INSTALLATION,static,1342308352
Control6=IDC_CHECK_START,button,1476460547

[CLS:CInstallPage]
Type=0
HeaderFile=InstallPage.h
ImplementationFile=InstallPage.cpp
BaseClass=CDialog
Filter=D
LastObject=CInstallPage
VirtualFilter=dWC


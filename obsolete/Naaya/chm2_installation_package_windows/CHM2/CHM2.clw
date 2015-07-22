; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=CCHM2Dlg
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "chm2.h"
LastPage=0

ClassCount=16
Class1=CAgreementPage
Class2=CCHM2App
Class3=CAboutDlg
Class4=CCHM2Dlg
Class5=CErrorPage
Class6=CFinishPage
Class7=CInstallPage
Class8=CInstallPathPage
Class9=CNewWizDialog
Class10=CNewWizPage
Class11=CParametersPage
Class12=CPortalMetadataPage
Class13=CPortsPage
Class14=CWelcomePage

ResourceCount=13
Resource1=IDW_PORTALMETADATA
Resource2=IDW_INSTALL
Resource3=IDW_INSTALLPATH
Resource4=IDW_PORTS
Resource5=IDD_ABOUTBOX
Resource6=IDW_PORTALADMINISTRATIVE
Resource7=IDW_FINISH
Resource8=IDD_CHM2_DIALOG
Resource9=IDW_AGREEMENT
Resource10=IDW_ERROR
Resource11=IDW_PARAMETERS
Class15=CPortalAdministrativePage
Resource12=IDW_WELCOME
Class16=CPortalLogosPage
Resource13=IDW_PORTALLOGOS

[CLS:CAgreementPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=AgreementPage.h
ImplementationFile=AgreementPage.cpp

[CLS:CCHM2App]
Type=0
BaseClass=CWinApp
HeaderFile=CHM2.h
ImplementationFile=CHM2.cpp

[CLS:CAboutDlg]
Type=0
BaseClass=CDialog
HeaderFile=CHM2Dlg.cpp
ImplementationFile=CHM2Dlg.cpp

[CLS:CCHM2Dlg]
Type=0
BaseClass=CNewWizDialog
HeaderFile=CHM2Dlg.h
ImplementationFile=CHM2Dlg.cpp
LastObject=CCHM2Dlg

[CLS:CErrorPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=ErrorPage.h
ImplementationFile=ErrorPage.cpp

[CLS:CFinishPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=FinishPage.h
ImplementationFile=FinishPage.cpp

[CLS:CInstallPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=InstallPage.h
ImplementationFile=InstallPage.cpp

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

[CLS:CPortalMetadataPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=PortalMetadataPage.h
ImplementationFile=PortalMetadataPage.cpp
LastObject=CPortalMetadataPage

[CLS:CPortsPage]
Type=0
BaseClass=CNewWizPage
HeaderFile=PortsPage.h
ImplementationFile=PortsPage.cpp

[CLS:CWelcomePage]
Type=0
BaseClass=CNewWizPage
HeaderFile=WelcomePage.h
ImplementationFile=WelcomePage.cpp

[DLG:IDW_AGREEMENT]
Type=1
Class=CAgreementPage
ControlCount=6
Control1=IDC_AGREEMENT_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC,static,1342308352
Control4=IDC_AGREEMENT_RB_ACCEPT,button,1342177289
Control5=IDC_AGREEMENT_RB_DECLINE,button,1342177289
Control6=IDC_AGREEMENT_INFORMATION,edit,1352665092

[DLG:IDD_ABOUTBOX]
Type=1
Class=CAboutDlg
ControlCount=4
Control1=IDC_STATIC,static,1342177283
Control2=IDC_STATIC,static,1342308480
Control3=IDC_STATIC,static,1342308352
Control4=IDOK,button,1342373889

[DLG:IDD_CHM2_DIALOG]
Type=1
Class=CCHM2Dlg
ControlCount=5
Control1=IDCANCEL,button,1342242816
Control2=ID_WIZFINISH,button,1342242816
Control3=ID_WIZNEXT,button,1342242816
Control4=ID_WIZBACK,button,1342242816
Control5=IDC_SHEETRECT,static,1342177298

[DLG:IDW_ERROR]
Type=1
Class=CErrorPage
ControlCount=4
Control1=IDC_ERROR_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_ERROR_SUMMARY_EDIT,edit,1352665092
Control4=IDC_STATIC,static,1342308352

[DLG:IDW_FINISH]
Type=1
Class=CFinishPage
ControlCount=4
Control1=IDC_FINISH_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_FINISH_SUMMARY_EDIT,edit,1353713668
Control4=IDC_STATIC,static,1342308352

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

[DLG:IDW_PORTALMETADATA]
Type=1
Class=CPortalMetadataPage
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

[DLG:IDW_PORTS]
Type=1
Class=CPortsPage
ControlCount=5
Control1=IDC_PORTS_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC,static,1342308352
Control4=IDC_PORTS_ZOPEHTTPPORT_EDIT,edit,1350639744
Control5=IDC_STATIC,static,1342308352

[DLG:IDW_WELCOME]
Type=1
Class=CWelcomePage
ControlCount=5
Control1=IDC_WELCOME_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342308352
Control3=IDC_STATIC,static,1342177294
Control4=IDC_STATIC,static,1342308352
Control5=IDC_STATIC,static,1342308352

[DLG:IDW_PORTALADMINISTRATIVE]
Type=1
Class=CPortalAdministrativePage
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

[CLS:CPortalAdministrativePage]
Type=0
HeaderFile=PortalAdministrativePage.h
ImplementationFile=PortalAdministrativePage.cpp
BaseClass=CNewWizPage
Filter=D
LastObject=CPortalAdministrativePage

[DLG:IDW_PORTALLOGOS]
Type=1
Class=CPortalLogosPage
ControlCount=10
Control1=IDC_PORTALLOGOS_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC,static,1342308352
Control4=IDC_LOGO_PATH,edit,1350631552
Control5=IDC_LOGO_BROWSE_BUTTON,button,1342242816
Control6=IDC_STATIC,static,1342308352
Control7=IDC_LOGOBIS_PATH,edit,1350631552
Control8=IDC_LOGOBIS_BROWSE_BUTTON,button,1342242816
Control9=IDC_STATIC,static,1342308352
Control10=IDC_STATIC,static,1342308352

[CLS:CPortalLogosPage]
Type=0
HeaderFile=PortalLogosPage.h
ImplementationFile=PortalLogosPage.cpp
BaseClass=CNewWizPage
Filter=D
LastObject=CPortalLogosPage


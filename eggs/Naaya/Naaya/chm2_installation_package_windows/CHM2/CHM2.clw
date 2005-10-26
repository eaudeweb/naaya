; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=CCHM2Dlg
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "CHM2.h"

ClassCount=3
Class1=CCHM2App
Class2=CCHM2Dlg
Class3=CAboutDlg

ResourceCount=11
Resource1=IDW_ERROR
Resource2=IDR_MAINFRAME
Resource3=IDW_AGREEMENT
Resource4=IDD_ABOUTBOX
Resource5=IDD_CHM2_DIALOG
Resource6=IDW_WELCOME
Resource7=IDW_FINISH
Resource8=IDW_INSTALLPATH
Resource9=IDW_PARAMETERS
Resource10=IDW_PORTS
Resource11=IDW_INSTALL

[CLS:CCHM2App]
Type=0
HeaderFile=CHM2.h
ImplementationFile=CHM2.cpp
Filter=N
BaseClass=CWinApp
VirtualFilter=AC

[CLS:CCHM2Dlg]
Type=0
HeaderFile=CHM2Dlg.h
ImplementationFile=CHM2Dlg.cpp
Filter=D
LastObject=CCHM2Dlg

[CLS:CAboutDlg]
Type=0
HeaderFile=CHM2Dlg.h
ImplementationFile=CHM2Dlg.cpp
Filter=D

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
Class=?
ControlCount=4
Control1=IDC_ERROR_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_ERROR_SUMMARY_EDIT,edit,1352665092
Control4=IDC_STATIC,static,1342308352

[DLG:IDW_WELCOME]
Type=1
Class=?
ControlCount=5
Control1=IDC_WELCOME_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342308352
Control3=IDC_STATIC,static,1342177294
Control4=IDC_STATIC,static,1342308352
Control5=IDC_STATIC,static,1342308352

[DLG:IDW_AGREEMENT]
Type=1
Class=?
ControlCount=7
Control1=IDC_AGREEMENT_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC,static,1342308352
Control4=IDC_AGREEMENT_RB_ACCEPT,button,1342177289
Control5=IDC_AGREEMENT_RB_DECLINE,button,1342177289
Control6=IDC_AGREEMENT_INFORMATION,edit,1352665092
Control7=IDC_STATIC,static,1342308352

[DLG:IDW_INSTALLPATH]
Type=1
Class=?
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
Class=?
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

[DLG:IDW_PORTS]
Type=1
Class=?
ControlCount=10
Control1=IDC_PORTS_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC,static,1342308352
Control4=IDC_STATIC,static,1342308352
Control5=IDC_PORTS_ZOPEHTTPPORT_EDIT,edit,1350639744
Control6=IDC_STATIC,static,1342308352
Control7=IDC_PORTS_ZOPEFTPPORT_EDIT,edit,1350639744
Control8=IDC_STATIC,static,1342308352
Control9=IDC_PORTS_ZOPEWEBDAVPORT_EDIT,edit,1350639744
Control10=IDC_STATIC,static,1342308352

[DLG:IDW_FINISH]
Type=1
Class=?
ControlCount=4
Control1=IDC_FINISH_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_FINISH_SUMMARY_EDIT,edit,1353713668
Control4=IDC_STATIC,static,1342308352

[DLG:IDW_INSTALL]
Type=1
Class=?
ControlCount=6
Control1=IDC_INSTALL_TITLE,static,1342308352
Control2=IDC_STATIC,static,1342177294
Control3=IDC_STATIC_INFO,static,1342308352
Control4=IDC_PROGRESS_INSTALLATION,msctls_progress32,1350565888
Control5=IDC_STATIC_INSTALLATION,static,1342308352
Control6=IDC_CHECK_START,button,1476460547


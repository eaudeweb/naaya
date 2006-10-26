; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=CZEUDlg
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "PTKConsole.h"

ClassCount=8
Class1=CPTKConsoleApp
Class2=CPTKConsoleDlg
Class3=CAboutDlg

ResourceCount=7
Resource1=IDD_TAB_ZOPE
Resource2=IDR_MAINFRAME
Class4=CConsoleTabCtrl
Resource3=IDD_ABOUTBOX
Class5=CTabService
Resource4=IDD_PTKCONSOLE_DIALOG
Class6=CTabZope
Resource5=IDD_TAB_SERVICE
Class7=CTabAbout
Resource6=IDD_TAB_ABOUT
Class8=CZEUDlg
Resource7=IDD_ZEU_DIALOG

[CLS:CPTKConsoleApp]
Type=0
HeaderFile=PTKConsole.h
ImplementationFile=PTKConsole.cpp
Filter=N

[CLS:CPTKConsoleDlg]
Type=0
HeaderFile=PTKConsoleDlg.h
ImplementationFile=PTKConsoleDlg.cpp
Filter=D
LastObject=IDC_CONSOLE_TAB

[CLS:CAboutDlg]
Type=0
HeaderFile=PTKConsoleDlg.h
ImplementationFile=PTKConsoleDlg.cpp
Filter=D

[DLG:IDD_ABOUTBOX]
Type=1
Class=CAboutDlg
ControlCount=4
Control1=IDC_STATIC,static,1342177283
Control2=IDC_STATIC,static,1342308480
Control3=IDC_STATIC,static,1342308352
Control4=IDOK,button,1342373889

[DLG:IDD_PTKCONSOLE_DIALOG]
Type=1
Class=CPTKConsoleDlg
ControlCount=4
Control1=IDOK,button,1342242817
Control2=IDC_CONSOLE_TAB,SysTabControl32,1342177280
Control3=IDC_TOP,static,1342308352
Control4=IDC_TITLE,static,1342308352

[CLS:CConsoleTabCtrl]
Type=0
HeaderFile=ConsoleTabCtrl.h
ImplementationFile=ConsoleTabCtrl.cpp
BaseClass=CTabCtrl
Filter=W
VirtualFilter=UWC
LastObject=CConsoleTabCtrl

[DLG:IDD_TAB_SERVICE]
Type=1
Class=CTabService
ControlCount=1
Control1=IDC_STATIC,static,1342308352

[CLS:CTabService]
Type=0
HeaderFile=TabService.h
ImplementationFile=TabService.cpp
BaseClass=CDialog
Filter=D
LastObject=CTabService

[DLG:IDD_TAB_ZOPE]
Type=1
Class=CTabZope
ControlCount=16
Control1=IDC_STATIC,static,1342308352
Control2=IDOK,button,1342242816
Control3=IDCANCEL,button,1342242816
Control4=IDC_STATIC,static,1342308864
Control5=IDC_STATUS_STATIC,static,1342312960
Control6=IDC_STATIC,static,1342308864
Control7=IDC_NAME_STATIC,static,1342312960
Control8=IDC_STATIC,static,1342308864
Control9=IDC_DISPLAY_STATIC,static,1342312960
Control10=IDC_STATIC,static,1342308864
Control11=IDC_PATH_EDIT,edit,1350633600
Control12=ID_EMERGENCYUSER,button,1342242816
Control13=IDC_STATIC,static,1342308864
Control14=IDC_STARTTYPE_COMBO,combobox,1344339971
Control15=IDC_APPLY_BUTTON,button,1342242816
Control16=IDC_ZOPECONF_PATH,edit,1350633600

[CLS:CTabZope]
Type=0
HeaderFile=TabZope.h
ImplementationFile=TabZope.cpp
BaseClass=CDialog
Filter=D
LastObject=CTabZope

[DLG:IDD_TAB_ABOUT]
Type=1
Class=CTabAbout
ControlCount=3
Control1=IDC_STATIC,static,1342308352
Control2=IDC_STATIC,static,1342308352
Control3=IDC_STATIC,static,1342308352

[CLS:CTabAbout]
Type=0
HeaderFile=TabAbout.h
ImplementationFile=TabAbout.cpp
BaseClass=CDialog
Filter=D
LastObject=CTabAbout

[DLG:IDD_ZEU_DIALOG]
Type=1
Class=CZEUDlg
ControlCount=12
Control1=IDOK,button,1342242817
Control2=IDC_STATIC,static,1342308352
Control3=IDC_STATIC,static,1342308352
Control4=IDC_STATIC,static,1342308352
Control5=IDC_USERNAME_EDIT,edit,1350631552
Control6=IDC_STATIC,static,1342308352
Control7=IDC_PASSWORD_EDIT,edit,1350631584
Control8=IDC_STATIC,static,1342308352
Control9=IDC_CONFIRMPASSWORD_EDIT,edit,1350631584
Control10=IDC_STATIC,static,1342308352
Control11=IDCANCEL,button,1342242816
Control12=IDC_DELETE_ZEU_BUTTON,button,1342242816

[CLS:CZEUDlg]
Type=0
HeaderFile=ZEUDlg.h
ImplementationFile=ZEUDlg.cpp
BaseClass=CDialog
Filter=D
LastObject=CZEUDlg


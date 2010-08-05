; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=CPTKUninstallDlg
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "PTKUninstall.h"

ClassCount=4
Class1=CPTKUninstallApp
Class2=CPTKUninstallDlg
Class3=CAboutDlg

ResourceCount=3
Resource1=IDD_ABOUTBOX
Resource2=IDR_MAINFRAME
Resource3=IDD_PTKUNINSTALL_DIALOG

[CLS:CPTKUninstallApp]
Type=0
HeaderFile=PTKUninstall.h
ImplementationFile=PTKUninstall.cpp
Filter=N

[CLS:CPTKUninstallDlg]
Type=0
HeaderFile=PTKUninstallDlg.h
ImplementationFile=PTKUninstallDlg.cpp
Filter=D
BaseClass=CDialog
VirtualFilter=dWC

[CLS:CAboutDlg]
Type=0
HeaderFile=PTKUninstallDlg.h
ImplementationFile=PTKUninstallDlg.cpp
Filter=D

[DLG:IDD_ABOUTBOX]
Type=1
Class=CAboutDlg
ControlCount=4
Control1=IDC_STATIC,static,1342177283
Control2=IDC_STATIC,static,1342308480
Control3=IDC_STATIC,static,1342308352
Control4=IDOK,button,1342373889

[DLG:IDD_PTKUNINSTALL_DIALOG]
Type=1
Class=CPTKUninstallDlg
ControlCount=7
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_TOP,static,1342177280
Control4=IDC_TITLE,static,1342308352
Control5=IDC_STATIC,static,1342308352
Control6=IDC_UNINSTALL_PROGRESS,msctls_progress32,1350565888
Control7=IDC_UNINSTALL_SUMMARY_EDIT,edit,1353779204


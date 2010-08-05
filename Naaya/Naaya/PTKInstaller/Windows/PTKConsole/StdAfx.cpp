// stdafx.cpp : source file that includes just the standard includes
//	PTKConsole.pch will be the pre-compiled header
//	stdafx.obj will contain the pre-compiled type information

#include "stdafx.h"

CRString::CRString(int nID)
{
	this->LoadString (nID);
}
CRString::~CRString()
{
}

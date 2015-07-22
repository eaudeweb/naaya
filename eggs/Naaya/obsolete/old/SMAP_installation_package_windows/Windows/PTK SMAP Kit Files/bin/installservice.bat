
@echo off

echo.
echo.
echo.Install Zope service
echo --------------------
echo.
echo.

echo Register Zope
echo -------------
"@@ZOPE_PATH@@\zope\bin\python.exe" "@@ZOPE_PATH@@\instance\bin\zopeservice.py" --startup=manual install
echo.
echo.


@echo off

echo.
echo.
echo.Start Zope service
echo ------------------
echo.
echo.

"@@ZOPE_PATH@@\zope\bin\python.exe" "@@ZOPE_PATH@@\instance\bin\zopeservice.py" start
echo.
echo.


@echo off

echo.
echo.
echo.Stop Zope service
echo -----------------
echo.
echo.

"@@ZOPE_PATH@@\zope\bin\python.exe" "@@ZOPE_PATH@@\instance\bin\zopeservice.py" stop
echo.
echo.

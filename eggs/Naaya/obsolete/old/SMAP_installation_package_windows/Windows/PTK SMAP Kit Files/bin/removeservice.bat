
@echo off

echo.
echo.
echo.Remove Zope service
echo -------------------
echo.
echo.

echo Try stoping Zope if started
echo ---------------------------
"@@ZOPE_PATH@@\zope\bin\python.exe" "@@ZOPE_PATH@@\instance\bin\zopeservice.py" stop
echo.
echo Remove Zope from services
echo -------------------------
"@@ZOPE_PATH@@\zope\bin\python.exe" "@@ZOPE_PATH@@\instance\bin\zopeservice.py" remove
echo.
echo.

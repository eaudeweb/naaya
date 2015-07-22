rem    ***
rem    Start script to run the maildrop python process
rem    Developed and graciously contributed by Chris Beaven
rem    !!!!You must change the values to reflect your own preferences!!!
rem    ***

rem    Set the maildrop main directory (e.g "C:\Program Files\Zope_Alec")
set maildrophome=D:\DocManager\zope_272\Products\DocManager\notification

rem    Where is your Zope instance? (e.g "C:\Program Files\WebSite")
set zope_home=D:\DocManager\zope_272

rem    What SMTP server will maildrop use?
set smtp="finfw.finronet.ro"

rem    How long to wait between spool checkups? (in seconds)
set pollinginterval=10

rem    Where is the python executable? (e.g "C:\Program Files\Python22\python.exe")
set pythonexe=D:\Zope-2.7.2-0\bin\python.exe

rem    Debug mode (REM out the following line if you don't want to use debug mode)
set debugmode=-d

rem    ----------- No changes needed below this line ----------

"%pythonexe%" "%maildrophome%\maildrop.py" -h "%zope_home%" -s %smtp% -i %pollinginterval% %debugmode%
pause

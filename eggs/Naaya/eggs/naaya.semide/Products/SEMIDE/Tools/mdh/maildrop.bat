rem    ***
rem    Start script to run the maildrop python process
rem    Developed and graciously contributed by Chris Beaven
rem    !!!!You must change the values to reflect your own preferences!!!
rem    ***

rem    Set the maildrop main directory (e.g 
"D:\zopefarms\275_naaya\Products\SEMIDE\Tools\mdh")
set maildrophome=%INSTANCE_HOME%\Products\SEMIDE\Tools\mdh

rem    Where is your Zope instance? (e.g "D:\zopefarms\275_naaya")
set zope_home2=%INSTANCE_HOME%

rem    What SMTP server will maildrop use?
set smtp=%MAILHOST%

rem    How long to wait between spool checkups? (in seconds)
set pollinginterval=120

rem    Where is the python executable? (e.g "D:\zopefarms\Zope-2.7.5-final\bin\python.exe")
set pythonexe=%ZOPE_HOME%\bin\python.exe

rem    Debug mode (REM out the following line if you don't want to use debug mode)
rem set debugmode=-d

rem    ----------- No changes needed below this line ----------

"%pythonexe%" "%maildrophome%/maildrop.py" -h "%zope_home2%" -s %smtp% -i %pollinginterval% %debugmode%



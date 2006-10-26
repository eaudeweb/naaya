@set PYTHON=@@ZOPE_PATH@@\zope\bin\python.exe
@set ZOPE_HOME=@@ZOPE_PATH@@\zope
@set INSTANCE_HOME=@@ZOPE_PATH@@\instance
@set SOFTWARE_HOME=@@ZOPE_PATH@@\zope\lib\python
@set CONFIG_FILE=@@ZOPE_PATH@@\instance\etc\zope.conf
@set PYTHONPATH=%SOFTWARE_HOME%
@set ZOPE_RUN=%SOFTWARE_HOME%\Zope\Startup\run.py
"%PYTHON%" "%ZOPE_RUN%" -C "%CONFIG_FILE%" %1 %2 %3 %4 %5 %6 %7

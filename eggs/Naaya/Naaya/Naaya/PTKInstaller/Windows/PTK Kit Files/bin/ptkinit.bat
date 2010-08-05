@set PYTHON=@@ZOPE_PATH@@\zope\bin\python.exe
@set INSTANCE_HOME=@@ZOPE_PATH@@\instance
@set SOFTWARE_HOME=@@ZOPE_PATH@@\zope\lib\python
@set CONFIG_FILE=@@ZOPE_PATH@@\instance\etc\zope.conf

"%PYTHON%" @@BIN_PATH@@\ptkinit.py --install

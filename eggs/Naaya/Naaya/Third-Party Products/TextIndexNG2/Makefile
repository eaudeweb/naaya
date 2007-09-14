PYTHON=python2.2

clean:
	find . -name build | xargs rm -fr 
	find . -name dist | xargs rm -fr 
	find . -name \*.pyc |xargs rm
	find . -name core\* |xargs rm
	find . -name \*.o |xargs rm
	find . -name \*.so | xargs rm

dist: 
	tar cfvz /tmp/TextIndexNG-`cat VERSION.txt`.tar.gz *
	${PYTHON} setup.py sdist
	${PYTHON} setup.py bdist

build:
	${PYTHON} setup.py build

install:
	${PYTHON} setup.py install

test:
	${PYTHON} ../../../../utilities/testrunner.py -d ${PWD}    

perm:
	find . -type f | xargs chmod a+rw 
	find . -type d | xargs chmod a+rx

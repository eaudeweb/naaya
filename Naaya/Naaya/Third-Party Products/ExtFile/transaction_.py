#
# Zope 2.8-style transactions for Zope <= 2.7.
#

# $Id: transaction_.py 15452 2005-12-30 21:29:18Z shh42 $

def get():
    return get_transaction()

def begin():
    get_transaction().begin()

def commit(sub=0):
    get_transaction().commit(sub)

def abort(sub=0):
    get_transaction().abort(sub)

def savepoint(optimistic=0):
    get_transaction().commit(1)
    return DummySavePoint()

class DummySavePoint:
    valid = 0
    def rollback(self):
        raise RuntimeError, 'Rollback of dummy savepoint'

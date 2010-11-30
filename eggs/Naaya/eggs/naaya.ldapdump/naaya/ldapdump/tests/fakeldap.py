import ldap
from ldap.dn import explode_dn

history = []

TREE = {}
def clearTree():
    TREE.clear()

def setTreeItem(dn, attrs=None):
    elems = explode_dn(dn)
    elems.reverse()

    tree_pos = TREE
    last_i = len(elems) - 1
    for i, elem in enumerate(elems):
        key = ','.join(elems[:i+1][::-1])
        if not tree_pos.has_key(key):
            if i == last_i and attrs is not None:
                tree_pos[key] = attrs
            else:
                tree_pos[key] = {}
        tree_pos = tree_pos[key]
    return tree_pos

def getSubtree(dn):
    elems = explode_dn(dn)
    elems.reverse()

    tree_pos = TREE
    tree_pos_dn = ''
    for elem in elems:
        if not tree_pos_dn:
            tree_pos_dn = elem
        else:
            tree_pos_dn = '%s,%s' % (elem, tree_pos_dn)

        if tree_pos.has_key(tree_pos_dn):
            tree_pos = tree_pos[tree_pos_dn]
        else:
            raise ldap.NO_SUCH_OBJECT(tree_pos_dn)
    assert tree_pos_dn == dn
    return tree_pos


def initialize(uri):
    history.append({'initialize': [uri]})
    return LDAPConn()

SCOPE_SUBTREE = ldap.SCOPE_SUBTREE
LDAPError = ldap.LDAPError
VERSION3 = ldap.VERSION3

class LDAPConn(object):
    def __init__(self):
        self.protocol_version = ''

    def simple_bind_s(self, dn, password):
        history.append({'simple_bind_s': [dn, password]})

    def search_s(self, baseDN, searchScope):
        history.append({'search_s': [baseDN, searchScope]})

        assert searchScope == SCOPE_SUBTREE
        return getSubtree(baseDN).items()

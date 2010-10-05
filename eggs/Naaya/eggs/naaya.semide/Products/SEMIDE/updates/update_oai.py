from Products.naayaUpdater.updates import UpdateScript

class UpdateOAI(UpdateScript):
    """  """
    id = 'update_oai'
    title='Update OAI connection url'
    description='The connection url to the SQLAlchemy must be editable'

    def _update(self, portal):
        """ """
        if hasattr(portal, 'oai'):
            portal.oai.connection_url = 'mysql+mysqldb://semide:semide@localhost/%s_oai?charset=utf8&use_unicode=1' % portal.id
            delattr(portal.oai, 'sqlalchemy')
            self._p_changed = True
        return True

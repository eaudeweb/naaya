from datetime import datetime
from zope.interface import Interface
from zope import schema

class GenericInterface(Interface):
    """
    Generic interface to be used in all other interfaces. Used for schema

    """
    title = schema.TextLine(title=u'Title')

class IHarvester(GenericInterface):
    """ Implemented by classes such as ZCatalogHarvester, And OAIHarvester
    A harvester collects data from some source in our case ZCatalog or an OAI
    Server. It contains OAIRecord items that represent the collected OAI data.

    """
    update_interval = schema.Int(title=u'Update interval', default=1,
                                 required=False)
    last_update = schema.Datetime(title=u'Last update',
                                    default=None, required = False)
    resume_token = schema.TextLine(title=u'Resume Token', default=u'',
                                     required=False)
    def update(self):
        """ Update all OAIRecord items """

    def clear(self):
        """ Delete all OAIRecord items """

class IZCatalogHarvester(IHarvester):
    """ Fetches local data based on metatype to be used in OAISever

    """
    search_meta_types = schema.List(title=u'Meta types', default=[],
                                    required=False) #Meta types to index

class IOAIHarvester(IHarvester):
    """ Fetches records from remote OAI servers

    """
    url = schema.URI(title=u'OAI URL')
    username = schema.TextLine(title=u'Username', default=u'', required=False)
    password = schema.TextLine(title=u'Password', default=u'', required=False)
    list_sets = schema.List(title=u"List sets", required=False)
    list_sets.update = False #Don't update by default
    list_sets_all = schema.Bool(title=u'Use all sets', default=True,
                                required=False)
    list_sets_selected = schema.List(title=u'Selected list sets', default=[],
                                     required=False)


class IOAIRecord(Interface):
    """

    """
    last_update = schema.Datetime(title=u'Last update', default=datetime.now(),
                                    required=False)
    encoding = schema.TextLine(title=u'Encoding', default=u'utf-8',
                               required=False)
    deleted = schema.Bool(title=u'Deleted', default=False, required=False)
    status = schema.TextLine(title=u'Status', default=u'available',
                             required=False)
    about = schema.Text(title=u'About', default=u'', required=False)
    harvester = schema.TextLine(title=u'Havester', default=u'',
                               required=False)

    def update(self):
        """ """

class IOAIRepository(GenericInterface):
    """ This container is generic for OAIServer and OAIAggregator
    It holds a ZCatalog for searching OAI data, namespace and resume token
    folders.

    """
    update_interval = schema.Int(title=u'Update interval', default=1,
                                 required=False)
    autopublish = schema.Int(title=u'Autopublish', default=1, required=False)
    token_expiration = schema.Int(title=u'Token expiration (minutes)',
                                  default=1, required=False)
    protocol_version = schema.TextLine(title=u'Procotol version',
                                      default=u'2.0',
                                      required=False)
    last_update = schema.Datetime(title=u'Last update', default=None,
                                    required = False)


    def add_indexes(self):
        """ """

    def add_metadata(self):
        """ """

class IOAIToken(Interface):
    """
    OAI Resumption Token is used to restore paused connections. Part of OAI
    protocol.

    """
    parent_id = schema.TextLine(title=u'Parent ID', required=False,
                                default=u"")
    request_args = schema.Dict(title=u'Request Arguments')
    token_args = schema.Dict(title=u'Token Arguments')

class IOAINamespace(GenericInterface):
    """OAI Namespace holds DublinCore data

    """

class IOAIServer(IOAIRepository):
    """ Implementation of OAI2 Server. Using the Zope publisher. Is a
    container for ZCatalogHarvesters uses indexed metadata from its ZCatalog
    to display the OAI content to the world.

    """
    autopublish_roles = schema.Text(title=u'Autopublish roles',
                                    default=u'Anonymous', required=False)
    results_limit = schema.Int(title=u'Display Limit', default=100,
                               required=False)
    deleted_record = schema.TextLine(title=u'Deleted record support',
                                     default=u'no', #transient, persistent
                                     required = False)
    date_granularity = schema.TextLine(title=u'Granularity',
                                       default=u'YYYY-MM-DD',
                                       required=False)
    admin_emails = schema.Text(title=u'Admin Emails', default=u'',
                               required=False)
    repository_name = schema.TextLine(title=u'Repository Name',
                                      default=u'Repository Name',
                                      required=False)

class IOAIAggregator(IOAIRepository):
    """ Stores the data collected from remote OAI servers. Is a container for
    OAIHarvesters. Usualy it is used in the frontend providing an interface
    to search and display cataloged OAIRecords

    """

    storage = schema.Choice(values=['ZCatalog', 'SQLAlchemy'],
                            title=u"Storage", default="ZCatalog",
                            required=False)
    connection_url = schema.TextLine(title=u"Connection string for SQLAlchemy",
                                     default=u'', required=False)
    def add_indexes(self):
        """ """

    def add_metadata(self):
        """ """

    def search(self, **kw):
        """ Search OAIRecords in OAIRepository catalog """

def initialize(context):
    """ """
    #register classes
    import InfoFolder
    from constants import *
    context.registerClass(
        InfoFolder.NyInfoFolder,
        permission = PERMISSION_ADD_INFOFOLDER,
        constructors = (
                InfoFolder.infofolder_add_html,
                InfoFolder.addNyInfoFolder,
                ),
        icon = 'www/NyInfoFolder.gif'
        )

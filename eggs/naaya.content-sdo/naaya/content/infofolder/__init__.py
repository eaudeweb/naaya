def initialize(context):
    """ """
    #register classes
    import InfoFolder
    from permissions import PERMISSION_ADD_INFOFOLDER
    context.registerClass(
        InfoFolder.NyInfoFolder,
        permission = PERMISSION_ADD_INFOFOLDER,
        constructors = (
                InfoFolder.infofolder_add_html,
                InfoFolder.addNyInfoFolder,
                ),
        icon = 'www/NyInfoFolder.gif'
        )

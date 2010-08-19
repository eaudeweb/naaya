import observatory

def initialize(context):
    context.registerClass(
            observatory.NyObservatory,
            permission = 'Naaya - Add Observatory',
            constructors=(observatory.manage_addNyObservatory,)
            )


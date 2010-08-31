from Products.Naaya.constants import JS_MESSAGES

import observatory

OBS_JS_MESSAGES = [
    'Type country name',
    'You can not add pin here. To close to a recently added pin!',
    'Error loading points: ',
    'You must enter a comment for citizen reported pins!',
    'Please select pin type!',
    'Please select rating value!',
]

def initialize(context):
    JS_MESSAGES.extend(OBS_JS_MESSAGES);
    context.registerClass(
            observatory.NyObservatory,
            permission = 'Naaya - Add Observatory',
            constructors=(observatory.manage_addNyObservatory,)
            )


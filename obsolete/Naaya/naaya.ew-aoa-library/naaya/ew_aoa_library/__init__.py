from viewer import manage_addViewer_html, manage_addViewer
from viewer import AoALibraryViewer

def initialize(context):
    context.registerClass(AoALibraryViewer, constructors=(
        ('manage_addViewer_html', manage_addViewer_html),
        ('manage_addViewer', manage_addViewer),
    ))

from Products.naayaUpdater.updates import UpdateScript, PRIORITY

OLD_CODE = '''    <tal:block define="main_section_images python:skin['main_section_images']"
               condition="python:main_section_images.hasObject(mainsection_id)">
'''

NEW_CODE = '''    <tal:block define="main_section_images python:skin['main_section_images']"
               condition="python:main_section_images.hasObject(mainsection_id) and here.show_mainsection_image(here)">
'''

class UpdateElementMainsectionImage(UpdateScript):
    """ """
    title = 'Update element mainsection image'
    creation_date = 'Mar 13, 2013'
    authors = ['Valentin Dumitru']
    priority = PRIORITY['LOW']
    description = ('Update element_mainsection_image to respect the '
                    'inherit_mainsection_image flag when showing '
                    'the main section picture')

    def _update(self, portal):

        skin = portal.portal_layout.getCurrentSkin()
        if hasattr(skin, 'element_mainsection_image'):
            template = skin.element_mainsection_image.read()
            if OLD_CODE not in template:
                if NEW_CODE in template:
                    self.log.debug('element_mainsection_image already updated')
                else:
                    self.log.error('element_mainsection_image not really '
                                    'how we expect it to be')
                    return False
            else:
                first_part, second_part = template.split(OLD_CODE)
                template = '%s%s%s' % (first_part, NEW_CODE, second_part)
                skin.element_mainsection_image.write(template)
                self.log.debug('element_mainsection_image updated successfully.')
        else:
            self.log.error('No element_mainsection_image in active skin, '
                            'maybe not a CHM3 portal?')
            return False

        return True

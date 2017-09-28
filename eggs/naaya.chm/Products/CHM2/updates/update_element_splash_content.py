from Products.naayaUpdater.updates import UpdateScript, PRIORITY

OLD_CODE = '''						<div class="lof-main-item-desc">
							<h2 tal:on-error="string:" tal:content="python:photo.title.split('|')[0]" />
							<p tal:on-error="string:" tal:content="python:photo.title.split('|')[1]" />
						</div>
'''

NEW_CODE = '''						<div tal:define="photo_details python:photo.title.split('|');
									photo_heading python:photo_details[0]"
								tal:attributes="class python:test(photo_heading or len(photo_details)>1, 'lof-main-item-desc', 'hidden')">
							<h2 tal:on-error="string:" i18n:translate="" tal:content="photo_heading" />
							<p tal:on-error="string:" i18n:translate="" tal:content="python:photo_details[1]" />
						</div>
'''

class UpdateElementSplashContent(UpdateScript):
    """ """
    title = 'Update element splash content'
    creation_date = 'Mar 13, 2013'
    authors = ['Valentin Dumitru']
    priority = PRIORITY['LOW']
    description = ('Update element splash content to hide the dark overlay '
                    'if no title or subtitle available')

    def _update(self, portal):

        skin = portal.portal_layout.getCurrentSkin()
        if hasattr(skin, 'element_splash_content'):
            template = skin.element_splash_content.read()
            if OLD_CODE not in template:
                if NEW_CODE in template:
                    self.log.debug('element_splash_content already updated')
                else:
                    self.log.error('element_splash_content not really '
                                    'how we expect it to be')
                    return False
            else:
                first_part, second_part = template.split(OLD_CODE)
                template = '%s%s%s' % (first_part, NEW_CODE, second_part)
                skin.element_splash_content.write(template)
                self.log.debug('element_splash_content updated successfully.')
        else:
            self.log.error('No element_splash_content in active skin, '
                            'maybe not a CHM3 portal?')
            return False

        return True

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.updates.utils import get_standard_template

COOKIE_POLICY_DOCUMENT = '''
    <p>A <strong>cookie</strong> is a small piece of data sent from
    a website and stored in the user's computer. This information
    can be used for several purposes, including saving user
    identification, preferences on the site, choices from one page
    to another, etc.</p>

    <p>They can also be used for tracking user activity and
    browsing history, which from a certain level is a privacy concern (triggering law regulations in the EU and US).</p>

    <h2>Our policy</h2>
    <p>This website uses cookies with the exclusive purposes of enabling its services and enhancing user experience on the site. Examples include:</p>

    <ul>
    <li>saving user authentication</li>
    <li>setting site language preferences</li>
    <li>saving site preferences (like the full-screen toggle)</li>
    <li>well-functioning of applications (where users need to follow
    a procedure consisting of several steps, and preferences must be
    saved between steps) </li>
    </ul>

    <h2>Google Analytics</h2>
    <p>We also make use of Google Analytics, a Web analytics service provided by Google Inc., helping measuring traffic patterns to,
    from, and within our public Web sites. The information generated
    by the cookies about your use of the Web site (including your IP
    address, truncated to ensure your anonymity) is transmitted to Google. No personal, identifying information is recorded or
    provided to Google. This anonymous information is then used to
    evaluate visitors' use of the Web site and to compile statistical
    reports on our site activity. The aggregate data and statistical
    reports are used only to help us make our site more useful to
    visitors and are made available only to Web managers and other
    designated staff who require this information to perform their
    duties.</p>

    <p>For further information about Google Analytics, please refer to
    <a href="http://www.google.com/intl/en_ALL/privacy/privacy-policy.html">
    Google Analytics Privacy Policy</a>. Google Inc. offers a
    possibility to <a href="https://tools.google.com/dlpage/gaoptout?hl=en">
    disable Google Analytics</a> (including the setting of cookies).
    '''

ELEMENT_DISCLAIMER_info = '''<metal:block define-macro="content">
    <div id="disclaimer">
        <p><img src="misc_/Naaya/info.png" /><tal:block i18n:translate="">This site uses cookies in order to function as expected. By continuing, you are agreeing to our <a tal:attributes="href string:${site_url}/info/cookie_policy" i18n:name="cookie_policy_link" i18n:translate="">cookie policy</a>.</tal:block><br/>
        <a href="javascript:void(0);" id="acknowledge" i18n:translate="">Agree and close</a></p>
    </div>
</metal:block>'''
ELEMENT_DISCLAIMER_About = '''<metal:block define-macro="content">
    <div id="disclaimer">
        <p><img src="misc_/Naaya/info.png" /><tal:block i18n:translate="">This site uses cookies in order to function as expected. By continuing, you are agreeing to our <a tal:attributes="href string:${site_url}/About/cookie_policy" i18n:name="cookie_policy_link" i18n:translate="">cookie policy</a>.</tal:block><br/>
        <a href="javascript:void(0);" id="acknowledge" i18n:translate="">Agree and close</a></p>
    </div>
</metal:block>'''
COOKIE_POLICY_info = '''        <a tal:attributes="href string:${site_url}/info/cookie_policy"
            i18n:translate="">Cookie policy</a>'''
COOKIE_POLICY_About = '''        <a tal:attributes="href string:${site_url}/About/cookie_policy"
            i18n:translate="">Cookie policy</a>'''
DISCLAIMER_SLOT_CHM3 = '''    <metal:block define-slot="disclaimer">
      <metal:block use-macro="python:current_layout['element_disclaimer'].macros['content']"/>
    </metal:block>'''
DISCLAIMER_SLOT_CHM2 = '''    <metal:block define-slot="disclaimer">
      <metal:block use-macro="python:here.getLayoutTool().getCurrentSkin()['element_disclaimer'].macros['content']"/>
    </metal:block>'''
DISCLAIMER_CSS = '''/* Styling for the Cookies Disclaimer message */
#disclaimer {
	background: #FFE49D;
	position: absolute;
	width: 100%;
	padding: 5px 0px;
	border-bottom: 1px solid #555;
	display: none;
	top: 0px;
	z-index: 10000;
}

#disclaimer p {
	text-align: center;
}

#disclaimer img {
	padding-right:  5px;
	vertical-align: text-top;
}'''



class AddDisclaimerMessage(UpdateScript):
    """ """
    title = 'Add cookie disclaimer message'
    creation_date = 'Mar 5, 2013'
    authors = ['Valentin Dumitru']
    priority = PRIORITY['LOW']
    description = ('Add cookie disclaimer message (cookie based)')

    def _update(self, portal):

        policy_in_info = True
        standard_template = get_standard_template(portal)
        skin = portal.portal_layout.getCurrentSkin()
        scheme = portal.portal_layout.getCurrentSkinScheme()
        if hasattr(skin, 'common.css'):
            chm3 = True
        else:
            chm3 = False

        self.log.debug('1. element_footer')
        if hasattr(skin, 'element_footer'):
            element_footer = skin.element_footer.read()
            if 'cookie_policy' in element_footer:
                self.log.debug('   cookie_policy already in element_footer')
            elif 'Feedback</a>' in element_footer:
                if 'info/copyright' in element_footer:
                    element_footer = element_footer.replace('Feedback</a>',
                        '%s\n%s' % ('Feedback</a>', COOKIE_POLICY_info))
                    self.log.debug('   element_footer uses "info"')
                elif 'About/copyright' in element_footer:
                    policy_in_info = False
                    element_footer = element_footer.replace('Feedback</a>',
                        '%s\n%s' % ('Feedback</a>', COOKIE_POLICY_About))
                    self.log.debug('   element_footer uses "About"')
                else:
                    self.log.error("   element_footer doesn't have the expected format")
                    return False
                skin.element_footer.write(element_footer)
                self.log.debug('   cookie_policy added to element_footer')
            else:
                self.log.error("   element_footer doesn't have the expected format")
                self.log.error("   element_footer NOT updated")
        else:
            self.log.debug('   no element_footer, so we use standard_template')
            tal = standard_template.read()
            if 'cookie_policy' in tal:
                self.log.debug('   cookie_policy already in standard_template')
            elif 'Feedback</a>]' in tal:
                if 'info/copyright' in tal:
                    tal = tal.replace('Feedback</a>]',
                        '%s\n[%s]' % ('Feedback</a>]', COOKIE_POLICY_info))
                    self.log.debug('   standard_template uses "info"')
                elif 'About/copyright' in tal:
                    policy_in_info = False
                    tal = tal.replace('Feedback</a>]',
                        '%s\n[%s]' % ('Feedback</a>]', COOKIE_POLICY_About))
                    self.log.debug('   standard_template uses "About"')
                else:
                    self.log.error("   element_footer doesn't have the expected format")
                    return False
                standard_template.write(tal)
                self.log.debug('   standard template updated with cookie_policy link')
            else:
                self.log.error("   element_footer doesn't have the expected format")
                self.log.error("   element_footer NOT updated")

        self.log.debug('2. element_disclaimer')
        if hasattr(skin, 'element_disclaimer'):
            self.log.debug('   element_disclaimer already in skin')
        else:
            skin.manage_addTemplate(id='element_disclaimer')
            if policy_in_info:
                skin.element_disclaimer.write(ELEMENT_DISCLAIMER_info)
            else:
                skin.element_disclaimer.write(ELEMENT_DISCLAIMER_About)
            self.log.debug('   element_disclaimer successfully added')

        self.log.debug('3. create document')
        if policy_in_info:
            container = portal.info
        else:
            container = portal.About
        if hasattr(container, 'cookie_policy'):
            self.log.debug('   cookie_policy already present')
        else:
            from naaya.content.document.document_item import _create_NyDocument_object
            _create_NyDocument_object(container, 'cookie_policy', self.REQUEST.AUTHENTICATED_USER.getUserName())
            container.cookie_policy.saveProperties(
                title="Cookie policy", body=COOKIE_POLICY_DOCUMENT)
            container.cookie_policy.submit_this()
            self.log.debug('   cookie_policy document created in %s' % container.getId())

        self.log.debug('4. standard_template')
        tal = standard_template.read()
        if '"disclaimer">' in tal:
            self.log.debug('   disclaimer slot already in standard_template')
        elif '<div id="header">' not in tal:
            self.log.error("   standard_template doesn't have the expected <div id='header'>")
            return False
        else:
            if chm3:
                tal = tal.replace('<div id="header">',
                    '%s\n%s' % (DISCLAIMER_SLOT_CHM3, '<div id="header">'))
            else:
                tal = tal.replace('<div id="header">',
                    '%s\n%s' % (DISCLAIMER_SLOT_CHM2, '<div id="header">'))
            standard_template.write(tal)
            self.log.debug('   disclaimer slot added to standard_template')

        self.log.debug('5. common.css')
        if chm3:
            if skin['common.css'].meta_type == 'Naaya Disk File':
                self.log.debug('   common.css is DiskFile, no need for an update')
            else:
                common_css = skin['common.css'].data
                if 'Styling for the Cookies Disclaimer message' in common_css:
                    self.log.debug('   common.css already updated')
                else:
                    common_css = '%s\n%s' % (common_css, DISCLAIMER_CSS)
                    skin['common.css'].data = common_css
                    self.log.debug('   common.css updated')
        else:
            common_css = scheme.style_common.read()
            if 'Styling for the Cookies Disclaimer message' in common_css:
                self.log.debug('   style_common already updated')
            else:
                common_css = '%s\n%s' % (common_css, DISCLAIMER_CSS)
                scheme.style_common.write(common_css)
                self.log.debug('   style_common updated')
        return True

class Addi18nToDisclaimerMessage(UpdateScript):
    """ """
    title = 'Add i18n tags to the cookie disclaimer message'
    creation_date = 'Jul 10, 2014'
    authors = ['Valentin Dumitru']
    priority = PRIORITY['LOW']
    description = ('Add i18n tags to the cookie disclaimer message')

    def _update(self, portal):

        policy_in_info = True
        standard_template = get_standard_template(portal)
        skin = portal.portal_layout.getCurrentSkin()
        scheme = portal.portal_layout.getCurrentSkinScheme()
        if hasattr(skin, 'common.css'):
            chm3 = True
        else:
            chm3 = False

        if not hasattr(skin, 'element_disclaimer'):
            self.log.debug('   element_disclaimer not in skin')
        else:
            if policy_in_info:
                skin.element_disclaimer.write(ELEMENT_DISCLAIMER_info)
            else:
                skin.element_disclaimer.write(ELEMENT_DISCLAIMER_About)
            self.log.debug('   element_disclaimer successfully updated')

        return True    

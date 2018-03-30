from Products.naayaUpdater.updates import UpdateScript
from naaya.content.bestpractice.bestpractice_item import addNyBestPractice
from Products.NaayaCore.managers.utils import make_id
from Products.NaayaCore.EmailTool import EmailTool


class ConvertContactsBestpractice(UpdateScript):
    """
    Convert contacts from certain location to Best Practice objects
    """
    title = 'Convert contacts from certain location to Best Practice objects'
    creation_date = 'Mar 28, 2018'
    authors = ['Valentin Dumitru']
    description = ('Convert contacts from certain location to '
                   'Best Practice objects')

    def _update(self, portal):
        EmailTool.divert_mail()
        cat = portal.getCatalogTool()
        brains = cat(
            meta_type='Naaya Contact',
            path='/demo-design/good-practices/nominees-and-winners-awards')
        for brain in brains:
            ob = brain.getObject()
            old_id = ob.getId()
            parent = ob.aq_parent
            if '.old' not in old_id:
                parent.manage_renameObject(old_id, old_id + '.old')
                self.log.debug('%s updated' % ob.absolute_url())
            title = ob.getLocalProperty('title') or ob.getLocalProperty(
                'title', 'de')
            new_id = make_id(parent, title=title)
            landscape_type = ob.getLocalProperty('landscape_type')
            if not landscape_type:
                landscape_type = 'Unspecified'
            if isinstance(landscape_type, list):
                if len(landscape_type) == 1:
                    landscape_type = landscape_type[0]
            addNyBestPractice(
                parent, id=new_id, title=title,
                category=getattr(ob, 'category-marketplace'),
                description=ob.getLocalProperty('description'),
                topics=ob.topics, geo_location=ob.geo_location,
                landscape_type=landscape_type,
                coverage=ob.getLocalProperty('coverage'),
                contributor=ob.contributor, approved=ob.approved,
                submitted=ob.submitted, phone=ob.phone, fax=ob.fax,
                firstname=ob.getLocalProperty('firstname'),
                lastname=ob.getLocalProperty('lastname'),
                cellphone=ob.cellphone, email=ob.email, webpage=ob.webpage)
            new_ob = parent._getOb(new_id)
            l_props = [data['id'] for data in ob._local_properties_metadata]
            for lang in portal.gl_get_languages():
                for l_prop in l_props:
                    if l_prop not in ['firstname', 'lastname',
                                      'landscape_type']:
                        new_ob.set_localpropvalue(
                            l_prop, lang, ob.getLocalProperty(l_prop, lang))
            self.log.info('created BestPractice %s' % new_ob.absolute_url())
            self.log.info('deleted Contact %s' % ob.absolute_url())
            parent.manage_delObjects([old_id + '.old'])
        EmailTool.divert_mail(False)

        return True

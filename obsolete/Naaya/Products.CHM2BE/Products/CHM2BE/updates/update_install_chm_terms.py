from Products.naayaUpdater.updates import UpdateScript

class InstallCHMTermsGlossary(UpdateScript):
    """ """
    title = "Install chm_terms glossary"
    authors = ["Valentin Dumitru", "Andrei Laza"]
    creation_date = 'Oct 28, 2011'

    def _update(self, portal):
        glossary_ids = [ob.getId()
                for ob in portal.objectValues('Naaya Glossary')]
        if 'chm_terms' in glossary_ids:
            self.log.debug('chm_terms glossary already installed')
        else:
            portal.add_chm_terms_glossary()
            self.log.debug("added chm_terms glossary")

        schema_tool = portal.getSchemaTool()
        for schema in ['NyBFile', 'NyContact', 'NyDocument',
                       'NyEduProduct', 'NyEvent', 'NyExFile',
                       'NyExpert', 'NyFile', 'NyFolder', 'NyGeoPoint',
                       'NyMediaFile', 'NyNews', 'NyOrganisation',
                       'NyPhotoGallery', 'NyPhotoFolder', 'NyPhoto',
                       'NyPointer', 'NyProject', 'NyStory', 'NyURL']:
            if not getattr(schema_tool.aq_base, schema, None):
                continue
            schema_obj = getattr(schema_tool, schema, None)
            if getattr(schema_obj, 'chm_terms-property', None):
                continue

            self.log.debug('adding chm_terms property for %s', schema)
            schema_obj.addWidget(name='chm_terms',
                    widget_type='Glossary', data_type='str', localized=True)
            chm_terms_property = getattr(schema_obj, 'chm_terms-property')
            chm_terms_property.saveProperties(
                    glossary_id="chm_terms", title='CHM Terms',
                    sortorder='65', visible=True,
                    display_mode='values-list', separator='|')
            self.log.debug('added chm_terms property for %s', schema)
        return True

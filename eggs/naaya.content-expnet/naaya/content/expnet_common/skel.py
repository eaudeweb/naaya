import itertools
import logging

TOPICS = [
  {'title_en': u"Status and trends of the components of biological diversity",
   'title_nl': u"Status en trends van componenten van biologische diversiteit",
   'subtopics': [
      {'title_en': u"Abundance and distribution of species",
       'title_nl': u"Aantal en verspreiding van soorten"},
      {'title_en': u"Status of threathened species",
       'title_nl': u"Status van bedreigde soorten"},
      {'title_en': u"Extent of selected biomes, ecosystems and habitats",
       'title_nl': u"Areaal van specifieke biomen, ecosystemen en habitats"},
      {'title_en': u"Genetic diversity",
       'title_nl': u"Genetische diversiteit"},
      {'title_en': u"Coverage of protected areas",
       'title_nl': u"Omvang van beschermde gebieden"},
      {'title_en': u"Island biodiversity",
       'title_nl': u"Biodiversiteit van Eilanden"},
      {'title_en': u"Mountain biodiversity",
       'title_nl': u"Biodiversiteit van Bergen"},
      {'title_en': u"Identification, Monitoring, Indicators and Assessments",
       'title_nl': u"Identificatie, Monitoring, Indicatoren en Evaluaties"},
    ]},
  {'title_en': u"Sustainable use of biological diversity",
   'title_nl': u"Duurzaam gebruik van biodiversiteit",
   'subtopics': [
      {'title_en': u"Forest under sustainable management",
       'title_nl': u"Bossen onder duurzaam beheer"},
      {'title_en': u"Agricultural practices potentially supporting "
                   u"biodiversity",
       'title_nl': u"Landbouw praktijken welke potentieel gunstig zijn "
                   u"voor biodiversiteit"},
      {'title_en': u"Sustainable fishery and aquaculture management",
       'title_nl': u"Duurzame visserij en aquacultuur management"},
      {'title_en': u"Products derived from sustainable sources",
       'title_nl': u"Producten vanuit duurzame bronnen"},
      {'title_en': u"Ecological Footprint",
       'title_nl': u"Ecologische Voetafdruk"},
    ]},
  {'title_en': u"Threats to biodiversity",
   'title_nl': u"Bedreigingen voor biodiversiteit",
   'subtopics': [
      {'title_en': u"Nitrogen deposition",
       'title_nl': u"Stikstof depositie"},
      {'title_en': u"Invasive alien species",
       'title_nl': u"Invasieve exotische soorten"},
      {'title_en': u"Climate change",
       'title_nl': u"Klimaatverandering"},
      {'title_en': u"Desertification",
       'title_nl': u"Woestijnvorming"},
    ]},
  {'title_en': u"Ecosystem integrity and Ecosystem goods and services",
   'title_nl': u"Integriteit van ecosystemen en ecosysteemdiensten",
   'subtopics': [
      {'title_en': u"Marine Trophic Index",
       'title_nl': u"Mariene Trofische index"},
      {'title_en': u"Fragmentation of natural and semi-natural areas",
       'title_nl': u"Fragmentatie van natuurlijke en semi-natuurlijke "
                   u"gebieden"},
      {'title_en': u"Fragmentation of river systems",
       'title_nl': u"Fragmentatie van riviersystemen"},
      {'title_en': u"Nutrients in transitional, coastal and marine waters",
       'title_nl': u"Nutri\xebnten in kust- en zeewateren"},
      {'title_en': u"Water quality of freshwater ecosystems",
       'title_nl': u"Waterkwaliteit van zoetwater ecosystemen"},
      {'title_en': u"Health and well-being of humans",
       'title_nl': u"Gezondheid en welzijn van mensen"},
      {'title_en': u"Biodiversity for food and medicine",
       'title_nl': u"Biodiversiteit voor voedsel en medicijnen"},
      {'title_en': u"Biodiversity and tourism",
       'title_nl': u"Biodiversiteit en toerisme"},
    ]},
  {'title_en': u"Knowledge of biodiversity",
   'title_nl': u"Kennis van biodiversiteit",
   'subtopics': [
      {'title_en': u"Traditional knowledge",
       'title_nl': u"Traditionele kennis"},
      {'title_en': u"Innovations",
       'title_nl': u"Innovaties"},
      {'title_en': u"Best practices",
       'title_nl': u"Praktijkvoorbeelden"},
    ]},
  {'title_en': u"Access to genetic resources and benefit-sharing",
   'title_nl': u"Toegang tot genetische bronnen en het delen van voordelen"},
  {'title_en': u"Resources for biodiversity",
   'title_nl': u"Hulpbronnen voor biodiversiteit",
   'subtopics': [
      {'title_en': u"Financing biodiversity management",
       'title_nl': u"Financiering van beheer van biodiversiteit"},
      {'title_en': u"Technology transfer and cooperation",
       'title_nl': u"Technologieoverdracht en samenwerking"},
      {'title_en': u"Liability and Redress",
       'title_nl': u"Aansprakelijkheid en compensatie"},
    ]},
  {'title_en': u"Public opinion about biodiversity and public awareness",
   'title_nl': u"Publieke opinie over biodiversiteit en besef van urgentie"},
]

log = logging.getLogger('naaya.content.expnet_common')

def setup_expnet_skel(portal):
    portlets_tool = portal.getPortletsTool()
    itopics = getattr(portlets_tool, 'expnet_topics', None)
    if not itopics:
        log.info('Creating ExpNet ref tree')
        portlets_tool.manage_addRefTree('expnet_topics',
                                        "Topics for experts network")
        ref_tree = portlets_tool['expnet_topics']
        trans = portal.getPortalTranslations()

        def translate_node(node):
            if 'nl' in portal.gl_get_languages():
                trans(node['title_en']) # add message to translations db
                log.debug('Saving Dutch translation for topic title %r: %r',
                          node['title_en'], node['title_nl'])
                trans.message_edit(trans.get_message_key(node['title_en']),
                                   'nl', node['title_nl'], '')

        counter = itertools.count(1)
        def add_node(node, parent_id):
            node_id = str(counter.next())
            title = node['title_en']
            log.debug('Creating ExpNet ref tree node %r (title: %r)',
                      node_id, title)
            ref_tree.manage_addRefTreeNode(node_id, title, parent_id)
            translate_node(node)

            for subnode in node.get('subtopics', []):
                add_node(subnode, node_id)

        for top_node in TOPICS:
            add_node(top_node, None)

    #Create catalog index if it doesn't exist
    catalog_tool = portal.getCatalogTool()

    if not 'topics' in catalog_tool.indexes():
        log.info('Creating ExpNet catalog index "topics"')
        try:
            catalog_tool.addIndex('topics', 'KeywordIndex',
                           extra={'indexed_attrs' : 'main_topics'})
            catalog_tool.manage_reindexIndex(['topics'])
        except:
            print ( 'Failed to create topics index. Naaya Expert content '
                    'type may not work properly' )

    if not 'title_field' in catalog_tool.indexes():
        log.info('Creating ExpNet catalog index "title_field"')
        try:
            catalog_tool.addIndex('title_field', 'FieldIndex',
                           extra={'indexed_attrs' : 'title'})
            catalog_tool.manage_reindexIndex(['title_field'])
        except:
            print ( 'Failed to create title_field index. Naaya Expert '
                    'Network content types may not work properly.' )

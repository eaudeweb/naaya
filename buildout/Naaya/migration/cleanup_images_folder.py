"""Delete unused non-image files from demo-design/images (Python 2 and 3).

Usage: bin/<instance> run cleanup_images_folder.py [--dry-run]
"""
from __future__ import print_function

import sys

import transaction

SITE = 'demo-design'

# Non-image uploads; 6 appear only as broken <img> tags, the rest nowhere (checked 2026-10-12).
IDS = [
    '20140929_flyer_insekten_leuchtmittel_2014_web.pdf',
    '5.flower-tool1.pptx',
    '6-tourcoop-projects.pptx',
    '87492',
    'DestiNet picture example2.pptx',
    'Heritage.htm',
    'Logos of Certificates per Region New New Version.ppt',
    'Natura 2000.pdf',
    'Nuovo Documento di Microsoft Word.docx',
    'Tourism Knowledge and Innovation Communities Handbook Cover.pdf',
    'Untitled.pdf',
    'affect-theory-and-attractiveness-destinations.pdf',
    'bed-bug-safe-label.pdf',
    'biodiversitaet-standards-und-qualitaetssiegeln_-baseline-report.pdf',
    'blauer-see_luenne.docx',
    'bto-logo.pdf',
    'cantoni-lorenzo-universita-della-svizzera-italiana.htm',
    'certifcates-and-labels-picture1.pptx',
    'certified-criteria_worksheet-german.pdf',
    'certified-green-hotels.xlsx',
    'certifiedpreislisteab01072022.pdf',
    'community-based-tourism-training-trainers-cbt-tot-_certificate-achievement.pdf',
    'condensed-2017-gen-will.pdf',
    'cover_var_4_nfi_tourismus_labelguide_2023_a6_quer_titel.pdf',
    'create-event.mp4',
    'csr-biodiv-design-buttons-146px.zip',
    'csr-biodiv-design-buttons-146px.zip-1',
    'csr-biodiv-design-buttons-26px.zip',
    'csr-biodiv-design-grk-buttons-146px.zip',
    'destinet-buttons-final.ai',
    'destinet-icons.zip',
    'dig-ppt-4-slides-v1-19apr2014-hh-v3-hyperlinks-page1.pdf',
    'draft-matera-event_18-november-2019_afternoon.pdf',
    'drive-download-20190425t153052z-001.zip',
    'dropbox.exe',
    'ecoact-logo.aspx',
    'ecoact-project-logo.pdf',
    'ecotrans member logo.emf',
    'ecotrans-15-20.pptx',
    'ecotrans-2024-2030-diagramm-01062024.pptx',
    'ecotrans-2024-v1.pptx',
    'ecotrans-agm-rd-statement-recorded.pdf',
    'ecotrans-financial-report-2024.xlsx',
    'ecotrans-good-practice-collection-conceptv1-hh.pptx',
    'email.htm',
    'emas_logo.wmf',
    'etgg2030-ruready-context-purpose.pptx',
    'file.txt',
    'file.txt-1',
    'file.txt-10',
    'file.txt-11',
    'file.txt-12',
    'file.txt-13',
    'file.txt-14',
    'file.txt-15',
    'file.txt-16',
    'file.txt-17',
    'file.txt-18',
    'file.txt-19',
    'file.txt-2',
    'file.txt-20',
    'file.txt-21',
    'file.txt-22',
    'file.txt-23',
    'file.txt-3',
    'file.txt-4',
    'file.txt-5',
    'file.txt-6',
    'file.txt-7',
    'file.txt-8',
    'file.txt-9',
    'fischratgeber-rezepte-juni-2014.pdf',
    'fwd-acta-new-logo.msg',
    'genevieve-1.mp4',
    'green-destination.htm',
    'green-travmap-turkey.docx',
    'greenleader_english_high-res.ai',
    'grkd-10-logos.zip',
    'grkd-gtm-information-itb-v2-hh-en.pptx',
    'gruene-reisekarte-deutschland_hh.doc',
    'grune-reisekarte-deutschland-fur-destinationen-info-dezember-2016-2.pdf',
    'guidelines-applying-precautionary-principle-biodiversity-conservation-and',
    'image-green.htm',
    'infosammlung-natursport.pdf',
    'itb2019-flyer-v5.pptx',
    'iucn-ew-wbcsd-handbook.pdf',
    'knowledge-round1.pptx',
    'kontrollbericht-biohonig-wenzel.pdf',
    'labelguide_dritte_auflage_de_2016.pdf',
    'layout-tiles-destinet-main-pages-topics-v2.pptx',
    'logo prod RBs.doc',
    'logo_ecotrans-gruen-neu.ai',
    'logos-30-zertifikate.zip',
    'logos-zertifikate-labelguide-de-2014.zip',
    'logos.zip',
    'logos.zip-1',
    'mpa-2018_en.pdf',
    'olympic-truce-train-trainers-workshop-jordan.pdf',
    'outlook-kontakte-duplicates.csv',
    'phto.doc',
    'picture-certified-tourism-section.pptx',
    'programme-flyer-v1.pptx',
    'quizz-triangle-tourism-value-chain-management-and-fair-trade.docx',
    'quizz-triangle-tourism-value-chain-management-and-fair-trade.docx-1',
    'sonja-gottlebe-digital-professional-certificate-sustainable-tourism-2021.pdf',
    'south carolina.htm',
    'speisekarte-kalinski.pdf',
    'ta_gl_logo_2017_outline-10.eps',
    'title-page.docx',
    'transdanube_eu.htm',
    'travel-green-europe-app-concept-v1.pptx',
    'triangle-t-etgg.pptx',
    'tucumjangada.htm',
    'we10_12_fahrtziel_natur_2015.pdf',
    'widget-link-explained-bookdifferent.pdf',
    'workshop-programme.docx',
    'xmas-card-ecotrans-changes-2013-14.pptx',
    'xmas-sweets.pptx',
]

dry_run = '--dry-run' in sys.argv
folder = app[SITE].getImagesFolder()  # noqa: F821
present = [i for i in IDS if i in folder.objectIds()]
missing = [i for i in IDS if i not in present]
size = sum(folder._getOb(i).get_size() for i in present)
print('%d of %d files present, %.1f MB; missing: %s'
      % (len(present), len(IDS), size / 1e6, missing or 'none'))
folder.manage_delObjects(present)
if dry_run:
    transaction.abort()
    print('Dry run, nothing deleted.')
else:
    transaction.get().note('Delete unused non-image files from %s/images' % SITE)
    transaction.commit()
    print('Deleted %d files. Pack the database to reclaim the space.' % len(present))

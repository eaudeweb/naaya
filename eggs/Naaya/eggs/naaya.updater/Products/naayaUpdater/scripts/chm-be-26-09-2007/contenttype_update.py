for portal in container.get_portals(exclude=False):
  portal_forms = portal.portal_forms

  #Naaya Event - update
  if portal.id in ['bch-cbd', 'test_layout_arnaud', 'maroc2']:
    #index orig, edit svn, add upd
    event_add_upd = portal_forms.event_add.document_src()
    event_add_upd = event_add_upd.replace(container.contenttype_data('EVENT_ADD_ORIG'),container.contenttype_data('EVENT_ADD_UPD'))
    portal_forms.event_add.pt_edit(text=event_add_upd, content_type='text/html')

  #Naaya Document - update
    #all orig

  #Naaya News - update
  if portal.id in ['bch-cbd', 'test_layout_arnaud', 'maroc2', 'comifac_dev']:
    #index orig, edit svn, add upd
    portal_forms.news_edit.pt_edit(text=container.get_fs_data('Products/NaayaContent/NyNews/zpt/news_edit.zpt'), content_type='text/html')
    news_add_upd = portal_forms.news_add.document_src()
    news_add_upd = news_add_upd.replace(container.contenttype_data('EVENT_ADD_ORIG'),container.contenttype_data('EVENT_ADD_UPD'))
    portal_forms.news_add.pt_edit(text=news_add_upd, content_type='text/html')

  #Naaya Story - update
  if portal.id in ['bch-cbd', 'test_layout_arnaud', 'maroc2', 'comifac_dev']:
    #index svn, edit svn, add upd
    portal_forms.story_index.pt_edit(text=container.get_fs_data('Products/NaayaContent/NyStory/zpt/story_index.zpt'), content_type='text/html')
    portal_forms.story_edit.pt_edit(text=container.get_fs_data('Products/NaayaContent/NyStory/zpt/story_edit.zpt'), content_type='text/html')
    story_add_upd = portal_forms.story_add.document_src()
    story_add_upd = story_add_upd.replace(container.contenttype_data('STORY_ADD_ORIG1'),container.contenttype_data('STORY_ADD_UPD1'))
    story_add_upd = story_add_upd.replace(container.contenttype_data('STORY_ADD_ORIG2'),container.contenttype_data('STORY_ADD_UPD2'))
    portal_forms.story_add.pt_edit(text=story_add_upd, content_type='text/html')

  #Naaya URL - update
    #all orig

  #Naaya Pointer - update
  if portal.id in ['bch-cbd', 'test_layout_arnaud', 'maroc2', 'comifac_dev']:
    #index orig, edit svn, add svn+upd
    portal_forms.pointer_edit.pt_edit(text=container.get_fs_data('Products/NaayaContent/NyPointer/zpt/pointer_edit.zpt'), content_type='text/html')
    portal_forms.pointer_add.pt_edit(text=container.get_fs_data('Products/NaayaContent/NyPointer/zpt/pointer_add.zpt'), content_type='text/html')
    pointer_add_upd = portal_forms.pointer_add.document_src()
    pointer_add_upd = pointer_add_upd.replace(container.contenttype_data('POINTER_ADD_ORIG'),container.contenttype_data('POINTER_ADD_UPD'))
    portal_forms.pointer_add.pt_edit(text=pointer_add_upd, content_type='text/html')

  #Naaya File - update
    #index orig, edit orig, add orig

  #Naaya Media File - update
    #index svn, edit upd, add upd, subtitle svn
  if portal.id in ['bch-cbd', 'test_layout_arnaud', 'maroc2', 'comifac_dev']:
    mediafile_add_upd = portal_forms.mediafile_add.document_src()
    mediafile_add_upd = mediafile_add_upd.replace(container.contenttype_data('MEDIAFILE_ADD_ORIG'),container.contenttype_data('MEDIAFILE_ADD_UPD'))
    portal_forms.mediafile_add.pt_edit(text=mediafile_add_upd, content_type='text/html')
    portal_forms.mediafile_edit.pt_edit(text=container.contenttype_data('MEDIAFILE_EDIT'), content_type='text/html')

print 'Done.'
return printed

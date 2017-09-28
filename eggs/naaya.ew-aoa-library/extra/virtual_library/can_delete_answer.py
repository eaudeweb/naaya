site = container.getSite()
rt_library_ids = site['review-template-viewer'].get_library_ids()
return answer_id not in rt_library_ids

rstk = context.rstk
events = []

for event_ob in context.getCatalogedObjectsCheckView(meta_type='Naaya Event', approved=1):
    try:
        event_date = rstk.convert_DateTime_to_datetime(event_ob.start_date)
    except:
        event_date = rstk.convert_DateTime_to_datetime(event_ob.releasedate)
    events.append({
        'is_local': True,
        'title': event_ob.title_or_id(),
        'date': event_date,
        'summary': context.html2text(event_ob.description, None) or "",
        'url': event_ob.absolute_url(),
    })

for channel in context.getSyndicationTool()['aggregated_events_feed']. getRemoteChannelsItems():
    for event_item in channel:
        events.append({
            'is_local': False,
            'title': event_item['title'],
            'date': rstk.parse_string_to_datetime (event_item['date']),
            'summary': event_item['summary'],
            'url': event_item['link'],
        })

def trim(text, max_len):
    if len(text) > max_len:
        return text[:max_len] + '...'
    else:
        return text

for event in events:
    event['summary_80chars'] = trim(event['summary'], 80)
    event['summary_500chars'] = trim(event['summary'], 500)

events.sort(key=lambda event: event['date'])
now = rstk.convert_DateTime_to_datetime (context. ZopeTime())
return filter(lambda event: event['date'] > now, events)


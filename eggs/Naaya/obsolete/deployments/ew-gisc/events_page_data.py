if container.checkPermissionPublishObjects():
    people_and_events_data = context.html2text(container['gisc-project']['documents']['gisc']['internal']['people-and-events'].body, None)
else:
    people_and_events_data = ''

clean_text = lambda value: value.replace('&nbsp;', ' ').replace('&amp;', '&').strip()

people_and_events = {}
i = 0
while True:
    try:
        i_start = people_and_events_data.index('{{', i)
        i_middle = people_and_events_data.index('--', i_start+2)
        i_end = people_and_events_data.index('}}', i_middle+2)
    except ValueError:
        break
    event_url = clean_text(people_and_events_data[i_start+2:i_middle])
    person_name = clean_text(people_and_events_data[i_middle+2:i_end])
    people_and_events.setdefault(event_url, []).append(person_name)
    i = i_end+2

events = container.aggregated_events()

events_by_month = {}
for event in events:
    event['assigned_people'] = people_and_events.get(event['url'], [])
    #event['debug'] = people_and_events
    zd = context.rstk.convert_datetime_to_DateTime(event['date']) # since we can't call strftime() for normal datetime objects, we need to use the Zope DateTime
    month = (zd.strftime('%Y %m'), zd.strftime('%B %Y')) # we store a sortable value, and the pretty month name, in a tuple, and use that as key
    events_by_month.setdefault(month, []).append(event)

months = events_by_month.keys()
months.sort()
return [{'month': key[1], 'events': events_by_month[key]} for key in months]


from DateTime import DateTime

base_filter = filters[0]

interval_start_date = kwargs.get('interval_start_date', None)
if interval_start_date:
    base_filter['end_date'] = {'query': DateTime(interval_start_date), 'range': 'min'}

interval_end_date = kwargs.get('interval_end_date', None)
if interval_end_date:
    base_filter['start_date'] = {'query': DateTime(interval_end_date), 'range': 'max'}

target_group = kwargs.get('target-group', [])
if target_group:
    base_filter['target_group'] = target_group

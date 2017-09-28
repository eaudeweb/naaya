def list_settings(db_statement):
    def to_int(value):
        if value is None:
            return None
        else:
            return int(str(value))

    class Entry(dict):
        def __repr__(self):
            return "<%s = %r>" % (self.name, self.value)
        def children_with_name(self, name):
            for child in self.values():
                if child.name == name:
                    yield child
        def child_value(self, name):
            try:
                return list(self.children_with_name(name))[0].value
            except IndexError:
                raise KeyError("Missing entry %r in %r" % (name, self))

    entries = {None: Entry()}

    with db_statement("SELECT * FROM Settings") as result_lines:
        for line in result_lines:
            entry = Entry()
            entry_id = to_int(line[0])
            entry.parent_id = to_int(line[1])
            entry.name = line[2]
            entry.value = line[3]
            entries[entry_id] = entry

    for entry_id, entry in entries.iteritems():
        if entry_id is None:
            entry.name = entry.value = "ROOT"
        else:
            entries[entry.parent_id][entry_id] = entry

    return entries[None][0]

def list_metadata(db_statement):
    fields = ['uuid', 'schemaId', 'isTemplate', 'isHarvested',
              'createDate', 'changeDate', 'source', 'title', 'root',
              'harvestUuid', 'harvestUri']
    bool_filter = {'y':True, 'n':False}.get
    query = "SELECT %s FROM Metadata" % ','.join(fields)
    with db_statement(query) as result_lines:
        for line in result_lines:
            item = dict(zip(fields, line))
            item['isHarvested'] = bool_filter(item['isHarvested'])
            item['isTemplate'] = bool_filter(item['isTemplate'])
            yield item

def gen_metadata(db_statement):
    fields = ['id', 'uuid', 'schemaId', 'isTemplate', 'isHarvested',
              'createDate', 'changeDate', 'data', 'source', 'title',
              'root', 'harvestUuid', 'owner', 'groupOwner', 'harvestUri',
              'rating', 'popularity']
    query = "SELECT %s FROM Metadata" % ','.join(fields)
    with db_statement(query) as result_lines:
        for line in result_lines:
            item = dict(zip(fields, line))
            for f in ['id', 'owner', 'groupOwner', 'rating', 'popularity']:
                if f in item and item[f] is not None:
                    item[f] = item[f].value
            yield item


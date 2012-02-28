def fix_exceptions(names, line, warn):
    idx = names.index

    # missing info
    if len(names) == len(line):
        return

    # malformed lines
    if len(names) == 19 and len(line) == 14:
        for i in range(5):
            line.insert(idx('OVERWRITE'), '')
        if not line[idx('TITLE')]:
            line[idx('TITLE')] = line[idx('FILENAME')].rsplit('/', 1)[-1]
        warn('Very short line: %r' % line)
    elif (line[idx('UPLOADDATE')] == '@circa' and
        line[idx('REFERENCE')] == '00/00/0000' and
        line[idx('CREATED')] == '00/00/0000'):

        #warn('WEIRD LINE: %r' % line)
        del line[idx('ISSUEDATE')]
        for name in ('ISSUEDATE', 'UPLOADDATE'):
            line[idx(name)] = ''
        line[idx('OWNER')] = ''
        line[idx('RANKING')] = 'Public'

    elif (line[idx('OWNER')] == '' and line[idx('UPLOADDATE')] == ''):
        if line[idx('FILENAME')].endswith('/'):
            line[idx('OWNER')] = ''
            #warn('WEIRD LINE: %r' % line)
        else:
            warn('WEIRD LINE: %r' % line)

    elif (line[idx('URN')] == '32460' and
        line[idx('FILENAME')].endswith('1276514784.url')):
        del line[idx('TITLE')]
        return True

    elif (line[idx('TITLE')].strip() == ''
          and line[idx('ABSTRACT')] == 'Public'):
        del line[idx('TITLE')]
        return True

    else:
        assert len(line) == len(names), 'busted line: %r, names: %r' % (line, names)

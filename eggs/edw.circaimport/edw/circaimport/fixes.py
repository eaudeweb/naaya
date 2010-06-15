def fix_exceptions(names, line, warn):
    idx = names.index

    # missing info
    if len(names) == len(line):
        return

    # malformed lines
    if (line[idx('UPLOADDATE')] == '@circa' and
        line[idx('REFERENCE')] == '00/00/0000' and
        line[idx('CREATED')] == '00/00/0000'):

        #warn('WEIRD LINE: %r' % line)
        del line[idx('ISSUEDATE')]
        for name in ('ISSUEDATE', 'UPLOADDATE'):
            line[idx(name)] = ''
        line[idx('OWNER')] = 'moregale'
        line[idx('RANKING')] = 'Public'

    elif (line[idx('OWNER')] == '' and line[idx('UPLOADDATE')] == ''):
        if line[idx('FILENAME')].endswith('/'):
            line[idx('OWNER')] = 'moregale'
            #warn('WEIRD LINE: %r' % line)
        else:
            warn('WEIRD LINE: %r' % line)

    elif (line[idx('URN')] == '32460' and
        line[idx('FILENAME')].endswith('1276514784.url')):
        del line[idx('TITLE')]
        return True

    else:
        assert len(line) == len(names), 'busted line: %r' % line

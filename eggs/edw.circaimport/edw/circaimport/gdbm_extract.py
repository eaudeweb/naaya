import sys
import gdbm
import csv


def gdbm2csv(dbpath, csvpath):
    db = gdbm.open(dbpath, 'r')
    csv_file = open(csvpath, 'wb')
    writer = csv.writer(csv_file)
    for k in db.keys():
        if not db[k]:
            continue
        values = [val.strip(')|(') for val in db[k].split(')|(')]
        row = [k] + values
        writer.writerow(row)
    db.close()
    csv_file.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: python %s <in-file.gdbm> <out-file.csv>' % sys.argv[0]
        sys.exit(1)

    try:
        gdbm2csv(sys.argv[1], sys.argv[2])
    except ValueError:
        print 'Usage: python %s <in-file.gdbm> <out-file.csv>' % sys.argv[0]
        sys.exit(1)

from sys import argv, exit
from os.path import isdir, isfile, splitext
from os import listdir, mkdir


from DocumentConverter import DocumentConverter, DocumentConversionException


if __name__ == '__main__':
    if len(argv) < 3:
        print 'USAGE: python %s <input-folder> <output-folder>' % argv[0]
        exit(255)

    if not isdir(argv[1]):
        print 'no such input folder: %s' % argv[1]
        exit(1)

    if not isdir(argv[2]):
        print 'no such output folder: %s' % argv[2]
        exit(1)

    for entry in listdir(argv[1]):
        fpath = argv[1]+'/'+entry
        if isfile(fpath):
            fname = splitext(entry)[0]
            #print 'found file %s with name %s' % (entry, fname)
            new_fpath = argv[2]+'/'+fname
            if not isdir(new_fpath):
                mkdir(new_fpath)
            try:
                converter = DocumentConverter()
                converter.convert(fpath, new_fpath + ('/%s.pdf' % fname))
            except DocumentConversionException, exception:
                print "ERROR!" + str(exception)
                exit(1)
            except Exception, exception:
                print "ERROR! ErrorCodeIOException %s" % exception
                exit(1)
        #else:
        #    print 'found non-file %s' % entry



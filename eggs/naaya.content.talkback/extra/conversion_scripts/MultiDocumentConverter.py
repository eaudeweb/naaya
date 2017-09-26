from sys import argv, exit
from os.path import isdir, isfile, splitext
from os import listdir, mkdir


from DocumentConverter import DocumentConverter, DocumentConversionException
from Convertor2 import convert_file


if __name__ == '__main__':
    if len(argv) < 3:
        print 'USAGE: python %s <input-folder> <output-folder>' % argv[0]
        exit(255)
    else:
        input_folder = argv[1]
        output_folder = argv[2]

    if not isdir(input_folder):
        print 'no such input folder: %s' % input_folder
        exit(1)

    if not isdir(output_folder):
        print 'no such output folder: %s' % output_folder
        exit(1)

    for entry in listdir(input_folder):
        fpath = input_folder+'/'+entry
        if isfile(fpath):
            fname = splitext(entry)[0]
            #print 'found file %s with name %s' % (entry, fname)
            new_fpath = output_folder+'/'+fname
            if not isdir(new_fpath):
                mkdir(new_fpath)
            try:
                converter = DocumentConverter()
                converter.convert(fpath, new_fpath + ('/%s.html' % fname))
                converter.convert(fpath, new_fpath + ('/%s.pdf' % fname))

                convert_file(new_fpath, fname+'.html')
            except DocumentConversionException, exception:
                print "ERROR!" + str(exception)
                exit(1)
            except Exception, exception:
                print "ERROR! ErrorCodeIOException %s" % exception
                exit(1)
        #else:
        #    print 'found non-file %s' % entry



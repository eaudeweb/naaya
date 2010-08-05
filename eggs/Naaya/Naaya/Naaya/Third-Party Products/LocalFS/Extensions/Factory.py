
class XMLDocumentFactory:

    def __call__(self, id, file):
        try: from Products.XMLDocument.XMLDocument import Document
        except: return
        ob = Document()
        ob.id = ob.__name__= id
        ob.parse(file)
        return ob

    def save(self, ob, path):
        f = open(path, 'w')
        f.write(ob.toXML())
        f.close()

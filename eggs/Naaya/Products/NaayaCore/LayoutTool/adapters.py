class TemplateSource(object):
    def __init__(self, template):
        self.template = template

    def __call__(self):
        try:
            self.template.read()
        except:
            pass
        return self.template._text

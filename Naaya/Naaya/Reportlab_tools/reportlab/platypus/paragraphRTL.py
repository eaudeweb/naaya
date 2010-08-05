from reportlab.platypus.paragraph import Paragraph


class ParagraphRTL(Paragraph):
    def beginText(self, x, y):
        return self.canv.beginTextRTL(x, y)


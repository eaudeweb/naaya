from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from contentratings.interfaces import _


def titled_vocab(items):
    terms = [SimpleTerm(k, title=v) for k,v in items]
    return SimpleVocabulary(terms)

five_star_vocab = titled_vocab(((1, _(u'Poor')),
                          (2, _(u'Fair')),
                          (3, _(u'Good')),
                          (4, _(u'Very Good')),
                          (5, _(u'Excellent'))))

three_star_vocab = titled_vocab(((1, _(u'Unacceptable')),
                                 (2, _(u'Acceptable')),
                                 (3, _(u'Excellent'))))


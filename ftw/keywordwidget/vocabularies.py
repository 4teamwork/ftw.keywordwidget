from binascii import b2a_qp
from plone.dexterity.utils import safe_unicode
from plone.dexterity.utils import safe_utf8
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class UnicodeKeywordsVocabulary(object):
    """ This is a copy of plone.app.vocabularies.catalog.KeywordsVocabulary
    with one significant difference the values of the vocabulary terms are
    unicode instead of utf-8. The catalog should return utf-8 by convention.

    Plus it allows you to choose the index_name, which is used to build the
    vocabulary.
    """
    index_name = 'unicode_keywords'

    def __init__(self, index_name=None):
        if index_name:
            self.index_name = index_name

    def __call__(self, context):

        site = getSite()
        self.catalog = getToolByName(site, "portal_catalog", None)
        if self.catalog is None:
            return SimpleVocabulary([])
        index = self.catalog._catalog.getIndex(self.index_name)

        # Vocabulary term tokens *must* be 7 bit values, titles *must* be
        # unicode
        items = [
            SimpleTerm(safe_unicode(i), b2a_qp(safe_utf8(i)), safe_unicode(i))
            for i in index._index
        ]
        return SimpleVocabulary(items)


UnicodeKeywordsVocabularyFactory = UnicodeKeywordsVocabulary()

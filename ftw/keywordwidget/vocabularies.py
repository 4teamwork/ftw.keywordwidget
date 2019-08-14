from binascii import b2a_qp
from ftw.keywordwidget.utils import safe_utf8
from ftw.keywordwidget.utils import as_keyword_token
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from z3c.formwidget.query.interfaces import IQuerySource
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
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

        if self.index_name in self.catalog._catalog.indexes:
            index = self.catalog._catalog.getIndex(self.index_name)
            # Vocabulary term tokens *must* be 7 bit values, titles *must* be
            # unicode
            items = [
                SimpleTerm(safe_unicode(i),
                           b2a_qp(safe_utf8(i)),
                           safe_unicode(i))
                for i in index._index
            ]
            return SimpleVocabulary(items)

        else:
            return SimpleVocabulary([])

UnicodeKeywordsVocabularyFactory = UnicodeKeywordsVocabulary()


class IKeywordWidgetAddableSource(Interface):

    def getTermByToken(token):
        """Checks whether the term exists in the current instance
        of the vocabulary. This allows new terms that have been added
        through addTermToInstance to pass validation.
        """


class KeywordWidgetAddableSourceWrapper(object):
    """Wrapper class used to allow adding new terms in async mode
    to a source vocabulary
    """

    def __init__(self, source):
        # Adding an interface to source is not ideal, as this means that
        # wrapping actually modifies source. This is not a problem though
        # as the wrapper is called in the binder, when the vocabulary is
        # instantiated.
        alsoProvides(source, IKeywordWidgetAddableSource)
        self._source = source
        self.instance_vocabulary = SimpleVocabulary([])

    def getTermByToken(self, token):
        """Checks whether the term exists in the current instance_vocabulary.
        This allows new terms that have been added in this request to pass
        validation.
        """
        try:
            return self._source.getTermByToken(token)
        except LookupError:
            return self.instance_vocabulary.getTermByToken(token)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._source, attr)


@implementer(IQuerySource)
class KeywordSearchableSource(object):
    """This example of a IQuerySource is taken from the
    plone.formwidget.autocomplete
    """

    def __init__(self, context):
        self.context = context
        catalog = getToolByName(context, 'portal_catalog')
        self.keywords = catalog.uniqueValuesFor('Subject')
        self.vocab = SimpleVocabulary.fromItems(
            [(as_keyword_token(x), x) for x in self.keywords])

    def __contains__(self, term):
        return self.vocab.__contains__(term)

    def __iter__(self):
        return self.vocab.__iter__()

    def __len__(self):
        return self.vocab.__len__()

    def getTerm(self, value):
        return self.vocab.getTerm(value)

    def getTermByToken(self, value):
        return self.vocab.getTermByToken(value)

    def search(self, query_string):
        q = query_string.lower()
        return [self.getTerm(kw) for kw in self.keywords if q in kw.lower()]


@implementer(IContextSourceBinder)
class KeywordSearchableSourceBinder(object):

    def __call__(self, context):
        return KeywordSearchableSource(context)


@implementer(IContextSourceBinder)
class KeywordSearchableAndAddableSourceBinder(object):

    def __call__(self, context):
        return KeywordWidgetAddableSourceWrapper(KeywordSearchableSource(context))

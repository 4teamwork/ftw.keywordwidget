from ftw.builder import Builder
from ftw.builder import create
from ftw.keywordwidget.tests import FunctionalTestCase
from ftw.keywordwidget.vocabularies import UnicodeKeywordsVocabulary
import transaction


class TestKeywordWidget(FunctionalTestCase):

    def setUp(self):
        super(TestKeywordWidget, self).setUp()
        self.grant('Manager')
        self.setup_fti()
        transaction.commit()

    def test_unicode_keyword_vocab_with_existing_index(self):
        create(Builder('sample content')
               .titled(u'A content')
               .having(subjects=(u'Bar', u'Baz')))

        vocab = UnicodeKeywordsVocabulary(index_name='Subject')(self.portal)
        self.assertItemsEqual([u'Bar', u'Baz'], vocab.by_value.keys())

    def test_unicode_keyword_vocab_with_NOT_existing_index(self):
        create(Builder('sample content')
               .titled(u'A content')
               .having(subjects=('Bar', 'Baz')))

        vocab = UnicodeKeywordsVocabulary(index_name='dummy')(self.portal)
        self.assertFalse(vocab.by_value.keys(), 'Expect an empty vocab')

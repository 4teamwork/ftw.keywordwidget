from ftw.builder import Builder
from ftw.builder import create
from ftw.keywordwidget.tests import FunctionalTestCase
from ftw.testbrowser import browsing
import transaction


class TestKeywordWidget(FunctionalTestCase):

    def setUp(self):
        super(TestKeywordWidget, self).setUp()
        self.grant('Manager')
        additional_behaviors = [
            'ftw.keywordwidget.behavior.IKeywordUseCases',
        ]
        self.setup_fti(additional_behaviors=additional_behaviors)
        transaction.commit()

    @browsing
    def test_choose_from_regular_list_with_choice_widget(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')
        types = browser.find_field_by_text(u'Types')

        self.assertTrue(types)
        # No add new terms field
        self.assertFalse(browser.css('#' + types.attrib['id'] + '_new'))

        # Some Possible options
        self.assertIn('SampleContent',
                      types.options_labels)
        self.assertIn('File',
                      types.options_labels)
        self.assertIn('Link',
                      types.options_labels)

        browser.fill({'Types': ('File', 'SampleContent')}).submit()
        browser.login().visit(content, view='edit')
        types = browser.find_field_by_text(u'Types')
        self.assertEquals(('File', 'SampleContent'), tuple(types.value))

    @browsing
    def test_choose_from_regular_choice_widget(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')
        types = browser.find_field_by_text(u'Single type')

        self.assertTrue(types)
        # No add new terms field
        self.assertFalse(browser.css('#' + types.attrib['id'] + '_new'))

        # Some Possible options
        self.assertIn('SampleContent',
                      types.options_labels)
        self.assertIn('File',
                      types.options_labels)
        self.assertIn('Link',
                      types.options_labels)

        browser.fill({'Single type': 'SampleContent'}).submit()
        browser.login().visit(content, view='edit')
        types = browser.find_field_by_text(u'Single type')
        self.assertEquals('SampleContent', types.value)

    @browsing
    def test_choose_from_tuple_with_choice_widget(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')
        types = browser.find_field_by_text(u'Types3')

        self.assertTrue(types)
        # No add new terms field
        self.assertFalse(browser.css('#' + types.attrib['id'] + '_new'))

        # Some Possible options
        self.assertIn('SampleContent',
                      types.options_labels)
        self.assertIn('File',
                      types.options_labels)
        self.assertIn('Link',
                      types.options_labels)

        browser.fill({'Types3': ('File', 'SampleContent')}).submit()
        browser.login().visit(content, view='edit')
        types = browser.find_field_by_text(u'Types3')
        self.assertEquals(('File', 'SampleContent'), tuple(types.value))

    @browsing
    def test_adding_terms_with_unicode_values_and_vocab_with_unicode_values(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')

        tags = browser.find_field_by_text(u'UnicodeTags')
        form = browser.find_form_by_field('UnicodeTags')
        new = browser.css('#' + tags.attrib['id'] + '_new').first
        new.text = u'NewItem1\nNew Item 2\nN\xf6i 3'
        form.submit()

        browser.visit(content, view='edit')
        tags = browser.find_field_by_text(u'UnicodeTags')
        self.assertTupleEqual(('New Item 2', 'NewItem1', 'N=C3=B6i 3'),
                              tuple(tags.value))

from ftw.builder import Builder
from ftw.builder import create
from ftw.keywordwidget.tests import FunctionalTestCase
from ftw.keywordwidget.widget import as_keyword_token
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from zope import schema
import json
import transaction


class TestKeywordWidgetWithRequiredFields(FunctionalTestCase):

    def setUp(self):
        super(TestKeywordWidgetWithRequiredFields, self).setUp()
        self.grant('Manager')
        additional_behaviors = [
            'ftw.keywordwidget.behavior.IKeywordCategorization',
            'ftw.keywordwidget.tests.behavior.IHaveARequiredTextField',
        ]
        self.setup_fti(additional_behaviors=additional_behaviors)

    @browsing
    def test_validation_errors_preserve_user_input(self, browser):
        browser.login().open(view='++add++SampleContent')
        browser.fill(
            {'form.widgets.IKeywordCategorization.subjects_new': 'foo'}
        ).submit()

        self.assertEqual(['There were some errors.'], error_messages())

        new_field = browser.find(
            'form.widgets.IKeywordCategorization.subjects_new')
        self.assertEqual('foo', new_field.value)

        tags = browser.find_field_by_text(u'Tags')
        self.assertEqual(['foo'], tags.options_labels)
        self.assertEqual(['foo'], list(tags.node.value),
                         'expected "foo" to be selected in the widget')

    @browsing
    def test_no_duplicates_after_submitting_after_a_validation_error(self, browser):
        browser.login().open(view='++add++SampleContent')

        browser.fill({
            'form.widgets.IKeywordCategorization.subjects_new': u'N\xe4h'}
        ).submit()
        self.assertEqual(['There were some errors.'], error_messages())

        # the second request will already contain the newly added selected
        # value from the first request (i.e. it's token).
        browser.fill({
            'form.widgets.IKeywordCategorization.subjects': as_keyword_token(
                u'N\xe4h'),
            'form.widgets.IKeywordCategorization.subjects_new': u'N\xe4h',
            'Title': 'jajaja...'}).submit()
        self.assertEqual(['Item created'], info_messages())

        self.assertEqual(['N\xc3\xa4h'], browser.context.subject)


class TestKeywordWidget(FunctionalTestCase):

    def setUp(self):
        super(TestKeywordWidget, self).setUp()
        self.grant('Manager')
        self.setup_fti()

        # Create a content with some keywords
        self.sample = create(Builder('sample content')
                             .titled(u'Dummy content for keywords')
                             .having(subjects=('F\xc3\xb6\xc3\xb6',
                                               'Bar', 'Baz')))

    @browsing
    def test_widget_render_input(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')

        tags = browser.find_field_by_text(u'Tags')
        self.assertTrue(tags)

        # Possible options
        self.assertListEqual(
            ['Bar', 'Baz', u'F\xf6\xf6'],
            tags.options_labels)

        # New entries field id derives from origin field id.
        new = browser.css('#' + tags.attrib['id'] + '_new')
        self.assertTrue(new)

    @browsing
    def test_select_and_save_from_given_entries(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')

        form = browser.find_form_by_field('Tags')
        form.fill({'Tags': ('Bar', 'F=C3=B6=C3=B6')}).submit()

        browser.visit(content, view='edit')
        tags = browser.find_field_by_text(u'Tags')
        self.assertEquals(('Bar', 'F=C3=B6=C3=B6'), tuple(tags.value))

    @browsing
    def test_add_new_tokens_to_field(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')

        tags = browser.find_field_by_text(u'Tags')
        form = browser.find_form_by_field('Tags')
        new = browser.css('#' + tags.attrib['id'] + '_new').first
        new.text = u'NewItem1\nNew Item 2\nN\xf6i 3'
        form.submit()

        browser.visit(content, view='edit')
        tags = browser.find_field_by_text(u'Tags')
        self.assertTupleEqual(('New Item 2', 'NewItem1', 'N=C3=B6i 3'),
                              tuple(tags.value))

    @browsing
    def test_add_new_terms_is_only_available_to_certain_roles(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        content.manage_permission('ftw.keywordwidget: Add new term',
                                  roles=[],
                                  acquire=0)
        transaction.commit()

        browser.login().visit(content, view='edit')
        tags = browser.find_field_by_text(u'Tags')
        self.assertFalse(len(browser.css('#' + tags.attrib['id'] + '_new')),
                         'Add new term field should NOT be there')

        content.manage_permission('ftw.keywordwidget: Add new term',
                                  roles=['Manager'],
                                  acquire=0)
        transaction.commit()

        browser.visit(content, view='edit')
        tags = browser.find_field_by_text(u'Tags')
        self.assertTrue(browser.css('#' + tags.attrib['id'] + '_new'),
                        'Add new term field should BE there')

    @browsing
    def test_default_select2_config_on_widget(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')
        tags = browser.find_field_by_text(u'Tags')

        select2_config = json.loads(tags.attrib['data-select2config'])
        self.assertListEqual(
            [u'i18n', u'width', u'allowClear', u'tokenSeparators', u'tags'],
            select2_config.keys())

    @browsing
    def test_add_twice_the_same_term_in_fact_adds_only_one(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')

        tags = browser.find_field_by_text(u'Tags')
        form = browser.find_form_by_field('Tags')
        new = browser.css('#' + tags.attrib['id'] + '_new').first
        new.text = u'New\nNew'
        form.submit()

        browser.visit(content, view='edit')
        tags = browser.find_field_by_text(u'Tags')
        self.assertTupleEqual(('New', ),
                              tuple(tags.value))

    @browsing
    def test_add_new_term_to_a_give_set_of_tags(self, browser):
        content = create(Builder('sample content')
                         .titled(u'A content')
                         .having(subjects=('Bar', 'Baz')))
        browser.login().visit(content, view='edit')

        tags = browser.find_field_by_text(u'Tags')
        form = browser.find_form_by_field('Tags')
        new = browser.css('#' + tags.attrib['id'] + '_new').first
        new.text = u'New'
        form.submit()

        browser.visit(content, view='edit')
        tags = browser.find_field_by_text(u'Tags')
        self.assertTupleEqual(('Bar', 'Baz', 'New'),
                              tuple(tags.value))

    @browsing
    def test_add_new_value_which_is_already_in_the_source(self, browser):
        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')

        tags = browser.find_field_by_text(u'Tags')
        form = browser.find_form_by_field('Tags')
        new = browser.css('#' + tags.attrib['id'] + '_new').first
        new.text = u'Bar'
        form.submit()

        browser.visit(content, view='edit')
        tags = browser.find_field_by_text(u'Tags')
        self.assertTupleEqual(('Bar', ),
                              tuple(tags.value))

    @browsing
    def test_add_new_term_to_empty_vocabulary(self, browser):
        self.portal.manage_delObjects(ids=[self.sample.getId()])
        transaction.commit()

        content = create(Builder('sample content').titled(u'A content'))
        browser.login().visit(content, view='edit')

        tags = browser.find_field_by_text(u'Tags')
        form = browser.find_form_by_field('Tags')
        new = browser.css('#' + tags.attrib['id'] + '_new').first
        new.text = u'NewItem1\nNew Item 2\nN\xf6i 3'
        form.submit()

        browser.visit(content, view='edit')
        tags = browser.find_field_by_text(u'Tags')
        self.assertTupleEqual(('New Item 2', 'NewItem1', 'N=C3=B6i 3'),
                              tuple(tags.value))

    def test_add_only_one_term_will_not_raise_an_error_after_cleanup_request(self):
        """The widget will not be used trough the browsertest. So we have to do
        it manually with a unittest.
        """
        field = schema.List(title=u"Subjects")
        widget = KeywordFieldWidget(field, self.request)

        widget.name = "Subjects"
        self.request['Subjects_new'] = u"Foo Bar"
        self.request['Subjects'] = u"Foo Bar"

        widget.cleanup_request()

        self.assertEqual([], self.request['Subjects'])
        self.assertEqual('Foo Bar', self.request['Subjects_new'])

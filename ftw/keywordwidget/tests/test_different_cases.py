from ftw.builder import Builder
from ftw.builder import create
from ftw.keywordwidget.search import SearchSource
from ftw.keywordwidget.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from zope.interface import implementer
from zope.schema import Choice
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import json
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


class TestAsyncOption(FunctionalTestCase):
    def setUp(self):
        super(TestAsyncOption, self).setUp()
        self.grant('Manager')
        additional_behaviors = [
            'ftw.keywordwidget.behavior.IKeywordCategorization',
            'ftw.keywordwidget.behavior.IKeywordUseCases',
        ]
        self.setup_fti(additional_behaviors=additional_behaviors)
        transaction.commit()

    @browsing
    def test_async_render_only_selected_items(self, browser):
        create(Builder('sample content')
               .titled(u'A content')
               .having(subjects=('foo', 'bar', 'baz', 'abc',
                                 'zzzzzz', 'lorem', 'ipsum')))

        content = create(Builder('sample content')
                         .titled(u'Use async lib')
                         .having(async=('abc', 'zzzzzz', 'lorem')))

        browser.login().visit(content, view='edit')
        field = browser.find_field_by_text('async')
        self.assertListEqual(list(field.value), field.options_values)

    @browsing
    def test_async_option_is_selectable_but_not_rendered(self, browser):
        create(Builder('sample content')
               .titled(u'A content')
               .having(subjects=('foo', 'bar', 'baz', 'abc',
                                 'zzzzzz', 'lorem', 'ipsum')))

        content = create(Builder('sample content')
                         .titled(u'Use async lib'))

        browser.login().visit(content, view='edit')
        field = browser.find_field_by_text('async')
        self.assertFalse(tuple(field.value), 'Expect no selectable options')

        form = browser.find_form_by_field('async')
        form.find_widget('async').fill(['foo', 'bar'])
        form.submit()

        self.assertSequenceEqual(['foo', 'bar'], content.async)

    @browsing
    def test_async_option_terms_not_in_source_are_ignored(self, browser):
        create(Builder('sample content')
               .titled(u'A content')
               .having(subjects=('foo', 'bar', 'baz', 'abc',
                                 'zzzzzz', 'lorem', 'ipsum')))

        content = create(Builder('sample content')
                         .titled(u'Use async lib'))

        browser.login().visit(content, view='edit')

        form = browser.find_form_by_field('async')
        form.find_widget('async').fill(['New', 'New2'])
        form.submit()

        self.assertFalse(content.async, 'Expect nothing in field async')

    def test_async_option_only_works_with_IQuerySource(self):

        @implementer(IContextSourceBinder)
        class DummySource(object):
            def __call__(self, context):
                return SimpleVocabulary([])

        content = create(Builder('sample content')
                         .titled(u'A content')
                         .having(subjects=('foo', 'bar', 'baz', 'abc')))

        edit_form = content.restrictedTraverse('@@edit').form_instance
        edit_form.update()
        new_field = Choice(title=u'dummy', source=DummySource())
        edit_form.fields['IKeywordUseCases.async'].field = new_field

        with self.assertRaises(TypeError):
            edit_form.update()

    def test_search_endpoint(self):
        content = create(Builder('sample content')
                         .titled(u'A content')
                         .having(subjects=('foo', 'bar', 'baz', 'abc',
                                           'zzzzzz', 'lorem', 'ipsum')))

        self.portal.REQUEST.set('q', 'ba')
        result = json.loads(self._get_search_view(content))

        self.assertTrue(isinstance(result, dict))
        self.assertIn('total_count', result)
        self.assertEquals(result['total_count'], 2)

        self.assertIn('page', result)
        self.assertEquals(result['page'], 1)

        self.assertIn('results', result)
        self.assertEquals([{'_resultId': u'bar',
                            'id': u'bar',
                            'text': u'bar'},
                           {'_resultId': u'baz',
                            'id': u'baz',
                            'text': u'baz'}, ],
                          result['results'])

        self.portal.REQUEST.set('q', 'dummy')
        result = json.loads(self._get_search_view(content))
        self.assertEquals([], result['results'])

    def test_search_endpoint_batch_result(self):
        content = create(Builder('sample content')
                         .titled(u'A content')
                         .having(subjects=map(str, range(1, 100))))

        self.portal.REQUEST.set('q', '1')
        self.portal.REQUEST.set('pagesize', '5')
        self.portal.REQUEST.set('page', '1')
        result = json.loads(self._get_search_view(content))

        self.assertEquals(5, len(result['results']))
        self.assertEquals(19, result['total_count'])
        self.assertEquals([u'1', u'10', u'11', u'12', u'13'],
                          self._get_values(result['results']))

        self.portal.REQUEST.set('q', '1')
        self.portal.REQUEST.set('pagesize', '5')
        self.portal.REQUEST.set('page', '3')
        result = json.loads(self._get_search_view(content))

        self.assertEquals(5, len(result['results']))
        self.assertEquals(19, result['total_count'])
        self.assertEquals([u'19', u'21', u'31', u'41', u'51'],
                          self._get_values(result['results']))

    def _get_values(self, items):
        return map(lambda item: item['id'], items)

    def _get_search_view(self, context):
        form = context.unrestrictedTraverse('@@edit').form_instance
        form.update()
        widget = form.widgets['IKeywordUseCases.async']
        return SearchSource(widget, widget.request)()

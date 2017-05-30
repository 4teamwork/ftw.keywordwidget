from binascii import b2a_qp
from ftw.keywordwidget import _
from ftw.keywordwidget.field import ChoicePlus
from ftw.keywordwidget.utils import safe_utf8
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.browser.select import SelectWidget
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import ISelectWidget
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import FieldWidget
from z3c.formwidget.query.interfaces import IQuerySource
from zope import schema
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import json


def is_list_type_field(field):
    if isinstance(field, schema.List):
        return True
    elif isinstance(field, schema.Tuple):
        return True
    else:
        return False


def as_keyword_token(value):
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    return b2a_qp(value)


class IKeywordWidget(ISelectWidget):
    """Marker interface for the Keywordwidget"""


@implementer(IKeywordWidget)
class KeywordWidget(SelectWidget):

    klass = u'keyword-widget'

    noValueToken = u''

    noValueMessage = _('no value')
    promptMessage = _('select some values ...')
    promptNoresultFound = _('No result found')
    label_new = _(u'New')
    label_searching = _(u'Searching...')
    label_loading_more = _('Load more results...')
    label_tooshort_prefix = _('Please enter ')
    label_tooshort_postfix = _(' or more characters')

    multiple = 'multiple'
    size = 10

    # KeywordWidget specific
    js_config = None
    config_json = ''
    ajax_options_json = ''
    choice_field = None
    add_permission = None
    new_terms_as_unicode = None
    async = False

    display_template = ViewPageTemplateFile('templates/keyword_display.pt')
    input_template = ViewPageTemplateFile('templates/keyword_input.pt')
    hidden_template = ViewPageTemplateFile('templates/keyword_hidden.pt')

    def __init__(self, request, js_config=None, add_permission=None,
                 new_terms_as_unicode=False, async=False):
        self.request = request
        self.js_config = js_config
        self.new_terms_as_unicode = new_terms_as_unicode
        self.async = async

        self.add_permission = (add_permission or
                               'ftw.keywordwidget: Add new term')

    def render(self):
        if self.mode == INPUT_MODE:
            return self.input_template(self)
        elif self.mode == DISPLAY_MODE:
            return self.display_template(self)
        elif self.mode == HIDDEN_MODE:
            return self.hidden_template(self)
        raise NotImplementedError(
            'Mode: "{0}" not supported'.format(self.mode))

    def get_new_values_from_request(self):
        """Get the values from the request and splits addition values by
        newlines,
        """
        new_values = set()
        new = self.request.get('{0}_new'.format(self.name), '').split('\n')
        for value in new:
            cleanedup_value = value.strip().strip('\r').strip('\n')
            if cleanedup_value:
                new_values.add(cleanedup_value)
        return list(new_values)

    def cleanup_request(self):
        """
        If the tags feature is enabled the new term is also in a
        "not normalized" variation in the request. We need to remove it, thus
        the super call of the sequence widget will still work.
        Otherwise it does not recognize all terms in the request as valid term.
        """
        values = self.request.get(self.name, [])
        if not isinstance(values, list):
            # This case happens if the user tries to add only one new keyword.
            # We will receive a string instead a list.
            values = [values]

        if not values:
            return

        for new_value in self.get_new_values_from_request():
            if new_value in values:
                values.remove(new_value)
        self.request.set(self.name, values)

    def _validate_source_for_async(self):
        source = self.choice_field.source
        if IContextSourceBinder.providedBy(source):
            source = source(self.context)
            if IQuerySource.providedBy(source):
                return
        raise(TypeError('A IContextSourceBinder with IQuerySource is needed'))

    def update(self):
        self.get_choice_field()

        if self.async:
            self._validate_source_for_async()

        super(KeywordWidget, self).update()

        self.update_multivalued_property()
        self.update_js_config()

        if isinstance(self.choice_field, ChoicePlus):
            has_permission = api.user.has_permission(
                self.add_permission,
                obj=self.context)
            self.field.value_type.allow_new = has_permission

    def update_js_config(self):
        # Sane default config
        default_config = {
            'i18n': {
                'label_placeholder': translate(self.promptMessage,
                                               context=self.request),
                'label_no_result': translate(self.promptNoresultFound,
                                             context=self.request),
                'label_new': translate(self.label_new,
                                       context=self.request),
                'label_searching': translate(self.label_searching,
                                             context=self.request),
                'label_loading_more': translate(self.label_loading_more,
                                                context=self.request),
                'label_tooshort_prefix': translate(self.label_tooshort_prefix,
                                                   context=self.request),
                'label_tooshort_postfix': translate(self.label_tooshort_postfix,
                                                    context=self.request),
            },
            'width': '300px',
            'allowClear': not self.field.required and not self.multiple,
        }

        if self.show_add_term_field():
            default_config['tags'] = True
            default_config['tokenSeparators'] = [',']

        if self.async:
            default_config['minimumInputLength'] = 3

        if self.js_config:
            default_config.update(self.js_config)

        if self.async:
            self.ajax_options_json = json.dumps(
                {'url': '{}/++widget++{}/search'.format(self.request.getURL(),
                                                        self.name),
                 'dataType': 'json',
                 'delay': 250}
            )

        self.config_json = json.dumps(default_config)

    def update_multivalued_property(self):
        if not is_list_type_field(self.field):
            self.multiple = None
            self.size = 1
            self.promptMessage = _('select a value ...')

    def get_choice_field(self):
        is_list = is_list_type_field(self.field)
        is_choice = isinstance(self.field, schema.Choice)

        if is_list and isinstance(self.field.value_type, schema.Choice):
            self.choice_field = self.field.value_type
        elif is_choice:
            self.choice_field = self.field
        else:
            raise ValueError('The field or the value type of the field '
                             'needs to be a Choice field.')

    def show_add_term_field(self):
        if isinstance(self.choice_field, ChoicePlus):
            return self.field.value_type.allow_new
        else:
            return False

    def extract(self, default=NOVALUE):
        """See z3c.form.interfaces.IWidget.
        """
        self.cleanup_request()

        values = super(KeywordWidget, self).extract(default=default)
        if values is NOVALUE or not self.show_add_term_field():
            return values

        # Adding new keywords, which are not in the vocab/source
        if (self.name + '_new' not in self.request and
                self.name + '-empty-marker' in self.request):
            return []

        tokens = set(values)
        for new_value in self.get_new_values_from_request():
            tokens.add(as_keyword_token(new_value))

        return list(tokens) if tokens else default

    def updateTerms(self):
        super(KeywordWidget, self).updateTerms()

        if self.async:
            # It's not possible to add new terms in async mode
            return self.terms

        simple_vocbaulary = self.terms.terms
        terms = self.terms.terms._terms

        for new_value in self.get_new_values_from_request():
            if new_value not in simple_vocbaulary.by_value:
                # Vocabulary term tokens *must* be 7 bit values, titles *must*
                # be unicode.
                # Value needs to be a utf-8 str, only hell knows why.
                # IMHO this should depend on the source. We're gonna have
                # trouble with this in the future.
                # ...
                # Well as I said before...
                new_token = as_keyword_token(new_value)
                if self.new_terms_as_unicode:
                    new_value = safe_unicode(new_value)
                else:
                    new_value = safe_utf8(new_value)

                terms.append(
                    SimpleTerm(new_value, new_token, safe_unicode(new_value)))

        self.terms.terms = SimpleVocabulary(terms)
        return self.terms

    def items(self):
        """This is a copy of the z3c.form.browser.select.SelectWidget
        There's one difference, if the widget is in async mode.
        The widget actually only renders the select values and not all
        possible values.
        """

        if self.terms is None:  # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
            })

        ignored = set(self.value)

        def addItem(idx, term, prefix=''):
            selected = self.isSelected(term)
            if selected and term.token in ignored:
                ignored.remove(term.token)
            id = '%s-%s%i' % (self.id, prefix, idx)
            content = term.token
            if ITitledTokenizedTerm.providedBy(term):
                content = translate(
                    term.title, context=self.request, default=term.title)
            items.append(
                {'id': id, 'value': term.token, 'content': content,
                 'selected': selected})

        if self.async:
            terms = [self.terms.getTermByToken(v) for v in self.value]
        else:
            terms = self.terms

        for idx, term in enumerate(terms):
            addItem(idx, term)

        if ignored:
            # some values are not displayed, probably they went away from the
            # vocabulary
            for idx, token in enumerate(sorted(ignored)):
                try:
                    term = self.terms.getTermByToken(token)
                except LookupError:
                    # just in case the term really went away
                    continue

                addItem(idx, term, prefix='missing-')
        return items


@implementer(IFieldWidget)
def KeywordFieldWidget(field, request):
    return FieldWidget(field, KeywordWidget(request))

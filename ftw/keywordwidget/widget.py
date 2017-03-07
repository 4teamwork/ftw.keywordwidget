from binascii import b2a_qp
from ftw.keywordwidget import _
from ftw.keywordwidget.field import ChoicePlus
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.browser.select import SelectWidget
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import FieldWidget
from zope import schema
from zope.i18n import translate
from zope.interface import implementer
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


class KeywordWidget(SelectWidget):

    klass = u'keyword-widget'

    noValueToken = u''

    noValueMessage = _('no value')
    promptMessage = _('select some values ...')
    promptNoresultFound = _('No result found')
    labelNew = _('New')
    multiple = 'multiple'
    size = 10

    # KeywordWidget specific
    js_config = None
    choice_field = None
    add_permission = None

    display_template = ViewPageTemplateFile('templates/keyword_display.pt')
    input_template = ViewPageTemplateFile('templates/keyword_input.pt')
    hidden_template = ViewPageTemplateFile('templates/keyword_hidden.pt')
    js_template = ViewPageTemplateFile('templates/keyword.js.pt')

    def __init__(self, request, js_config=None, add_permission=None):
        self.request = request
        self.js_config = js_config

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

    def update(self):
        self.get_choice_field()

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
                'label_new': translate(self.labelNew,
                                       context=self.request)
            },
            'width': '300px',
            'allowClear': not self.field.required and not self.multiple,
        }

        if self.show_add_term_field():
            default_config['tags'] = True
            default_config['tokenSeparators'] = [',']

        if self.js_config:
            default_config.update(self.js_config)

        self.js_config = json.dumps(default_config)

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

        if not self.show_add_term_field():
            return values

        else:
            # Adding new keywords, which are not in the vocab/source
            if (self.name + '_new' not in self.request and
                    self.name + '-empty-marker' in self.request):
                return []

            new_values = self.get_new_values_from_request()

            if values is default:
                values = []
            else:
                # We need to remove the new added keywords from extracted
                # values, since they need to be processed separately.
                # This happens if the select2 plugin has the tag option
                # activated
                values = [val for val in values if val not in new_values]

            for new_value in new_values:
                # The new values needs to fit the token value in the
                # vocabulary
                values.append(as_keyword_token(new_value))

            return values and list(set(values)) or default

    def updateTerms(self):
        super(KeywordWidget, self).updateTerms()
        simple_vocbaulary = self.terms.terms
        terms = self.terms.terms._terms

        for new_value in self.get_new_values_from_request():
            if new_value not in simple_vocbaulary.by_value:
                # Vocabulary term tokens *must* be 7 bit values, titles *must*
                # be unicode.
                # Value needs to be a utf-8 str, only hell knows why.
                # IMHO this should depend on the source. We're gonna have
                # trouble with this in the future.
                new_token = as_keyword_token(new_value)
                if isinstance(new_value, unicode):
                    new_value = new_value.encode('utf-8')
                terms.append(
                    SimpleTerm(new_value, new_token, safe_unicode(new_value)))

        self.terms.terms = SimpleVocabulary(terms)
        return self.terms

    def keyword_js(self):
        return self.js_template(widgetid=self.id)


@implementer(IFieldWidget)
def KeywordFieldWidget(field, request):
    return FieldWidget(field, KeywordWidget(request))

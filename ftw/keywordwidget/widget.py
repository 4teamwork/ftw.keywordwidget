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
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class KeywordWidget(SelectWidget):

    klass = u'keyword-widget'

    noValueToken = u''

    noValueMessage = _('no value')
    promptMessage = _('select a value ...')
    multiple = 'multiple'
    size = 10

    js_config = {}

    display_template = ViewPageTemplateFile('templates/keyword_display.pt')
    input_template = ViewPageTemplateFile('templates/keyword_input.pt')
    hidden_template = ViewPageTemplateFile('templates/keyword_hidden.pt')

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
        new_values = []
        new = self.request.get('{0}_new'.format(self.name), '').split('\n')
        for value in new:
            cleanedup_value = value.strip().strip('\r').strip('\n')
            if cleanedup_value:
                new_values.append(cleanedup_value)
        return new_values

    def update(self):
        super(KeywordWidget, self).update()

        if isinstance(self.field.value_type, ChoicePlus):
            has_permission = api.user.has_permission(
                'ftw.keywordwidget: Add new term',
                obj=self.context)
            self.field.value_type.allow_new = has_permission

    def show_add_term_field(self):
        if isinstance(self.field.value_type, ChoicePlus):
            return self.field.value_type.allow_new
        else:
            return False

    def extract(self, default=NOVALUE):
        """See z3c.form.interfaces.IWidget.
        """
        values = super(KeywordWidget, self).extract(default=default)

        # Adding new keywords, which are not in the vocab/source
        if (self.name + '_new' not in self.request and
                self.name + '-empty-marker' in self.request):
            return []

        new_values = self.get_new_values_from_request()

        for new_value in new_values:
            if new_value not in values:

                # The new values needs to fit the token value in the vocabulary
                if isinstance(new_value, unicode):
                    new_value = new_value.encode('utf-8')
                    new_value = b2a_qp(new_value)

                values.append(new_value)

        return values and values or default

    def updateTerms(self):
        super(KeywordWidget, self).updateTerms()
        simple_vocbaulary = self.terms.terms
        terms = self.terms.terms._terms

        for new_value in self.get_new_values_from_request():
            if new_value not in simple_vocbaulary.by_value:

                # Vocabulary term tokens *must* be 7 bit values, titles *must*
                # be unicode.
                # Value needs to be a utf-8 str, hell I don't know why.
                # IMHO this should depend on the source. We're gonna have
                # trouble with this in the future.
                new_token = new_value
                if isinstance(new_value, unicode):
                    new_value = new_token = new_value.encode('utf-8')
                new_token = b2a_qp(new_token)
                terms.append(
                    SimpleTerm(new_value, new_token, safe_unicode(new_value)))

        self.terms.terms = SimpleVocabulary(terms)
        return self.terms


@implementer(IFieldWidget)
def KeywordFieldWidget(field, request):
    return FieldWidget(field, KeywordWidget(request))

from binascii import b2a_qp
from ftw.keywordwidget import _
from ftw.keywordwidget.field import ChoicePlus
from plone import api
from Products.CMFPlone.utils import safe_unicode
from z3c.form.browser.select import SelectWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ISelectWidget
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IKeywordWidget(ISelectWidget):
    """Keyword widget interface"""


class KeywordWidget(SelectWidget):
    implements(ICollection, IKeywordWidget)

    klass = u'keyword-widget'

    noValueToken = u''

    noValueMessage = _('no value')
    promptMessage = _('select a value ...')
    size = u'10'

    multiple = u'multiple'

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

    def get_new_values_from_request(self):
        """Get the values from the request and splits addition values by
        newlines,
        """
        new_values = []
        new = self.request.get(
            '{0}_new'.format(self.name), '').split('\n')
        for value in new:
            cleanedup_value = value.strip().strip('\r').strip('\n')
            if cleanedup_value:
                new_values.append(cleanedup_value)
        return new_values

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


@adapter(IChoice, Interface, IFormLayer)
@implementer(IFieldWidget)
def KeywordFieldWidget(field, source, request=None):
    """IFieldWidget factory for SelectWidget."""
    # BBB: emulate our pre-2.0 signature (field, request)
    if request is None:
        real_request = source
    else:
        real_request = request
    return FieldWidget(field, KeywordWidget(real_request))

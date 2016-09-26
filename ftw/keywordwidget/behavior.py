from ftw.keywordwidget.field import ChoicePlus
from ftw.keywordwidget.widget import KeywordFieldWidget
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.form.interfaces import IEditForm, IAddForm
from zope import schema
from zope.interface import alsoProvides


class IKeywordCategorization(model.Schema):

    model.fieldset(
        'categorization',
        label=_PMF(u'label_schema_categorization', default=u'Categorization'),
        fields=['subjects', ],
    )

    directives.widget('subjects', KeywordFieldWidget)
    subjects = schema.List(
        title=_PMF(u'label_tags', default=u'Tags'),
        description=_PMF(
            u'help_tags',
            default=u'Tags are commonly used for ad-hoc organization of ' +
                    u'content.'
        ),
        value_type=ChoicePlus(
            title=u"Multiple",
            vocabulary='plone.app.vocabularies.Keywords', ),
        required=False,
        missing_value=(),
    )

    # Show field only on edit/add forms.
    directives.omitted('subjects', )
    directives.no_omit(IEditForm, 'subjects', )
    directives.no_omit(IAddForm, 'subjects', )

alsoProvides(IKeywordCategorization, IFormFieldProvider)


class Categorization(MetadataBase):

    def _get_subjects(self):
        return self.context.subject

    def _set_subjects(self, value):
        self.context.subject = value
    subjects = property(_get_subjects, _set_subjects)

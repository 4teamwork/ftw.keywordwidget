from ftw.keywordwidget.vocabularies import KeywordSearchableSourceBinder
from ftw.keywordwidget.widget import KeywordFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides


class IHaveARequiredTextField(model.Schema):

    fillme = schema.Text(
        title=u'Fill me',
        required=True,
    )


alsoProvides(IHaveARequiredTextField, IFormFieldProvider)


class IOptionalChoiceField(model.Schema):

    directives.widget('keyword', KeywordFieldWidget, async=True)
    keyword = schema.Choice(
        title=u'Colors',
        required=False,
        source=KeywordSearchableSourceBinder())


alsoProvides(IOptionalChoiceField, IFormFieldProvider)

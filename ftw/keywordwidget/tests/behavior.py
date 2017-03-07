from plone.supermodel import model
from zope import schema


class IHaveARequiredTextField(model.Schema):

    fillme = schema.Text(
        title=u'Fill me',
        required=True,
    )

from plone import api
from zope.interface import implementer
from zope.schema import Choice
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import IFromUnicode
from zope.schema.vocabulary import getVocabularyRegistry
from zope.schema.vocabulary import VocabularyRegistryError


@implementer(IChoice, IFromUnicode)
class ChoicePlus(Choice):
    """A choice field, which allows additional terms.
    Example: Allow new tags for catalog based vocabulary.
    """

    def _validate(self, value):
        # Pass all validations during initialization
        if self._init_field:
            return

        super(Choice, self)._validate(value)
        vocabulary = self.vocabulary
        if vocabulary is None:
            vr = getVocabularyRegistry()
            try:
                vocabulary = vr.get(None, self.vocabularyName)
            except VocabularyRegistryError:
                raise ValueError("Can't validate value without vocabulary")

        # The widget can control this attribute too
        if getattr(api.portal.getRequest(), 'allow_new', True):
            # Allow new values!
            return
        else:
            if value not in vocabulary:
                raise ConstraintNotSatisfied(value)

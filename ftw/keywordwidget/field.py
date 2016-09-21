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
    Example: Allow new tags for catalog based vocabulary"""

    allow_new = None

    def __init__(self, values=None, vocabulary=None, source=None, **kw):
        super(ChoicePlus, self).__init__(values, vocabulary, source, **kw)
        self.allow_new = True

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
        if self.allow_new:
            # Allow new values!
            return
        else:
            if value not in vocabulary:
                raise ConstraintNotSatisfied(value)

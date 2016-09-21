from ftw.keywordwidget.widget import IKeywordWidget
from z3c.form.converter import CollectionSequenceDataConverter
from zope.component import adapts
from zope.schema.interfaces import IField


class KeywordDataConverter(CollectionSequenceDataConverter):
    """Basic data converter for IKeyWordWidget."""
    adapts(IField, IKeywordWidget)

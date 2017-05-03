from ftw.builder import registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.keywordwidget.testing import FTW_FUNCTIONAL
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.content import Container
from plone.dexterity.fti import DexterityFTI
from plone.supermodel import model
from unittest2 import TestCase
from zope.interface import implements
from zope.interface import Interface
import ftw.keywordwidget.tests.widget
import transaction


class ISampleContentSchema(model.Schema):
    pass


class ISampleContententMarker(Interface):
    pass


class SampleContent(Container):
    implements(ISampleContententMarker)


class FunctionalTestCase(TestCase):
    layer = FTW_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()

    def setup_fti(self, additional_behaviors=None):
        types_tool = self.portal.portal_types

        default_behaviors = [
            'plone.app.dexterity.behaviors.metadata.IBasic',
            'plone.app.content.interfaces.INameFromTitle'
        ]

        if additional_behaviors is None:
            default_behaviors += [
                'ftw.keywordwidget.behavior.IKeywordCategorization',
            ]
        else:
            default_behaviors += additional_behaviors

        fti = DexterityFTI('SampleContent')
        fti.schema = 'ftw.keywordwidget.tests.ISampleContentSchema'
        fti.klass = 'ftw.keywordwidget.tests.SampleContent'
        fti.behaviors = tuple(default_behaviors)
        fti.default_view = 'view'
        types_tool._setObject('SampleContent', fti)

        transaction.commit()


# Builders
class SampleContentBuilder(DexterityBuilder):
    portal_type = 'SampleContent'

registry.builder_registry.register(
    'sample content', SampleContentBuilder)

from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.keywordwidget.behavior import IKeywordUseCases
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.indexer import indexer
from plone.testing import z2
from Products.CMFCore.interfaces import IContentish
from zope.component import provideAdapter
from zope.configuration import xmlconfig


def _setup_catalog_for_tests(portal):
    @indexer(IContentish)
    def unicode_keywords(obj):
        return IKeywordUseCases(obj).unicode_keywords

    provideAdapter(unicode_keywords)

    catalog = portal.portal_catalog
    catalog.addIndex('unicode_keywords', 'KeywordIndex')


class FtwLayer(PloneSandboxLayer):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.keywordwidget')

        import ftw.keywordwidget.tests
        xmlconfig.file('tests.zcml',
                       ftw.keywordwidget.tests,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.keywordwidget:default')
        _setup_catalog_for_tests(portal)


FTW_FIXTURE = FtwLayer()
FTW_FUNCTIONAL = FunctionalTesting(
    bases=(FTW_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.keywordwidget:functional")

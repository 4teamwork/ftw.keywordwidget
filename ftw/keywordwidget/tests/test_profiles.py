from Products.CMFCore.utils import getToolByName
from ftw.keywordwidget.tests import FunctionalTestCase
from ftw.testing import IS_PLONE_5
from plone import api


class TestDefaultProfile(FunctionalTestCase):

    def test_installed(self):
        portal_setup = getToolByName(self.portal, 'portal_setup')
        version = portal_setup.getLastVersionForProfile('ftw.keywordwidget:default')
        self.assertNotEqual(version, None)
        if IS_PLONE_5:
            resources = api.portal.get_registry_record('plone.bundles/ftw-keywordwidget-resources.jscompilation')
            self.assertTrue(bool(resources), "Profile not installed.")
        else:
            self.assertNotEqual(version, 'unknown')

# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.behavior.interfaces import IBehavior

from conference.program.behaviors.presenters import IPresenters

from conference.program.testing import INTEGRATION_TESTING


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    name = 'conference.program.behaviors.presenters.IPresenters'

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.ct = self.portal.portal_catalog
        self.portal.invokeFactory('conference.program', 'program')
        self.program = self.portal['program']
        self.program.invokeFactory('conference.track', 'track-1')
        self.track = self.program['track-1']

    def test_registration(self):
        registration = queryUtility(IBehavior, name=self.name)
        self.assertNotEquals(None, registration)

    def test_adapt_talk(self):
        self.program.invokeFactory('conference.talk', 'talk')
        talk = self.program['talk']
        presenters = IPresenters(talk)
        self.assertNotEquals(None, presenters)

    def test_adapt_training(self):
        self.program.invokeFactory('conference.training', 'training')
        training = self.program['training']
        presenters = IPresenters(training)
        self.assertNotEquals(None, presenters)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

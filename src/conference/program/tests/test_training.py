# -*- coding: utf-8 -*-
import unittest2 as unittest

from AccessControl import Unauthorized

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from plone.dexterity.interfaces import IDexterityFTI

from conference.program.content.training import ITraining

from conference.program.testing import INTEGRATION_TESTING


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('conference.program', 'program')
        self.program = self.portal['program']
        self.program.invokeFactory('conference.track', 'track-1')
        self.track = self.program['track-1']

    def test_adding_as_manager(self):
        self.program.invokeFactory('conference.training', 'training')
        training = self.program['training']
        self.assertTrue(ITraining.providedBy(training))

    def test_adding_in_a_track(self):
        self.track.invokeFactory('conference.training', 'training')
        training = self.track['training']
        self.assertTrue(ITraining.providedBy(training))

    def test_adding_outside_program(self):
        # Adding outside a conference.program will return a
        # Disallowed subobject type: conference.training
        self.assertRaises(ValueError,
                          self.portal.invokeFactory,
                          *('conference.training', 'training'))

    def test_adding_member_unauthorized(self):
        # Set user roles as Member
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        # This should only be allowed when program is on a
        # specific workflow state
        self.assertRaises(Unauthorized,
                          self.program.invokeFactory,
                          *('conference.training', 'training'))

    def test_adding_anonymous_unauthorized(self):
        logout()
        self.assertRaises(Unauthorized,
                          self.program.invokeFactory,
                          *('conference.training', 'training'))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='conference.training')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='conference.training')
        schema = fti.lookupSchema()
        self.assertEquals(ITraining, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='conference.training')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ITraining.providedBy(new_object))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

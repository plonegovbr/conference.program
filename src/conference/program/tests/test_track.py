# -*- coding: utf-8 -*-
import unittest2 as unittest

from AccessControl import Unauthorized

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from plone.dexterity.interfaces import IDexterityFTI

from conference.program.content.track import ITrack

from conference.program.testing import INTEGRATION_TESTING


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('conference.program', 'program')
        self.program = self.portal['program']

    def test_adding_as_manager(self):
        self.program.invokeFactory('conference.track', 'track-1')
        track = self.program['track-1']
        self.assertTrue(ITrack.providedBy(track))

    def test_adding_outside_program(self):
        # Adding outside a conference.program will return a
        # Disallowed subobject type: conference.track
        self.assertRaises(ValueError,
                          self.portal.invokeFactory,
                          *('conference.track', 'track-1'))

    def test_adding_member_unauthorized(self):
        # Set user roles as Member
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertRaises(Unauthorized,
                          self.program.invokeFactory,
                          *('conference.track', 'track-1'))

    def test_adding_anonymous_unauthorized(self):
        logout()
        self.assertRaises(Unauthorized,
                          self.program.invokeFactory,
                          *('conference.track', 'track-1'))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='conference.track')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='conference.track')
        schema = fti.lookupSchema()
        self.assertEquals(ITrack, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='conference.track')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ITrack.providedBy(new_object))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

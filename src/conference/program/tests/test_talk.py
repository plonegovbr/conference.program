# -*- coding: utf-8 -*-
import unittest2 as unittest

from AccessControl import Unauthorized

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from plone.dexterity.interfaces import IDexterityFTI

from conference.program.content.talk import ITalk

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
        self.program.invokeFactory('conference.talk', 'talk')
        talk = self.program['talk']
        self.assertTrue(ITalk.providedBy(talk))

    def test_adding_in_a_track(self):
        self.track.invokeFactory('conference.talk', 'talk')
        talk = self.track['talk']
        self.assertTrue(ITalk.providedBy(talk))

    def test_adding_outside_program(self):
        # Adding outside a conference.program will return a
        # Disallowed subobject type: conference.talk
        self.assertRaises(ValueError,
                          self.portal.invokeFactory,
                          *('conference.talk', 'talk'))

    def test_adding_member_unauthorized(self):
        # Set user roles as Member
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        # This should only be allowed when program is on a
        # specific workflow state
        self.assertRaises(Unauthorized,
                          self.program.invokeFactory,
                          *('conference.talk', 'talk'))

    def test_adding_anonymous_unauthorized(self):
        logout()
        self.assertRaises(Unauthorized,
                          self.program.invokeFactory,
                          *('conference.talk', 'talk'))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='conference.talk')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='conference.talk')
        schema = fti.lookupSchema()
        self.assertEquals(ITalk, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='conference.talk')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ITalk.providedBy(new_object))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

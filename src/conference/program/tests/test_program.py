# -*- coding: utf-8 -*-
import unittest2 as unittest

from DateTime import DateTime

from AccessControl import Unauthorized

from zope.component import createObject
from zope.component import queryUtility

from zope.interface import Invalid

from zope.schema.interfaces import IVocabularyFactory

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from plone.dexterity.interfaces import IDexterityFTI

from conference.program.content.program import IProgram

from conference.program.testing import INTEGRATION_TESTING


class MockProgram(object):
    start_date = None
    end_date = None


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.ct = self.portal.portal_catalog
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_adding(self):
        self.portal.invokeFactory('conference.program', 'program')
        program = self.portal['program']
        self.assertTrue(IProgram.providedBy(program))

    def test_adding_member_unauthorized(self):
        # Set user roles as Member
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertRaises(Unauthorized,
                          self.portal.invokeFactory,
                          *('conference.program', 'program'))

    def test_adding_anonymous_unauthorized(self):
        logout()
        self.assertRaises(Unauthorized,
                          self.portal.invokeFactory,
                          *('conference.program', 'program'))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='conference.program')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='conference.program')
        schema = fti.lookupSchema()
        self.assertEquals(IProgram, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='conference.program')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IProgram.providedBy(new_object))

    def test_talk_indexing(self):
        self.portal.invokeFactory('conference.program', 'program')
        program = self.portal['program']
        program.start_date = DateTime('2012/04/18')
        program.end_date = DateTime('2012/04/18')
        program.reindexObject()
        results = self.ct.searchResults(portal_type='conference.program',
                                        getId='program')
        brain = results[0]
        self.assertEquals(program.start_date, brain.start)
        self.assertEquals(program.end_date, brain.end)

    def test_valid_empty_dates(self):
        ''' Both empty dates are considered valid as those fields
            are not required
        '''
        data = MockProgram()
        try:
            IProgram.validateInvariants(data)
        except Invalid:
            self.fail()

    def test_valid_dates(self):
        ''' Same day, different days
        '''
        # Same Day
        data = MockProgram()
        data.start_date = DateTime('2012/04/18')
        data.end_date = DateTime('2012/04/18')
        try:
            IProgram.validateInvariants(data)
        except Invalid:
            self.fail()

        # Different day
        data = MockProgram()
        data.start_date = DateTime('2012/04/18')
        data.end_date = DateTime('2012/04/19')
        try:
            IProgram.validateInvariants(data)
        except Invalid:
            self.fail()

    def test_invalid_end_date(self):
        ''' Both empty dates are considered valid as those fields
            are not required
        '''
        data = MockProgram()
        data.start_date = DateTime('2012/04/18')
        # Conference ends a day earlier than it starts...
        data.end_date = DateTime('2012/04/17')
        self.assertRaises(Invalid, IProgram.validateInvariants, data)

    def test_rooms_vocabulary(self):
        ''' Vocabulary for rooms should normalize id
        '''
        self.portal.invokeFactory('conference.program', 'program')
        program = self.portal['program']
        program.start_date = DateTime('2012/04/18')
        program.end_date = DateTime('2012/04/18')
        program.rooms = [u'Dorneles Treméa', u'Eric Idle']
        program.reindexObject()
        voc_factory = queryUtility(IVocabularyFactory,
                                   'conference.program.rooms')
        rooms = voc_factory(program)
        tokens = rooms.by_token.keys()
        # Validate tokens
        self.assertTrue('dorneles-tremea' in tokens)
        self.assertTrue('eric-idle' in tokens)

        # Validate values
        values = rooms.by_value.keys()
        self.assertTrue(u'Dorneles Treméa' in values)
        self.assertTrue(u'Eric Idle' in values)


class WorkflowTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.ct = self.portal.portal_catalog
        self.wt = self.portal.portal_workflow
        self.cPerm = self.portal.portal_membership.checkPermission
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('conference.program', 'program')
        self.program = self.portal['program']

    def test_default_state(self):
        review_state = self.wt.getInfoFor(self.program, 'review_state')
        self.assertEquals(review_state, 'closed')

    def test_closed_manager_permissions(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.assertEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_closed_editor_permissions(self):
        setRoles(self.portal, TEST_USER_ID, ['Editor'])

        self.assertEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_closed_contributor_permissions(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        self.assertNotEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_closed_member_permissions(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertNotEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_open_manager_permissions(self):
        self.wt.doActionFor(self.program, 'open')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.assertEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_open_editor_permissions(self):
        self.wt.doActionFor(self.program, 'open')
        setRoles(self.portal, TEST_USER_ID, ['Editor'])

        self.assertEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_open_contributor_permissions(self):
        self.wt.doActionFor(self.program, 'open')
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        self.assertEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_open_member_permissions(self):
        self.wt.doActionFor(self.program, 'open')
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        self.assertEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_finished_manager_permissions(self):
        self.wt.doActionFor(self.program, 'open')
        self.wt.doActionFor(self.program, 'finish')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.assertEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_finished_editor_permissions(self):
        self.wt.doActionFor(self.program, 'open')
        self.wt.doActionFor(self.program, 'finish')
        setRoles(self.portal, TEST_USER_ID, ['Editor'])

        self.assertEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_finished_contributor_permissions(self):
        self.wt.doActionFor(self.program, 'open')
        self.wt.doActionFor(self.program, 'finish')
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        self.assertNotEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_finished_member_permissions(self):
        self.wt.doActionFor(self.program, 'open')
        self.wt.doActionFor(self.program, 'finish')
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        self.assertNotEquals(self.cPerm('conference.program: Add Talk',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Track',
                                          self.program), True)
        self.assertNotEquals(self.cPerm('conference.program: Add Presenter',
                                          self.program), True)

    def test_workflow_transitions(self):
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        review_state = self.wt.getInfoFor(self.program, 'review_state')
        self.assertEquals(review_state, 'closed')
        # Open program
        self.wt.doActionFor(self.program, 'open')
        review_state = self.wt.getInfoFor(self.program, 'review_state')
        self.assertEquals(review_state, 'open')
        # Close program
        self.wt.doActionFor(self.program, 'close')
        review_state = self.wt.getInfoFor(self.program, 'review_state')
        self.assertEquals(review_state, 'closed')
        # Open again program
        self.wt.doActionFor(self.program, 'open')
        review_state = self.wt.getInfoFor(self.program, 'review_state')
        self.assertEquals(review_state, 'open')
        # Finish program
        self.wt.doActionFor(self.program, 'finish')
        review_state = self.wt.getInfoFor(self.program, 'review_state')
        self.assertEquals(review_state, 'finished')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

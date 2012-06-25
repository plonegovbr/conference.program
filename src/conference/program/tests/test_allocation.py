# -*- coding: utf-8 -*-
from datetime import datetime
from pytz import timezone
from DateTime import DateTime
import unittest2 as unittest

from zope.component import queryUtility

from zope.interface import Invalid

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.behavior.interfaces import IBehavior

from conference.program.behaviors.allocation import IAllocation

from conference.program.testing import INTEGRATION_TESTING


class MockAllocation(object):
    location = None
    start_date = None
    end_date = None


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    name = 'conference.program.behaviors.allocation.IAllocation'

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
        allocation = IAllocation(talk)
        self.assertNotEquals(None, allocation)

    def test_adapt_training(self):
        self.program.invokeFactory('conference.training', 'training')
        training = self.program['training']
        allocation = IAllocation(training)
        self.assertNotEquals(None, allocation)

    def test_valid_start_end_dates(self):
        data = MockAllocation()
        data.start_date = DateTime('2012/04/18 11:20:00-0300')
        data.end_date = DateTime('2012/04/18 11:25:00-0300')
        try:
            IAllocation.validateInvariants(data)
        except Invalid:
            self.fail()

    def test_valid_start_end_dates_with_datetime(self):
        tz = timezone('Brazil/East')
        data = MockAllocation()
        data.start_date = datetime(2012, 4, 18, 11, 20, 0, 0, tz)
        data.end_date = datetime(2012, 4, 18, 11, 25, 0, 0, tz)
        try:
            IAllocation.validateInvariants(data)
        except Invalid:
            self.fail()

    def test_valid_empty_dates(self):
        ''' Both empty dates are considered valid as those fields
            are not required
        '''
        data = MockAllocation()
        try:
            IAllocation.validateInvariants(data)
        except Invalid:
            self.fail()

    def test_invalid_empty_start_date(self):
        ''' If we have a valid end_date but an empty start_date
            we will not validate the entry
        '''
        data = MockAllocation()
        data.end_date = DateTime('2012/04/18 11:25:00-0300')
        self.assertRaises(Invalid, IAllocation.validateInvariants, data)

    def test_invalid_empty_end_date(self):
        ''' If we have a valid start_date but an empty end_date
            we will not validate the entry
        '''
        data = MockAllocation()
        data.start_date = DateTime('2012/04/18 11:20:00-0300')
        self.assertRaises(Invalid, IAllocation.validateInvariants, data)

    def test_invalid__end_date(self):
        ''' End date should be in the future of start_date
        '''
        data = MockAllocation()
        data.start_date = DateTime('2012/04/18 11:20:00-0300')
        # Session ends one hour earlier than it starts...
        data.end_date = DateTime('2012/04/18 10:20:00-0300')
        self.assertRaises(Invalid, IAllocation.validateInvariants, data)

        data = MockAllocation()
        data.start_date = DateTime('2012/04/18 11:20:00-0300')
        # Session with duration of 2 minutes is considered invalid here
        data.end_date = DateTime('2012/04/18 11:22:00-0300')
        self.assertRaises(Invalid, IAllocation.validateInvariants, data)

    def test_training_indexing(self):
        self.program.invokeFactory('conference.training', 'training')
        training = self.program['training']
        allocation = IAllocation(training)
        allocation.location = u'Room 1'
        allocation.start_date = DateTime('2012/04/18 11:20:00-0300')
        allocation.end_date = DateTime('2012/04/18 11:40:00-0300')
        training.reindexObject()
        results = self.ct.searchResults(portal_type='conference.training',
                                        getId='training')
        brain = results[0]
        self.assertEquals(allocation.location, brain.location)
        self.assertEquals(allocation.start_date, brain.start)
        self.assertEquals(allocation.end_date, brain.end)

    def test_talk_indexing(self):
        self.program.invokeFactory('conference.talk', 'talk')
        talk = self.program['talk']
        allocation = IAllocation(talk)
        allocation.location = u'Room 1'
        allocation.start_date = DateTime('2012/04/18 13:20:00-0300')
        allocation.end_date = DateTime('2012/04/18 13:40:00-0300')
        talk.reindexObject()
        results = self.ct.searchResults(portal_type='conference.talk',
                                        getId='talk')
        brain = results[0]
        self.assertEquals(allocation.location, brain.location)
        self.assertEquals(allocation.start_date, brain.start)
        self.assertEquals(allocation.end_date, brain.end)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

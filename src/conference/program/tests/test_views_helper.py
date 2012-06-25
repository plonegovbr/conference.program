# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import getMultiAdapter

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from conference.program.behaviors.presenters import IPresenters

from conference.program.testing import INTEGRATION_TESTING


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp_tracks(self, program):
        ''' Create tracks '''
        tracks = []
        tracks_info = [('track-1', u'Track 1'),
                       ('track-2', u'Track 2')]
        for track_id, track_title in tracks_info:
            program.invokeFactory('conference.track', track_id)
            track = program[track_id]
            track.title = track_title
            track.reindexObject()
            tracks.append(track)
        return tracks

    def setUp_presenters(self, program):
        ''' Create presenters '''
        presenters = []
        presenters_info = [('guido', u'Guido van Rossun', 'guido@python.org'),
                         ('turing', u'Alan Turing', 'turing@acm.org'),
                         ('babbage', u'Charles Babbage', 'babbage@acm.org')]
        for s_id, s_title, s_email in presenters_info:
            program.invokeFactory('conference.presenter', s_id)
            presenter = program[s_id]
            presenter.fullname = s_title
            presenter.email = s_email
            presenter.reindexObject()
            presenters.append(presenter)
        return presenters

    def setUp_talks(self, tracks, presenters):
        ''' Create one talk for each presenter in each track '''
        talks = []
        talks_info = [('%s-%s', u'Talk at %s by %s')]
        for t_id, t_title in talks_info:
            for track in tracks:
                for presenter in presenters:
                    track_id = t_id % (track.id, presenter.id)
                    track.invokeFactory('conference.talk', track_id)
                    talk = track[track_id]
                    talk.title = t_title % (track.title, presenter.title)
                    talk.track = self.helper.IUUID(track)
                    talk.level = 'basic'
                    talk.text = 'Foo, bar by %s' % presenter.title
                    talk.language = 'en'
                    adapter = IPresenters(talk)
                    adapter.presenters = [self.helper.IUUID(presenter)]
                    talk.reindexObject()
                    talks.append(talk)
        return talks

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('conference.program', 'program')
        self.program = self.portal['program']
        self.program.languages = ['en']
        self.program.rooms = [u'Dorneles Treméa', u'Eric Idle']
        self.program.reindexObject()
        self.helper = getMultiAdapter((self.program,
                                       self.program.REQUEST), name=u'helper')

        self.tracks = self.setUp_tracks(self.program)
        self.presenters = self.setUp_presenters(self.program)
        self.talks = self.setUp_talks(self.tracks, self.presenters)

    def test_IUUID(self):
        ''' Test IUUID method of program helper view '''
        ct = self.helper.ct
        program = self.program
        brains = ct.searchResults(portal_type='conference.program',
                                  path='/'.join(program.getPhysicalPath()))
        brain_program = brains[0]
        self.assertEquals(self.helper.IUUID(program),
                          brain_program.UID)

    def test_login_url(self):
        ''' Test login_url property of program helper view'''
        self.assertEquals(self.helper.login_url,
                          'http://nohost/plone/login')

    def test_register_url(self):
        ''' Test register_url property of program helper view'''
        self.assertEquals(self.helper.register_url,
                          'http://nohost/plone/@@register')

    def test_tracks(self):
        ''' Test tracks method of program helper view '''
        tracks = self.helper.tracks()
        self.assertEquals(len(tracks), len(self.tracks))
        # Compare titles
        view_titles = [t.Title for t in tracks]
        sorted(view_titles)
        tracks_titles = [t.Title() for t in self.tracks]
        sorted(tracks_titles)
        self.assertEquals(view_titles, tracks_titles)

    def test_talks(self):
        ''' Test talks method of program helper view '''
        talks = self.helper.talks()
        self.assertEquals(len(talks), len(self.talks))
        # Compare titles
        view_titles = [t.Title for t in talks]
        sorted(view_titles)
        talks_titles = [t.Title() for t in self.talks]
        sorted(talks_titles)
        self.assertEquals(view_titles, talks_titles)

    def test_presenters(self):
        ''' Test presenters method of program helper view '''
        presenters = self.helper.presenters()
        self.assertEquals(len(presenters), len(self.presenters))
        # Compare titles
        view_titles = [s.Title for s in presenters]
        sorted(view_titles)
        presenters_titles = [s.Title() for s in self.presenters]
        sorted(presenters_titles)
        self.assertEquals(view_titles, presenters_titles)

    def test_presenter_image(self):
        ''' Test presenter_image method of program helper view '''
        presenter = self.presenters[0]
        presenter_image = self.helper.presenter_image(presenter)
        self.assertEquals(presenter_image, '')

    def test_tracks_dict(self):
        ''' Test tracks_dict method of program helper view '''
        tracks = self.helper.tracks_dict
        self.assertEquals(len(tracks), len(self.tracks))
        track_uid = self.helper.IUUID(self.tracks[0])
        self.assertNotEquals(tracks.get(track_uid), None)
        track = tracks.get(track_uid)
        self.assertEquals(track['title'], self.tracks[0].Title())

    def test_talks_dict(self):
        ''' Test talks_dict method of program helper view '''
        talks = self.helper.talks_dict
        self.assertEquals(len(talks), len(self.talks))
        talk_uid = self.helper.IUUID(self.talks[0])
        self.assertNotEquals(talks.get(talk_uid), None)
        talk = talks.get(talk_uid)
        self.assertEquals(talk['title'], self.talks[0].Title())

    def test_presenters_dict(self):
        ''' Test presenters_dict method of program helper view '''
        presenters = self.helper.presenters_dict
        self.assertEquals(len(presenters), len(self.presenters))
        presenter_uid = self.helper.IUUID(self.presenters[0])
        self.assertNotEquals(presenters.get(presenter_uid), None)
        presenter = presenters.get(presenter_uid)
        self.assertEquals(presenter['name'], self.presenters[0].Title())

    def test_track_info(self):
        ''' Test track_info method of program helper view '''
        track_uid = self.helper.IUUID(self.tracks[0])
        self.assertNotEquals(self.helper.track_info(track_uid), None)
        track = self.helper.track_info(track_uid)
        self.assertEquals(track['title'], self.tracks[0].Title())

    def test_talk_info(self):
        ''' Test talk_info method of program helper view '''
        talk_uid = self.helper.IUUID(self.talks[0])
        self.assertNotEquals(self.helper.talk_info(talk_uid), None)
        talk = self.helper.talk_info(talk_uid)
        self.assertEquals(talk['title'], self.talks[0].Title())

    def test_presenter_info(self):
        ''' Test presenter_info method of program helper view '''
        presenter_uid = self.helper.IUUID(self.presenters[0])
        self.assertNotEquals(self.helper.presenter_info(presenter_uid), None)
        presenter = self.helper.presenter_info(presenter_uid)
        self.assertEquals(presenter['name'], self.presenters[0].Title())

    def test_presenters_by_username(self):
        ''' Test presenters_by_username method of program helper view '''
        presenters = self.helper.presenters_by_username('guido@python.org')
        self.assertEquals(len(presenters), 1)
        presenter = presenters[0]
        self.assertEquals(presenter.Title, u'Guido van Rossun')
        # Another search
        presenters = self.helper.presenters_by_username('turing@acm.org')
        self.assertEquals(len(presenters), 1)
        presenter = presenters[0]
        self.assertEquals(presenter.Title, u'Alan Turing')
        # Non existing user
        presenters = self.helper.presenters_by_username('foo@bar.org')
        self.assertEquals(len(presenters), 0)

    def test_talks_by_username(self):
        ''' Test talks_by_username method of program helper view '''
        talks = self.helper.talks_by_username('guido@python.org')
        self.assertEquals(len(talks), 2)

    def test_talks_presenter(self):
        ''' Test talks_presenter method of program helper view '''
        talks_presenter = self.helper.talks_presenter()
        self.assertEquals(len(talks_presenter.keys()), 3)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

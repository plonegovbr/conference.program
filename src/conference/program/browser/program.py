# -*- coding:utf-8 -*-
from five import grok
from Acquisition import aq_inner

from zope.schema.interfaces import IVocabularyFactory

from zope.component import getMultiAdapter
from zope.component import queryUtility

from plone.uuid.interfaces import IUUID

from plone.memoize.view import memoize

from conference.program.content.program import IProgram

SPEAKER_TYPE = 'conference.presenter'
TALK_TYPE = 'conference.talk'
TRACK_TYPE = 'conference.track'
TRAINING_TYPE = 'conference.training'


class ProgramHelper(grok.View):
    grok.context(IProgram)
    grok.require('zope2.View')
    grok.name('helper')

    def __init__(self, context, request):
        super(ProgramHelper, self).__init__(context, request)
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                      name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                      name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        self.ct = self.tools.catalog()
        self.is_anonymous = self.portal.anonymous()
        self.member = self.portal.member()
        voc = {}
        voc['languages'] = queryUtility(IVocabularyFactory,
                                    'conference.program.languages')(context)
        voc['rooms'] = queryUtility(IVocabularyFactory,
                                    'conference.program.rooms')(context)
        self.voc = voc

    def render(self):
        return ''

    def IUUID(self, obj):
        return IUUID(obj)

    @property
    def login_url(self):
        return '%s/login' % self.portal.portal_url()

    @property
    def register_url(self):
        return '%s/@@register' % self.portal.portal_url()

    @memoize
    def tracks(self, **kw):
        ''' Return catalog brains for conference.program.track '''
        kw['portal_type'] = TRACK_TYPE
        kw['path'] = self._path
        brains = self.ct.searchResults(**kw)
        return brains

    @memoize
    def talks(self, **kw):
        ''' Return catalog brains for conference.program.talk '''
        kw['portal_type'] = TALK_TYPE
        if not 'path' in kw:
            kw['path'] = self._path
        brains = self.ct.searchResults(**kw)
        return brains

    @memoize
    def trainings(self, **kw):
        ''' Return catalog brains for conference.program.training '''
        kw['portal_type'] = TRAINING_TYPE
        if not 'path' in kw:
            kw['path'] = self._path
        brains = self.ct.searchResults(**kw)
        return brains

    @memoize
    def presenters(self, **kw):
        kw['portal_type'] = SPEAKER_TYPE
        kw['path'] = self._path
        brains = self.ct.searchResults(**kw)
        return brains

    def presenter_image_from_brain(self, brain):
        presenter = brain.getObject()
        return self.presenter_image(presenter)

    def presenter_image(self, presenter):
        if not presenter.image:
            return ''
        images_view = getMultiAdapter((presenter, self.request),
                                     name=u'images')
        scale = images_view.scale('image',
                                   width=150,
                                   height=150,
                                   direction='keep')
        url = scale.absolute_url()
        return url

    @property
    def tracks_dict(self):
        brains = self.tracks()
        tracks = dict([(b.UID, {'title': b.Title,
                               'description': b.Description,
                               'review_state': b.review_state,
                               'url': b.getURL(),
                               'json_url': '%s/json' % b.getURL(), })
                    for b in brains])
        return tracks

    @property
    def talks_dict(self):
        brains = self.talks()
        talks = dict([(b.UID, {'title': b.Title,
                               'description': b.Description,
                               'track': b.track,
                               'presenters': b.presenters,
                               'language': b.language,
                               'level': b.level,
                               'location': b.location,
                               'start': b.start,
                               'end': b.end,
                               'review_state': b.review_state,
                               'url': b.getURL(),
                               'json_url': '%s/json' % b.getURL(), })
                    for b in brains])
        return talks

    @property
    def trainings_dict(self):
        brains = self.trainings()
        trainings = dict([(b.UID, {'uid': b.UID,
                                   'title': b.Title,
                                   'description': b.Description,
                                   'track': b.track,
                                   'presenters': b.presenters,
                                   'language': b.language,
                                   'level': b.level,
                                   'review_state': b.review_state,
                                   'location': b.location or '',
                                   'start': b.start,
                                   'end': b.end,
                                   'seats': b.seats or 0,
                                   'url': b.getURL(),
                                   'json_url': '%s/json' % b.getURL(), })
                    for b in brains])
        return trainings

    @property
    def presenters_dict(self):
        spk_img = self.presenter_image_from_brain
        brains = self.presenters()
        presenters = dict([(b.UID, {'name': b.Title,
                     'organization': b.organization,
                     'bio': b.Description,
                     'review_state': b.review_state,
                     'language': b.language,
                     'country': b.country,
                     'state': b.state,
                     'city': b.city,
                     'image_url': spk_img(b),
                     'url': b.getURL(),
                     'json_url': '%s/json' % b.getURL(),
                     })
                    for b in brains])
        return presenters

    @memoize
    def track_info(self, uid):
        ''' Return track info for a given uid '''
        return self.tracks_dict.get(uid, {})

    @memoize
    def talk_info(self, uid):
        ''' Return talk info for a given uid '''
        return self.talks_dict.get(uid, {})

    @memoize
    def presenter_info(self, uid):
        ''' Return presenter info for a given uid '''
        return self.presenters_dict.get(uid, {})

    def presenters_by_username(self, username, **kw):
        # HACK: username is an email
        presenters_profiles = self.presenters(email=username)
        if not presenters_profiles:
            # Let's see if this user created a profile under a different email
            presenters_profiles = self.presenters(Creator=username)
        return presenters_profiles

    def talks_by_username(self, username, **kw):
        # HACK: username is an email
        presenters_profiles = [b.UID
                            for b in self.presenters_by_username(username)]
        kw['presenters'] = tuple(presenters_profiles)
        return self.talks(**kw)

    @memoize
    def talks_presenter(self):
        talks = self.talks_dict
        talks_presenter = {}
        for talk_uid, talk in talks.items():
            presenters = talk['presenters']
            for presenter in presenters:
                if not presenter in talks_presenter:
                    talks_presenter[presenter] = {'all': [],
                                              'confirmed': [],
                                              'submitted': [],
                                              'created': [],
                                              'accepted': [],
                                              'rejected': [],
                                              'cancelled': []}
                talks_presenter[presenter][talk['review_state']].append(talk_uid)
                talks_presenter[presenter]['all'].append(talk_uid)
        return talks_presenter

    @memoize
    def program_stats(self):
        stats = {}
        stats['presenters'] = len([uid
                                 for uid, data in self.talks_presenter().items()
                                 if data['confirmed']])
        stats['talks'] = len(self.talks(review_state='confirmed'))
        stats['tracks'] = len(self.tracks())
        return stats


class View(grok.View):
    grok.context(IProgram)
    grok.require('zope2.View')

    def update(self):
        super(View, self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.helper = getMultiAdapter((context, self.request), name=u'helper')
        self.languages = self.helper.voc['languages']
        self.rooms = self.helper.voc['rooms']
        self.ct = self.helper.ct
        self.is_anonymous = self.helper.is_anonymous
        self.member = self.helper.member
        if not self.helper.state.is_editable():
            self.request['disable_border'] = True

    def tracks(self):
        ''' Return a list of tracks available in this program '''
        helper = self.helper
        results = helper.tracks(sort_on='getObjPositionInParent')
        return results

    def presenters(self):
        ''' Return a list of presenters in this program '''
        helper = self.helper
        results = helper.presenters(sort_on='sortable_title')
        return results

    def talks(self):
        ''' Return a list of talks in this program '''
        helper = self.helper
        results = helper.talks(sort_on='sortable_title')
        return results

    def my_talks(self):
        ''' Return a list of my talks in this program '''
        helper = self.helper
        results = helper.talks_by_username(username=self.member.getUserName(),
                                        sort_on='sortable_title', )
        return results

    def my_talks_accepted(self):
        ''' Return a list of my talks in this program
            waiting for confirmation '''
        helper = self.helper
        results = helper.talks_by_username(username=self.member.getUserName(),
                                        review_state='accepted',
                                        sort_on='sortable_title')
        return results

    def my_talks_confirmed(self):
        ''' Return a list of my talks in this program confirmed '''
        helper = self.helper
        results = helper.talks_by_username(username=self.member.getUserName(),
                                        review_state='confirmed',
                                        sort_on='sortable_title')
        return results

    def my_profiles(self):
        ''' Return a list of my presenter profiles in this program '''
        helper = self.helper
        results = helper.presenters_by_username(username=self.member.getUserName(),
                                           sort_on='sortable_title')
        return results

    def last_talks(self):
        ''' Return a list of the last 5 talks created in this program '''
        helper = self.helper
        results = helper.talks(sort_on='created',
                               sort_order='reverse',
                               sort_limit=5)
        return results[:5]

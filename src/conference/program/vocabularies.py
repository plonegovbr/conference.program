# -*- coding: utf-8 -*-
from five import grok

from zope.component import queryUtility

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName

from plone.i18n.normalizer.interfaces import IIDNormalizer

from conference.program.utils import get_enclosing_program

from conference.program import MessageFactory as _


class TracksVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Look for an enclosing program
            list available tracks inside it '''
        terms = []
        program = get_enclosing_program(context)
        if program:
            program_path = '/'.join(program.getPhysicalPath())
            ct = getToolByName(context, 'portal_catalog')
            results = ct.searchResults(portal_type='conference.program.track',
                                       path=program_path)
            for brain in results:
                term = (brain.UID, brain.UID, brain.Title)
                terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(TracksVocabulary,
                    name=u"conference.program.tracks")


class LanguagesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Look for an enclosing program
            list available languages in it '''
        terms = []
        program = get_enclosing_program(context)
        if program:
            languages = program.languages
            for language in languages:
                term = (language, language, language)
                terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(LanguagesVocabulary,
                    name=u"conference.program.languages")


class RoomsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Look for an enclosing program
            list available rooms in it '''
        normalizer = queryUtility(IIDNormalizer)
        terms = []
        program = get_enclosing_program(context)
        if program:
            rooms = program.rooms
            for room in rooms:
                room_id = normalizer.normalize(room)
                term = (room, room_id, room)
                terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(RoomsVocabulary,
                    name=u"conference.program.rooms")


class LevelsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Look for an enclosing program
            list available languages in it '''
        terms = []
        levels = [('basic', _(u'Basic')),
                  ('intermediate', _(u'Intermediate')),
                  ('advanced', _(u'Advanced')),
                ]
        for code, text in levels:
            term = (code, code, text)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(LevelsVocabulary,
                    name=u"conference.program.levels")

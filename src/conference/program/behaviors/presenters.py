# -*- coding:utf-8 -*-
from Acquisition import aq_inner

from five import grok

from zope import schema

from zope.annotation.interfaces import IAnnotations

from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implements

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from z3c.formwidget.query.interfaces import IQuerySource

from plone.directives import form

from plone.indexer import indexer

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString

from conference.program.content.session import ISession

from conference.program import MessageFactory as _


class PresentersSource(object):
    implements(IQuerySource)

    def __init__(self, context):
        self.context = aq_inner(context)

    @property
    def presenters(self):
        return self.find_presenters()

    @property
    def all_presenters(self):
        return self.find_presenters(filter=False)

    def find_presenters(self, filter=True):
        mt = getToolByName(self.context, 'portal_membership')
        ct = getToolByName(self.context, 'portal_catalog')
        member = mt.getAuthenticatedMember()
        rolesHere = member.getRolesInContext(self.context)
        dictSearch = {'portal_type': 'conference.presenter',
                      'sort_on': 'sortable_title'}
        if filter and not [r for r in rolesHere
                                   if r in ['Manager', 'Reviewer']]:
            #Only list profiles created by this user
            dictSearch['Creator'] = member.getUserName()
        return ct.searchResults(**dictSearch)

    @property
    def vocab(self):
        return SimpleVocabulary([SimpleTerm(b.UID, b.UID, b.Title)
                                for b in self.presenters if hasattr(b, 'UID')])

    @property
    def unfiltered_vocab(self):
        return SimpleVocabulary([SimpleTerm(b.UID, b.UID, b.Title)
                                 for b in self.all_presenters
                                 if hasattr(b, 'UID')])

    def __contains__(self, term):
        return self.vocab.__contains__(term)

    def __iter__(self):
        return self.vocab.__iter__()

    def __len__(self):
        return self.vocab.__len__()

    def getTerm(self, value):
        try:
            term = self.vocab.getTerm(value)
        except LookupError:
            term = self.unfiltered_vocab.getTerm(value)
        return term

    def getTermByToken(self, value):
        try:
            term = self.vocab.getTermByToken(value)
        except LookupError:
            term = self.unfiltered_vocab.getTermByToken(value)
        return term

    def normalizeString(self, value):
        context = self.context
        return normalizeString(value, context).lower()

    def search(self, query_string):
        q = self.normalizeString(query_string)
        return [self.getTerm(b.UID) for b in self.presenters
                                    if q in self.normalizeString(b.Title)]


class PresentersSourceBinder(object):
    implements(IContextSourceBinder)

    def __call__(self, context):
        return PresentersSource(context)


class IPresenters(form.Schema):
    ''' Presenterss to sessions
    '''

    form.fieldset('presenters',
            label=_(u"Session presenter"),
            fields=['presenters'],
    )

    presenters = schema.List(
            title=_(u"Session presenter"),
            description=_(u'Please fill in the name of the presenter.'
                          u'If no presenter profile was created for this name,'
                          u' click on Add new presenter'),
            value_type=schema.Choice(title=_(u"Presenters"),
                                     source=PresentersSourceBinder()),
            required=True,
    )


alsoProvides(IPresenters, form.IFormFieldProvider)


class Presenters(object):
    ''' adapter for IPresenters '''

    implements(IPresenters)
    adapts(ISession)

    def __init__(self, context):
        self.context = context
        self.annotation = IAnnotations(self.context)

    @property
    def presenters(self):
        return self.annotation.get('presenter.presenters', [])

    @presenters.setter
    def presenters(self, value):
        self.annotation['presenter.presenters'] = value


@indexer(ISession)
def presentersIndexer(obj):
    presenter_adapter = IPresenters(obj, None)
    if presenter_adapter and presenter_adapter.presenters:
        return presenter_adapter.presenters
grok.global_adapter(presentersIndexer, name="presenters")

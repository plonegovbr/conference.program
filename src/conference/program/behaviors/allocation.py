# -*- coding:utf-8 -*-
from five import grok

from DateTime import DateTime

from zope import schema

from zope.annotation.interfaces import IAnnotations

from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implements

from zope.interface import invariant
from zope.interface import Invalid

from plone.indexer import indexer

from plone.directives import form
from plone.directives import dexterity

from conference.program.content.session import ISession

from conference.program import MessageFactory as _


class InvalidDateRange(Invalid):
    __doc__ = _(u"Please fix the provided information.")


class IAllocation(form.Schema):
    ''' Allocate objects in a conference program
    '''

    form.fieldset('allocation',
            label=_(u"Session allocation"),
            fields=['location', 'start_date', 'end_date'],
    )

    dexterity.read_permission(location='zope2.View')
    dexterity.write_permission(location='conference.program.AllocateSession')
    location = schema.Choice(
        title=_(u"Location"),
        required=False,
        description=_(u"Room where this session will be presented"),
        vocabulary='conference.program.rooms',
    )

    dexterity.read_permission(start_date='zope2.View')
    dexterity.write_permission(start_date='conference.program.AllocateSession')
    start_date = schema.Datetime(
        title=_(u"Start date"),
        required=False,
        description=_(u"Talk start date"),
    )

    dexterity.read_permission(end_date='zope2.View')
    dexterity.write_permission(end_date='conference.program.AllocateSession')
    end_date = schema.Datetime(
        title=_(u"End date"),
        required=False,
        description=_(u"Talk end date"),
    )

    @invariant
    def validate_duration(data):
        ''' Validate provided start and end date'''
        start_date = data.start_date
        end_date = data.end_date
        if start_date or end_date:
            # As it is not required we will only check if
            # any of these fields are provided
            if not (start_date and end_date):
                msg = _(u'Please provide a start and an end date')
                raise InvalidDateRange(msg)
            # Use datetime instead of DateTime
            if isinstance(start_date, DateTime):
                start_date = start_date.asdatetime()
            if isinstance(end_date, DateTime):
                end_date = end_date.asdatetime()
            # We will have a timedelta object here
            delta = end_date - start_date
            if not(delta.days > -1 and delta.seconds >= 300):
                msg = _(u'End date must be in the future of start date and '
                        u'duration of session should be at least 5 minutes.')
                raise InvalidDateRange(msg)


alsoProvides(IAllocation, form.IFormFieldProvider)


class Allocation(object):
    ''' adapter for IAllocation '''

    implements(IAllocation)
    adapts(ISession)

    def __init__(self, context):
        self.context = context
        self.annotation = IAnnotations(self.context)

    @property
    def location(self):
        return self.annotation.get('allocation.location', '')

    @location.setter
    def location(self, value):
        self.annotation['allocation.location'] = value

    @property
    def start_date(self):
        return self.annotation.get('allocation.start_date', '')

    @start_date.setter
    def start_date(self, value):
        self.annotation['allocation.start_date'] = value

    @property
    def end_date(self):
        return self.annotation.get('allocation.end_date', '')

    @end_date.setter
    def end_date(self, value):
        self.annotation['allocation.end_date'] = value


@indexer(ISession)
def locationIndexer(obj):
    allocation = IAllocation(obj, None)
    if allocation and allocation.location:
        return allocation.location
grok.global_adapter(locationIndexer, name="location")


@indexer(ISession)
def startIndexer(obj):
    allocation = IAllocation(obj, None)
    if allocation and allocation.start_date:
        date = allocation.start_date
        if not isinstance(date, DateTime):
            date = DateTime('%s' % date.isoformat())
        return date
grok.global_adapter(startIndexer, name="start")


@indexer(ISession)
def endIndexer(obj):
    allocation = IAllocation(obj, None)
    if allocation and allocation.end_date:
        date = allocation.end_date
        if not isinstance(date, DateTime):
            date = DateTime('%s' % date.isoformat())
        return date
grok.global_adapter(endIndexer, name="end")

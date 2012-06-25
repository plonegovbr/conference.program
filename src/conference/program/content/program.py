# -*- coding:utf-8 -*-
from DateTime import DateTime

from five import grok
from zope import schema

from zope.interface import invariant
from zope.interface import Invalid

from plone.indexer import indexer

from plone.directives import dexterity, form

from conference.program import MessageFactory as _


class InvalidDateRange(Invalid):
    __doc__ = _(u"Please fix the provided information.")


class IProgram(form.Schema):
    """
    Conference Program
    """

    start_date = schema.Date(
        title=_(u"Start date"),
        required=True,
        description=_(u"Conference start date"),
    )

    end_date = schema.Date(
        title=_(u"End date"),
        required=True,
        description=_(u"Conference end date"),
    )

    form.fieldset('venue',
            label=_(u"Venue capabilities"),
            fields=['rooms', ],
    )

    form.widget(rooms='plone.z3cform.textlines.TextLinesFieldWidget')
    rooms = schema.List(
        title=_(u'Conference rooms'),
        description=_(u'Please inform a list of available rooms to the'
                      u'conference, one room per line.'),
        default=[],
        value_type=schema.TextLine(),
        required=True,
        )

    form.fieldset('session',
            label=_(u"Session Config "),
            fields=['languages', ],
    )

    languages = schema.List(
        title=_(u'Conference languages'),
        description=_(u'Select which languages will be available for'
                      u'presenters to choose from when proposing a talk.'),
        value_type=schema.Choice(
                vocabulary='plone.app.vocabularies.SupportedContentLanguages'),
        required=True,
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
                start_date = start_date.asdatetime().date()
            if isinstance(end_date, DateTime):
                end_date = end_date.asdatetime().date()
            # We will have a timedelta object here
            delta = end_date - start_date
            if not(delta.days > -1):
                msg = _(u'End date must not be prior to start date')
                raise InvalidDateRange(msg)


@indexer(IProgram)
def startIndexer(obj):
    if obj.start_date:
        date = obj.start_date
        if not isinstance(date, DateTime):
            date = DateTime('%s' % date.isoformat())
        return date
grok.global_adapter(startIndexer, name="start")


@indexer(IProgram)
def endIndexer(obj):
    if obj.end_date:
        date = obj.end_date
        if not isinstance(date, DateTime):
            date = DateTime('%s' % date.isoformat())
        return date
grok.global_adapter(endIndexer, name="end")


class Program(dexterity.Container):
    grok.implements(IProgram)

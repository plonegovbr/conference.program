# -*- coding:utf-8 -*-
from five import grok
from zope import schema

from plone.directives import dexterity, form

from plone.namedfile.field import NamedImage

from plone.uuid.interfaces import IUUID

from conference.program import MessageFactory as _


class ITrack(form.Schema):
    """
    A track inside a conference
    """

    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Please inform title for this track'),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=True,
        description=_(u"A brief description of this track."),
    )

    image = NamedImage(
        title=_(u"Track Logo"),
        required=False,
        description=_(u"Upload an image to be used as this track's logo."),
    )


class Track(dexterity.Container):
    grok.implements(ITrack)

    @property
    def track(self):
        ''' Return uuid for this object '''
        return IUUID(self)

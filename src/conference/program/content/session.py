# -*- coding:utf-8 -*-
from five import grok
from zope import schema

from plone.directives import dexterity
from plone.directives import form

from conference.program import MessageFactory as _


class ISession(form.Schema):
    """
    A session in a conference.
    """

    title = schema.TextLine(
        title=_(u'Session Title'),
        description=_(u'Inform a title for this session'),
        required=True,
    )

    track = schema.Choice(
        title=_(u"Track"),
        required=True,
        description=_(u"Which track this session is"),
        vocabulary='conference.program.tracks',
    )

    level = schema.Choice(
        title=_(u"Level"),
        required=True,
        description=_(u"Level of this session"),
        vocabulary='conference.program.levels',
    )

    form.widget(text='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    text = schema.Text(
        title=_(u"Session abstract"),
        required=True,
        description=_(u"An abstract of this session"),
    )

    language = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Language this session will be presented at"),
        vocabulary='conference.program.languages',
    )


class Session(dexterity.Item):
    grok.implements(ISession)

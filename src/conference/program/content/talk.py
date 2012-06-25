# -*- coding:utf-8 -*-
from five import grok
from zope import schema

from plone.directives import form

from conference.program.content.session import ISession
from conference.program.content.session import Session

from conference.program import MessageFactory as _


class ITalk(ISession):
    """
    A talk in a conference
    """

    title = schema.TextLine(
        title=_(u'Talk Title'),
        description=_(u'Inform a talk title'),
        required=True,
    )

    track = schema.Choice(
        title=_(u"Track"),
        required=True,
        description=_(u"Which track this talk is"),
        vocabulary='conference.program.tracks',
    )

    level = schema.Choice(
        title=_(u"Level"),
        required=True,
        description=_(u"Level of this talk"),
        vocabulary='conference.program.levels',
    )

    form.widget(text='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    text = schema.Text(
        title=_(u"Talk abstract"),
        required=True,
        description=_(u"An abstract of this talk"),
    )

    language = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Language this talk will be given"),
        vocabulary='conference.program.languages',
    )


class Talk(Session):
    grok.implements(ITalk)

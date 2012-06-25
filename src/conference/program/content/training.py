# -*- coding:utf-8 -*-
from five import grok
from zope import schema

from plone.directives import form

from conference.program.content.session import ISession
from conference.program.content.session import Session

from conference.program import MessageFactory as _


class ITraining(ISession):
    """
    A training in a conference
    """

    title = schema.TextLine(
        title=_(u'Training Title'),
        description=_(u'Inform a training title'),
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
        description=_(u"Level of this training"),
        vocabulary='conference.program.levels',
    )

    form.widget(text='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    text = schema.Text(
        title=_(u"Training abstract"),
        required=True,
        description=_(u"An abstract of this training"),
    )

    form.widget(text='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    requirements = schema.Text(
        title=_(u"Training requirements"),
        required=True,
        description=_(u"What are the requirements for this training session?"),
    )

    language = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Language this training will be given"),
        vocabulary='conference.program.languages',
    )


class Training(Session):
    grok.implements(ITraining)

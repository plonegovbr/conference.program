# -*- coding:utf-8 -*-
from five import grok
from plone.directives import dexterity, form

from plone.namedfile.field import NamedImage
#from plone.formwidget.contenttree import ObjPathSourceBinder

from zope import schema

#from z3c.relationfield.schema import RelationChoice

#from conference.registration.attendee import IAttendee

from conference.program import MessageFactory as _


class IPresenter(form.Schema):
    """
    A presenter in the conference
    """

    fullname = schema.TextLine(
        title=_(u'Fullname'),
        description=_(u'Please inform your fullname'),
        required=True,
    )

    description = schema.Text(
        title=_(u"Biografy"),
        required=True,
        description=_(u"A brief biografy"),
    )

    organization = schema.TextLine(
        title=_(u"Organization"),
        required=True,
        description=_(u"Organization you represent"),
    )

    email = schema.TextLine(
        title=_(u"Email"),
        required=True,
        description=_(u"Presenter's email"),
    )

    home_page = schema.TextLine(
        title=_(u"Site"),
        required=True,
        description=_(u"Presenter's site"),
    )

    language = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Presenter's language"),
        vocabulary='apyb.papers.languages',
    )

    image = NamedImage(
        title=_(u"Portrait"),
        required=False,
        description=_(u"Upload an image to be used as presenters' portrait."),
    )

#    form.fieldset('registration',
#            label=_(u"Registering Information"),
#            fields=['registration', ],
#    )
#    dexterity.read_permission(registration='cmf.ReviewPortalContent')
#    dexterity.write_permission(registration='cmf.ReviewPortalContent')
#    registration = RelationChoice(
#     title=_(u"Registration"),
#     source=ObjPathSourceBinder(object_provides=IAttendee.__identifier__),
#     required=False,
#    )


class Presenter(dexterity.Item):
    grok.implements(IPresenter)

    @property
    def title(self):
        return self.fullname

    @title.setter
    def title(self, value):
        pass

    def Title(self):
        return self.title

    def Description(self):
        return self.description

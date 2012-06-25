# -*- coding:utf-8 -*-
from five import grok

from collective.grok import gs
from collective.grok import i18n

from Products.CMFPlone.interfaces import INonInstallable

from conference.program import MessageFactory as _

PROJECTNAME = 'conference.program'
PROFILE_ID = 'conference.program:default'


# Default Profile
gs.profile(name=u'default',
           title=_(u'conference.program'),
           description=_(u'Installs conference.program'),
           directory='profiles/default')

# Uninstall Profile
gs.profile(name=u'uninstall',
           title=_(u'Uninstall conference.program'),
           description=_(u'Uninstall conference.program'),
           directory='profiles/uninstall')

i18n.registerTranslations(directory='locales')


class HiddenProfiles(grok.GlobalUtility):

    grok.implements(INonInstallable)
    grok.provides(INonInstallable)
    grok.name('conference.program')

    def getNonInstallableProfiles(self):
        profiles = ['conference.program:uninstall', ]
        return profiles

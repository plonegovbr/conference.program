# -*- coding: utf-8 -*-
from collective.grok import gs


@gs.upgradestep(title=u'Initial upgrade steo',
                description=u'Upgrade step run at install time',
                source='0.0', destination='1000', sortkey=1,
                profile='conference.program:default')
def fromZero(context):
    """ Upgrade from Zero to version 1000
    """
    pass
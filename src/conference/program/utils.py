# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from conference.program.content.program import IProgram


def get_enclosing_program(context):
    ''' Given a context, find the enclosing program '''
    context = aq_inner(context)
    while not (IProgram.providedBy(context) or
               IPloneSiteRoot.providedBy(context)):
        context = aq_parent(context)
    return IProgram.providedBy(context) and context or None

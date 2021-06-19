#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Please don't remove this disclaimer
# modified by Madhouse to run under Python2/3
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE
import os
import gettext
import sys
PluginLanguageDomain = 'NGsetting'
PluginLanguagePath = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Po'

def localeInit():
    lang = language.getLanguage()[:2]
    os.environ['LANGUAGE'] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE, ''))

def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.dgettext('enigma2', txt)
    return t

localeInit()
language.addCallback(localeInit)

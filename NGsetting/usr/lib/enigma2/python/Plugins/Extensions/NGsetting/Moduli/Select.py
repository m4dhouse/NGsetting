#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Please don't remove this disclaimer
# modified by Madhouse to run under Python2/3
from Components.Label import Label
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Plugins.Plugin import PluginDescriptor
from enigma import getDesktop
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import *
import sys
import os
from .Config import *
from .Language import _
HD = getDesktop(0).size()

class MenuListSelect(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if HD.width() > 1280:
            self.l.setFont(0, gFont('Regular', 36))
            self.l.setItemHeight(65)
        else:
            self.l.setFont(0, gFont('Regular', 25))
            self.l.setItemHeight(45)

class ListSelect:

    def __init__(self):
        pass

    def readSaveList(self):
        try:
            jw = open('/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/Select')
            jjw = jw.readlines()
            jw.close()
            list = []
            for x in jjw:
                try:
                    jx = x.split('---')
                    list.append((jx[0], jx[1].strip()))
                except:
                    pass
            return list
        except:
            pass

    def SaveList(self, list):
        jw = open('/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/Select', 'w')
        for dir, name, value in list:
            if value == '1':
                jw.write(dir + '---' + name + '\n')
        jw.close()

    def readBouquetsList(self, pwd, bouquetname):
        try:
            f = open(pwd + '/' + bouquetname)
        except Exception as e:
            print(e)
            return
        ret = []
        while True:
            line = f.readline()
            if line == '':
                break
            if line[:8] != '#SERVICE':
                continue
            tmp = line.strip().split(':')
            line = tmp[(len(tmp) - 1)]
            filename = None
            if line[:12] == 'FROM BOUQUET':
                tmp = line[13:].split(' ')
                filename = tmp[0].strip('"')
            else:
                filename = line
            if filename:
                try:
                    fb = open(pwd + '/' + filename)
                except Exception as e:
                    continue
                tmp = fb.readline().strip()
                if tmp[:6] == '#NAME ':
                    ret.append([filename, tmp[6:]])
                else:
                    ret.append([filename, filename])
                fb.close()
        return ret

    def readBouquetsTvList(self, pwd):
        return self.readBouquetsList(pwd, 'bouquets.tv')

    def TvList(self):
        jload = self.readSaveList()
        self.bouquetlist = []
        for x in self.readBouquetsTvList('/etc/enigma2'):
            value = '0'
            try:
                for j, jx in jload:
                    if j == x[0] and jx.find(x[1]) != -1:
                        value = '1'
                        break
            except:
                pass
            self.bouquetlist.append((x[0], x[1], value))
        return self.bouquetlist

class MenuSelect(Screen, ConfigListScreen):

    def __init__(self, session):
        self.session = session
        if HD.width() > 1280:
            skin = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Skin/Main_fhd.xml'
        else:
            skin = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Skin/Main_hd.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.ListSelect = ListSelect()
        self['autotimer'] = Label('')
        self['namesat'] = Label('')
        self['text'] = Label('')
        self['dataDow'] = Label('')
        self['Green'] = Pixmap()
        self['Blue'] = Pixmap()
        self['Yellow'] = Pixmap()
        self['Green'].hide()
        self['Yellow'].hide()
        self['Blue'].hide()
        self['Key_Lcn'] = Label('')
        self['Key_Red'] = Label(_('Exit'))
        self['Key_Green'] = Label(_('Setting Installed:'))
        self['Key_Personal'] = Label('')
        self['A'] = MenuListSelect([])
        self['B'] = MenuListSelect([])
        self['B'].selectionEnabled(1)
        self.Info()
        self.Menu()
        self.MenuA()
        self['actions'] = ActionMap(['OkCancelActions', 'ShortcutActions', 'WizardActions', 'ColorActions', 'SetupActions', 'NumberActions', 'MenuActions', 'HelpActions', 'EPGSelectActions'], {'ok': self.OkSelect,
           'up': self.keyUp,
           'down': self.keyDown,
           'cancel': self.Uscita,
           'nextBouquet': self['B'].pageUp,
           'prevBouquet': self['B'].pageDown,
           'red': self.Uscita}, -1)

    def Info(self):
        AutoTimer, NameSat, Data, Type, Personal, DowDate = Load()
        if str(Data) == '0':
            newdate = ''
        else:
            newdate = ' - ' + ConverDate(Data)
        if str(DowDate) == '0':
            newDowDate = _('Last Update: Unregistered')
        else:
            newDowDate = _('Last Update: ') + DowDate
        self['namesat'].setText(NameSat + newdate)
        self['dataDow'].setText(newDowDate)

    def Uscita(self):
        self.close()

    def keyUp(self):
        self['B'].up()

    def keyDown(self):
        self['B'].down()

    def hauptListEntry(self, dir, name, value):
        res = [(dir, name, value)]
        if HD.width() > 1280:
            icon = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Panel/redpanel.png'
        else:
            icon = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Panel/redpanel_hd.png'
        if value == '1':
            if HD.width() > 1280:
                icon = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Panel/greenpanel.png'
            else:
                icon = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Panel/greenpanel_hd.png'
        try:
            name = name.split('   ')[0]
        except:
            pass
        if HD.width() > 1280:
            res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 14), size=(30, 30), png=loadPic(icon, 30, 30, 0, 0, 0, 1)))
            res.append(MultiContentEntryText(pos=(70, 7), size=(425, 40), font=0, text=name, flags=RT_HALIGN_LEFT))
        else:
            res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 11), size=(20, 20), png=loadPic(icon, 20, 20, 0, 0, 0, 1)))
            res.append(MultiContentEntryText(pos=(50, 7), size=(425, 40), font=0, text=name, flags=RT_HALIGN_LEFT))
        res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=dir, flags=RT_HALIGN_LEFT))
        res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, text=value, flags=RT_HALIGN_LEFT))
        return res

    def hauptListEntryA(self, name):
        res = [name]
        try:
            name = name.split('   ')[0]
        except:
            pass
        if HD.width() > 1280:
            res.append(MultiContentEntryText(pos=(20, 7), size=(425, 40), font=0, text=name, flags=RT_HALIGN_LEFT))
        else:
            res.append(MultiContentEntryText(pos=(10, 7), size=(425, 40), font=0, text=name, flags=RT_HALIGN_LEFT))
        return res

    def MenuA(self):
        self.jB = []
        lista = self.ListSelect.readSaveList()
        if lista:
            for dir, name in lista:
                self.jB.append(self.hauptListEntryA(name))
        self['A'].setList(self.jB)
        if not self.jB:
            self['text'].setText('      Maintenance\n          Folders\n       Customized')
        else:
            self['text'].setText(' ')
        self['B'].selectionEnabled(1)
        self['A'].selectionEnabled(0)

    def Menu(self):
        self.jA = []
        for dir, name, value in self.ListSelect.TvList():
            if name != 'Digitale Terrestre' and name != 'Favourites (TV)' and name[2:] != 'Vhannibal Settings':
                self.jA.append(self.hauptListEntry(dir, name, value))
        self['B'].setList(self.jA)

    def OkSelect(self):
        NewName = self['B'].getCurrent()[0][1]
        NewDir = self['B'].getCurrent()[0][0]
        self.list = []
        for dir, name, value in self.ListSelect.TvList():
            if dir == NewDir and name == NewName:
                if value == '0':
                    self.list.append((dir, name, '1'))
            elif value == '1':
                self.list.append((dir, name, '1'))
        self.ListSelect.SaveList(self.list)
        self.Menu()
        self.MenuA()

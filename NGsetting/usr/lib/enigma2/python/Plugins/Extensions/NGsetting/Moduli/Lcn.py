#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Please don't remove this disclaimer
# modified by Madhouse to run under Python2/3
from enigma import eDVBDB, eServiceReference, eServiceCenter
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigSubsection, ConfigYesNo, ConfigSelection, configfile
from Tools.Directories import resolveFilename, SCOPE_CONFIG
from enigma import *
from .Config import *
import os
import sys
import re
import xml.etree.cElementTree as ET

def Bouquet():
    for file in os.listdir('/etc/enigma2/'):
        if re.search('^userbouquet.*.tv', file):
            f = open('/etc/enigma2/' + file, 'r')
            x = f.read()
            if re.search('#NAME Digitale Terrestre', x, flags=re.IGNORECASE):
                return '/etc/enigma2/' + file

class LCN:
    service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'

    def __init__(self):
        self.dbfile = '/var/etc/enigma2/lcndb'
        self.bouquetfile = Bouquet()
        self.lcnlist = []
        self.markers = []
        self.e2services = []
        mdom = ET.parse('/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/rules.xml')
        self.root = None
        for x in mdom.getroot():
            if x.tag == 'ruleset' and x.get('name') == 'Italy':
                self.root = x
                return
        return

    def addLcnToList(self, namespace, nid, tsid, sid, lcn, signal):
        for x in self.lcnlist:
            if x[0] == lcn and x[1] == namespace and x[2] == nid and x[3] == tsid and x[4] == sid:
                return
        if lcn == 0:
            return
        for i in range(0, len(self.lcnlist)):
            if self.lcnlist[i][0] == lcn:
                if self.lcnlist[i][5] > signal:
                    self.addLcnToList(namespace, nid, tsid, sid, lcn + 16536, signal)
                else:
                    znamespace = self.lcnlist[i][1]
                    znid = self.lcnlist[i][2]
                    ztsid = self.lcnlist[i][3]
                    zsid = self.lcnlist[i][4]
                    zsignal = self.lcnlist[i][5]
                    self.lcnlist[i][1] = namespace
                    self.lcnlist[i][2] = nid
                    self.lcnlist[i][3] = tsid
                    self.lcnlist[i][4] = sid
                    self.lcnlist[i][5] = signal
                    self.addLcnToList(znamespace, znid, ztsid, zsid, lcn + 16536, zsignal)
                return
            if self.lcnlist[i][0] > lcn:
                self.lcnlist.insert(i, [lcn, namespace, nid, tsid, sid, signal])
                return
        self.lcnlist.append([lcn, namespace, nid, tsid, sid, signal])

    def renumberLcn(self, range, rule):
        tmp = range.split('-')
        if len(tmp) != 2:
            return
        min = int(tmp[0])
        max = int(tmp[1])
        for x in self.lcnlist:
            if x[0] >= min and x[0] <= max:
                value = x[0]
                cmd = 'x[0] = ' + rule
                try:
                    exec(cmd)
                except Exception as e:
                    print(e)

    def addMarker(self, position, text):
        self.markers.append([position, text])

    def read(self):
        self.readE2Services()
        try:
            f = open(self.dbfile)
        except Exception as e:
            print(e)
            return
        while True:
            line = f.readline()
            if line == '':
                break
            line = line.strip()
            if len(line) != 38:
                continue
            tmp = line.split(':')
            if len(tmp) != 6:
                continue
            self.addLcnToList(int(tmp[0], 16), int(tmp[1], 16), int(tmp[2], 16), int(tmp[3], 16), int(tmp[4]), int(tmp[5]))
        if self.root is not None:
            for x in self.root:
                if x.tag == 'rule':
                    if x.get('type') == 'marker':
                        self.addMarker(int(x.get('position')), x.text)
        self.markers.sort(key=lambda z: int(z[0]))
        return

    def readE2Services(self):
        self.e2services = []
        refstr = '%s ORDER BY name' % self.service_types_tv
        ref = eServiceReference(refstr)
        serviceHandler = eServiceCenter.getInstance()
        servicelist = serviceHandler.list(ref)
        if servicelist is not None:
            while True:
                service = servicelist.getNext()
                if not service.valid():
                    break
                unsigned_orbpos = service.getUnsignedData(4) >> 16
                if unsigned_orbpos == 61166:
                    self.e2services.append(service.toString())
        return

    def ClearDoubleMarker(self, UserBouquet):
        if os.path.exists(UserBouquet):
            ReadFile = open(UserBouquet, 'r')
            uBQ = ReadFile.readlines()
            ReadFile.close()
            WriteFile = open(UserBouquet, 'w')
            LineMaker = []
            PosDelMaker = []
            x = 1
            for line in uBQ:
                if line.find('#SERVICE 1:64:'):
                    x += 1
                    continue
                elif line.find('#DESCRIPTION'):
                    LineMaker.append(x)
                x += 1
            START = 0
            STOP = 0
            i = 0
            for xx in LineMaker:
                if i + 1 < len(LineMaker):
                    START = LineMaker[i]
                    STOP = LineMaker[(i + 1)]
                    if STOP - START < 3:
                        PosDelMaker.append(START)
                        PosDelMaker.append(START + 1)
                    if uBQ[START] == uBQ[STOP]:
                        PosDelMaker.append(STOP)
                        PosDelMaker.append(STOP + 1)
                i += 1
            PosDelMaker.reverse()
            for delmark in PosDelMaker:
                del uBQ[delmark - 1]
            for x in uBQ:
                WriteFile.write(x)
            WriteFile.close()

    def writeBouquet(self):
        try:
            f = open(self.bouquetfile, 'w')
        except Exception as e:
            print(e)
            return
        f.write('#NAME Digitale Terrestre\n')
        for x in self.lcnlist:
            if len(self.markers) > 0:
                if x[0] > self.markers[0][0]:
                    f.write('#SERVICE 1:64:0:0:0:0:0:0:0:0:\n')
                    f.write('#DESCRIPTION ------- ' + self.markers[0][1] + ' -------\n')
                    self.markers.remove(self.markers[0])
            refstr = '1:0:1:%x:%x:%x:%x:0:0:0:' % (x[4], x[3], x[2], x[1])
            refsplit = eServiceReference(refstr).toString().split(':')
            for tref in self.e2services:
                tmp = tref.split(':')
                if tmp[3] == refsplit[3] and tmp[4] == refsplit[4] and tmp[5] == refsplit[5] and tmp[6] == refsplit[6]:
                    f.write('#SERVICE ' + tref + '\n')
                    break
        f.close()
        self.ClearDoubleMarker(self.bouquetfile)

    def reloadBouquets(self):
        eDVBDB.getInstance().reloadBouquets()

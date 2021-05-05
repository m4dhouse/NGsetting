#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from random import choice
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
import re
import os
import sys
from enigma import *
from .Setting import *
try:
    py_version = sys.version_info.major
except:
    py_version = 3

Directory = os.path.dirname(sys.modules[__name__].__file__)
if not os.path.exists(Directory + '/NGsetting'):
    os.system('mkdir  ' + Directory + '/NGsetting')
if not os.path.exists(Directory + '/NGsetting/Temp'):
    os.system('mkdir  ' + Directory + '/NGsetting/Temp')

def ConverDate(data):
    anno = data[:2]
    mese = data[-4:][:2]
    giorno = data[-2:]
    return giorno + '/' + mese + '/' + anno

def ConverDate_noyear(data):
    mese = data[-4:][:2]
    giorno = data[-2:]
    return giorno + '/' + mese

def DownloadSetting():
    list = []
    try:
        import requests
        link = requests.get('http://www.vhannibal.net/asd.php', headers = {'User-Agent': 'Mozilla/5.0'}).text
        xx = re.compile('<td><a href="(.+?)">(.+?)</a></td>.*?<td>(.+?)</td>', re.DOTALL).findall(link)
        for link, name, date in xx:
            list.append((date, name.replace('Vhannibal ', ''), 'http://www.vhannibal.net/' + link))
    except ImportError:
        req = Request('http://www.vhannibal.net/asd.php')
        req.add_header('User-Agent', 'VAS14')
        response = urlopen(req)
        link = response.read()
        response.close()
        xx = re.compile('<td><a href="(.+?)">(.+?)</a></td>.*?<td>(.+?)</td>', re.DOTALL).findall(link)
        for link, name, date in xx:
            list.append((date, name.replace('Vhannibal ', ''), 'http://www.vhannibal.net/' + link))
    except:
        pass
    return list

def Load():
    AutoTimer = '0'
    if py_version == 2:
        NameSat = 'Hot Bird 13\xc2\xb0E'
    else:
        NameSat = 'Hot Bird 13°E'
    Data = '0'
    Type = '0'
    Personal = '0'
    DowDate = '0'
    if os.path.exists(Directory + '/NGsetting/Date'):
        xf = open(Directory + '/NGsetting/Date', 'r')
        f = xf.readlines()
        xf.close()
        for line in f:
            try:
                LoadDate = line.strip()
                elements = LoadDate.split('=')
                if LoadDate.find('AutoTimer') != -1:
                    AutoTimer = elements[1][1:]
                elif LoadDate.find('NameSat') != -1:
                    NameSat = elements[1][1:]
                elif LoadDate.find('Data') != -1:
                    Data = elements[1][1:]
                elif LoadDate.find('Type') != -1:
                    Type = elements[1][1:]
                elif LoadDate.find('Personal') != -1:
                    Personal = elements[1][1:]
                elif LoadDate.find('DowDate') != -1:
                    DowDate = elements[1][1:]
            except:
                pass
    else:
        xf = open(Directory + '/NGsetting/Date', 'w')
        xf.write('AutoTimer = 0\n')
        if py_version == 2:
            xf.write('NameSat= Hot Bird 13\xc2\xb0E\n')
        else:
            xf.write('NameSat= Hot Bird 13°E\n')
        xf.write('Data = 0\n')
        xf.write('Type = 0\n')
        xf.write('Personal = 0\n')
        xf.write('DowDate = 0\n')
        xf.close()
    return (
     AutoTimer, NameSat, Data, Type, Personal, DowDate)

def WriteSave(name, autotimer, Type, Data, Personal, DowDate):
    xf = open(Directory + '/NGsetting/Date', 'w')
    xf.write('AutoTimer = %s\n' % str(autotimer))
    xf.write('NameSat = %s\n' % str(name))
    xf.write('Data = %s\n' % str(Data))
    xf.write('Type = %s\n' % str(Type))
    xf.write('Personal = %s\n' % str(Personal))
    xf.write('DowDate = %s\n' % str(DowDate))
    xf.close()

def Plugin():
    try:
        import requests
        link = requests.get('http://www.vhannibal.net/asu.php', headers = {'User-Agent': 'Mozilla/5.0'}).text
        return re.compile('<a href="(.+?)" src="(.+?)">updater</a>').findall(link)
    except ImportError:
        req = Request('http://www.vhannibal.net/asu.php')
        req.add_header('User-Agent', 'VAS14')
        response = urlopen(req, None, 3)
        link = response.read()
        response.close()
        return re.compile('<a href="(.+?)" src="(.+?)">updater</a>').findall(link)
    except:
        return
    return

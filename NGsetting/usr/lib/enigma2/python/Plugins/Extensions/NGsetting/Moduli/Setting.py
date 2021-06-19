#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Please don't remove this disclaimer
# modified by Madhouse to run under Python2/3
from enigma import eTimer
from random import choice
import re
import glob
import shutil
import os
import time
import sys
from os import statvfs
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from enigma import *
from .Config import *
from .Language import _
try:
    py_version = sys.version_info.major
except:
    py_version = 3
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
try:
    from requests import get
except ImportError:
    pass

Directory = os.path.dirname(sys.modules[__name__].__file__)
#Directory = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli'

def TimerControl():
    now = time.localtime(time.time())
    Ora = str(now[3]).zfill(2) + ':' + str(now[4]).zfill(2) + ':' + str(now[5]).zfill(2)
    Date = str(now[2]).zfill(2) + '-' + str(now[1]).zfill(2) + '-' + str(now[0])
    return '%s ora: %s' % (Date, Ora)

def StartSavingTerrestrialChannels():

    def ForceSearchBouquetTerrestrial():
        for file in sorted(glob.glob('/etc/enigma2/*.tv')):
            f = open(file, 'r').read()
            x = f.strip().lower()
            if x.find('eeee0000') != -1:
                if x.find('82000') == -1 and x.find('c0000') == -1:
                    return file
                    break

    def ResearchBouquetTerrestrial(search):
        for file in sorted(glob.glob('/etc/enigma2/*.tv')):
            f = open(file, 'r').read()
            x = f.strip().lower()
            x1 = f.strip()
            if x1.find('#NAME') != -1:
                if x.lower().find(search.lower()) != -1:
                    if x.find('eeee0000') != -1:
                        return file
                        break

    def SaveTrasponderService():
        TrasponderListOldLamedb = open(Directory + '/NGsetting/Temp/TrasponderListOldLamedb', 'w')
        ServiceListOldLamedb = open(Directory + '/NGsetting/Temp/ServiceListOldLamedb', 'w')
        Trasponder = False
        inTransponder = False
        inService = False
        try:
            LamedbFile = open('/etc/enigma2/lamedb', 'r')
            while 1:
                line = LamedbFile.readline()
                if not line:
                    break
                if not (inTransponder or inService):
                    if line.find('transponders') == 0:
                        inTransponder = True
                    if line.find('services') == 0:
                        inService = True
                if line.find('end') == 0:
                    inTransponder = False
                    inService = False
                line = line.lower()
                if line.find('eeee0000') != -1:
                    Trasponder = True
                    if inTransponder:
                        TrasponderListOldLamedb.write(line)
                        line = LamedbFile.readline()
                        TrasponderListOldLamedb.write(line)
                        line = LamedbFile.readline()
                        TrasponderListOldLamedb.write(line)
                    if inService:
                        tmp = line.split(':')
                        ServiceListOldLamedb.write(tmp[0] + ':' + tmp[1] + ':' + tmp[2] + ':' + tmp[3] + ':' + tmp[4] + ':0\n')
                        line = LamedbFile.readline()
                        ServiceListOldLamedb.write(line)
                        line = LamedbFile.readline()
                        ServiceListOldLamedb.write(line)
            TrasponderListOldLamedb.close()
            ServiceListOldLamedb.close()
            if not Trasponder:
                os.system('rm -fr ' + Directory + '/NGsetting/Temp/TrasponderListOldLamedb')
                os.system('rm -fr ' + Directory + '/NGsetting/Temp/ServiceListOldLamedb')
        except:
            pass
        return Trasponder

    def CreateBouquetForce():
        WritingBouquetTemporary = open(Directory + '/NGsetting/Temp/TerrestrialChannelListArchive', 'w')
        WritingBouquetTemporary.write('#NAME terrestre\n')
        ReadingTempServicelist = open(Directory + '/NGsetting/Temp/ServiceListOldLamedb', 'r').readlines()
        for jx in ReadingTempServicelist:
            if jx.find('eeee') != -1:
                String = jx.split(':')
                WritingBouquetTemporary.write('#SERVICE 1:0:%s:%s:%s:%s:%s:0:0:0:\n' % (hex(int(String[4]))[2:], String[0], String[2], String[3], String[1]))
        WritingBouquetTemporary.close()

    def SaveBouquetTerrestrial():
        NameDirectory = ResearchBouquetTerrestrial('terr')
        if not NameDirectory:
            NameDirectory = ForceSearchBouquetTerrestrial()
        try:
            shutil.copyfile(NameDirectory, Directory + '/NGsetting/Temp/TerrestrialChannelListArchive')
            return True
        except:
            pass
    Service = SaveTrasponderService()
    if Service:
        if not SaveBouquetTerrestrial():
            CreateBouquetForce()
        return True

def TransferBouquetTerrestrialFinal():

    def RestoreTerrestrial():
        for file in os.listdir('/etc/enigma2/'):
            if re.search('^userbouquet.*.tv', file):
                f = open('/etc/enigma2/' + file, 'r')
                x = f.read()
                if re.search('#NAME Digitale Terrestre', x, flags=re.IGNORECASE):
                    return '/etc/enigma2/' + file
    try:
        TerrestrialChannelListArchive = open(Directory + '/NGsetting/Temp/TerrestrialChannelListArchive').readlines()
        DirectoryUserBouquetTerrestrial = RestoreTerrestrial()
        if DirectoryUserBouquetTerrestrial:
            TrasfBouq = open(DirectoryUserBouquetTerrestrial, 'w')
            for Line in TerrestrialChannelListArchive:
                if Line.lower().find('#name') != -1:
                    TrasfBouq.write('#NAME Digitale Terrestre\n')
                else:
                    TrasfBouq.write(Line)
            TrasfBouq.close()
            return True
    except:
        return False

def SearchIPTV():
    iptv_list = []
    for iptv_file in sorted(glob.glob('/etc/enigma2/userbouquet.*.tv')):
        usbq = open(iptv_file, 'r').read()
        usbq_lines = usbq.strip().lower()
        if 'http' in usbq_lines:
            iptv_list.append(os.path.basename(iptv_file))
    if not iptv_list:
        return False
    else:
        return iptv_list

def StartProcess(link, type, Personal):
    def LamedbRestore():
        try:
            TrasponderListNewLamedb = open(Directory + '/NGsetting/Temp/TrasponderListNewLamedb', 'w')
            ServiceListNewLamedb = open(Directory + '/NGsetting/Temp/ServiceListNewLamedb', 'w')
            inTransponder = False
            inService = False
            infile = open('/etc/enigma2/lamedb', 'r')
            while 1:
                line = infile.readline()
                if not line:
                    break
                if not (inTransponder or inService):
                    if line.find('transponders') == 0:
                        inTransponder = True
                    if line.find('services') == 0:
                        inService = True
                if line.find('end') == 0:
                    inTransponder = False
                    inService = False
                if inTransponder:
                    TrasponderListNewLamedb.write(line)
                if inService:
                    ServiceListNewLamedb.write(line)
            TrasponderListNewLamedb.close()
            ServiceListNewLamedb.close()
            WritingLamedbFinal = open('/etc/enigma2/lamedb', 'w')
            WritingLamedbFinal.write('eDVB services /4/\n')
            TrasponderListNewLamedb = open(Directory + '/NGsetting/Temp/TrasponderListNewLamedb', 'r').readlines()
            for x in TrasponderListNewLamedb:
                WritingLamedbFinal.write(x)
            try:
                TrasponderListOldLamedb = open(Directory + '/NGsetting/Temp/TrasponderListOldLamedb', 'r').readlines()
                for x in TrasponderListOldLamedb:
                    WritingLamedbFinal.write(x)
            except:
                pass
            WritingLamedbFinal.write('end\n')
            ServiceListNewLamedb = open(Directory + '/NGsetting/Temp/ServiceListNewLamedb', 'r').readlines()
            for x in ServiceListNewLamedb:
                WritingLamedbFinal.write(x)
            try:
                ServiceListOldLamedb = open(Directory + '/NGsetting/Temp/ServiceListOldLamedb', 'r').readlines()
                for x in ServiceListOldLamedb:
                    WritingLamedbFinal.write(x)
            except:
                pass
            WritingLamedbFinal.write('end\n')
            WritingLamedbFinal.close()
            return True
        except:
            return False

    def DownloadSettingAgg(link):
        dir = Directory + '/NGsetting/Temp/listaE2.zip'
        try:
            if py_version == 2:
                req = Request(link)
                req.add_header('User-Agent',"VAS14")
                response = urlopen(req)
                link = response.read()
                response.close()
                Setting = open(dir, 'w')
                Setting.write(link)
                Setting.close()
            else:
                url_zip = get(link)
                with open(dir, 'wb') as f:
                    f.write(url_zip.content)
            if os.path.exists(dir):
                import zipfile
                if not os.path.exists(Directory + '/NGsetting/Temp/setting'):
                    os.system('mkdir ' + Directory + '/NGsetting/Temp/setting')
                image_zip = zipfile.ZipFile(Directory + '/NGsetting/Temp/listaE2.zip')
                image_zip.extractall(Directory + '/NGsetting/Temp/setting')
                if not os.path.exists(Directory + '/NGsetting/Temp/enigma2'):
                    os.system('mkdir ' + Directory + '/NGsetting/Temp/enigma2')
                dir_setting = os.listdir('/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/Temp/setting/')
                name_setting = dir_setting[0]
                dir_name = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/Temp/setting/' + name_setting
                destination = '/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/Temp/enigma2'
                for filename in glob.glob(os.path.join(dir_name, '*')):
                    shutil.copy(filename, destination)
                if os.path.exists(Directory + '/NGsetting/Temp/enigma2/lamedb'):
                    return True
            return False
        except:
            return

    def SaveList(list):
        jw = open('/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/SelectBack', 'w')
        for dir, name in list:
            jw.write(dir + '---' + name + '\n')
        jw.close()

    def SavePersonalSetting():
        try:
            os.system('mkdir ' + Directory + '/NGsetting/SelectFolder')
            jw = open('/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/Select')
            jjw = jw.readlines()
            jw.close()
            count = 1
            list = []
            for x in jjw:
                try:
                    jx = x.split('---')
                    newfile = 'userbouquet.NgSetting' + str(count) + '.tv'
                    os.system('cp /etc/enigma2/' + jx[0] + ' /' + Directory + '/NGsetting/SelectFolder/' + newfile)
                    list.append((newfile, jx[1]))
                    count = count + 1
                except:
                    pass
            SaveList(list)
        except:
            return
        return True

    def TransferPersonalSetting():
        try:
            jw = open('/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/SelectBack')
            jjw = jw.readlines()
            jw.close()
            for x in jjw:
                try:
                    jx = x.split('---')
                    os.system('cp -rf ' + Directory + '/NGsetting/SelectFolder/' + jx[0] + '  /etc/enigma2/')
                except:
                    pass
        except:
            pass
        return True

    def CreateUserbouquetPersonalSetting():
        try:
            jw = open('/usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/SelectBack', 'r')
            jjw = jw.readlines()
            jw.close()
        except:
            pass
        jRewriteBouquet = open('/etc/enigma2/bouquets.tv', 'r')
        RewriteBouquet = jRewriteBouquet.readlines()
        jRewriteBouquet.close()
        WriteBouquet = open('/etc/enigma2/bouquets.tv', 'w')
        Counter = 0
        for xx in RewriteBouquet:
            if Counter == 1:
                for x in jjw:
                    if x[0].strip() != '':
                        try:
                            jx = x.split('---')
                            WriteBouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + jx[0].strip() + '" ORDER BY bouquet\n')
                        except:
                            pass
                WriteBouquet.write(xx)
            else:
                WriteBouquet.write(xx)
            Counter = Counter + 1
        WriteBouquet.close()

    def KeepIPTV():
        iptv_to_save = SearchIPTV()
        if iptv_to_save:
            for iptv in iptv_to_save:
                os.system('cp -rf /etc/enigma2/' + iptv + ' ' + Directory + '/NGsetting/Temp/enigma2/' + iptv)

    def TransferNewSetting():
        try:
            KeepIPTV()
            os.system('rm -rf /etc/enigma2/lamedb')
            os.system('rm -rf /etc/enigma2/*.radio')
            os.system('rm -rf /etc/enigma2/*.tv')
            os.system('cp -rf ' + Directory + '/NGsetting/Temp/enigma2/*.tv /etc/enigma2/')
            os.system('cp -rf ' + Directory + '/NGsetting/Temp/enigma2/*.radio /etc/enigma2/')
            os.system('cp -rf ' + Directory + '/NGsetting/Temp/enigma2/lamedb /etc/enigma2/')
            if not os.path.exists('/etc/enigma2/blacklist'):
                os.system('cp -rf ' + Directory + '/NGsetting/Temp/enigma2/blacklist /etc/enigma2/')
            if not os.path.exists('/etc/enigma2/whitelist'):
                os.system('cp -rf ' + Directory + '/NGsetting/Temp/enigma2/whitelist /etc/enigma2/')
            os.system('cp -rf ' + Directory + '/NGsetting/Temp/enigma2/satellites.xml /etc/tuxbox/')
        except:
            return
        return True

    Status = True
    if int(type) == 1:
        SavingProcessTerrestrialChannels = StartSavingTerrestrialChannels()
        os.system('cp -r /etc/enigma2/ ' + Directory + '/NGsetting/enigma2')
    if not DownloadSettingAgg(link):
        os.system('cp ' + Directory + '/NGsetting/enigma2/* /etc/enigma2')
        os.system('rm -rf ' + Directory + '/NGsetting/enigma2')
        Status = False
    else:
        personalsetting = False
        if int(Personal) == 1:
            personalsetting = SavePersonalSetting()
        if TransferNewSetting():
            if personalsetting:
                if TransferPersonalSetting():
                    CreateUserbouquetPersonalSetting()
                    os.system('rm -rf ' + Directory + '/NGsetting/SelectFolder')
                    os.system('mv /usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/SelectBack /usr/lib/enigma2/python/Plugins/Extensions/NGsetting/Moduli/NGsetting/Select')
            os.system('rm -rf ' + Directory + '/NGsetting/enigma2')
        else:
            os.system('cp ' + Directory + '/NGsetting/enigma2/* /etc/enigma2')
            os.system('rm -rf ' + Directory + '/NGsetting/Temp/*')
            Status = False
        if int(type) == 1 and Status:
            if SavingProcessTerrestrialChannels:
                if LamedbRestore():
                    TransferBouquetTerrestrialFinal()
    return Status

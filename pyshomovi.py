#!/usr/bin/env python3

import time
import re
import operator
import pip
import os
import platform
from optparse import OptionParser
import multiprocessing
pip.main(['install','--upgrade', '--quiet', 'shodan'])
import shodan
try:
  import progressbar
except ImportError:
  pip.main(['install', '--quiet', 'progressbar2'])
  import progressbar
try:
  from uritools import uricompose
except ImportError:
  pip.main(['install', '--quiet', 'uritools'])
  from uritools import uricompose
try:
  from urllib3 import PoolManager
except ImportError:
  pip.main(['install', '--quiet', 'urllib3'])
  from urllib3 import PoolManager
try:
  from pymediainfo import MediaInfo
except ImportError:
  pip.main(['install', '--quiet', 'pymediainfo'])
  from pymediainfo import MediaInfo

usage = 'usage: %prog --file FILE --shodan API --list LIST'
parser = OptionParser(usage = usage)
parser.add_option('-s', '--shodan', dest = 'shodanapi', default = 'X2H3GH8nfdDjoG5PqPfZrmA8g7oTaWFT', help = 'tu shodan API', metavar = 'API')
parser.add_option('-f', '--file', dest = 'filename', default = 'MOVISTAR+IPs.txt', help = 'escribe las ip al archivo especificado', metavar = 'FILE')
parser.add_option('-l', '--list', dest = 'listname', default = 'MOVISTAR+.m3u', help = 'escribe la lista m3u al archivo especificado', metavar = 'LIST')
(options, args) = parser.parse_args()

try:
  shodanapi = shodan.Shodan(options.shodanapi)
  if not shodanapi.api_key:
    raise shodan.APIError('Introduce tu Shodan API')
except shodan.APIError as e:
  print('ShodanError: %s' % (e))
  parser.print_help()
  raise SystemExit(1)

if ((platform.system() == 'Windows') and not (os.path.exists('C:\\Windows\\System32\\MediaInfo.dll'))):
  print('Instala MediaInfo.dll en C:\Windows\system32\MediaInfo.dll ..')
  raise SystemExit(1)
elif ((platform.system() == 'Linux') and not (os.popen('ldconfig -p | grep "mediainfo"').read())):
  print('Instala libmediainfo ..')
  raise SystemExit(1)

channels = {1:{'id':'MV3','name':'MOVISTAR+ #0', 'path':'1:0:1:7478:3F0:1:C00000:0:0:0:'},
  2:{'id':'MV1','name':'MOVISTAR+ ESTRENOS', 'path':'1:0:1:76C0:40E:1:C00000:0:0:0:'},
  3:{'id':'CPACCI','name':'MOVISTAR+ ACCIÓN','path':'1:0:1:746C:3F0:1:C00000:0:0:0:'},
  4:{'id':'CPCOLE','name':'MOVISTAR+ DCINE','path':'1:0:1:746E:3F0:1:C00000:0:0:0:'},
  5:{'id':'CPCOME','name':'MOVISTAR+ COMEDIA','path':'1:0:1:746D:3F0:1:C00000:0:0:0:'},
  6:{'id':'CPXTRA','name':'MOVISTAR+ XTRA','path':'1:0:1:77C6:40A:1:C00000:0:0:0:'},
  7:{'id':'CPSER','name':'MOVISTAR+ SERIES','path':'1:0:1:7696:41E:1:C00000:0:0:0:'},
  8:{'id':'DCESP','name':'CINE Ñ','path':'1:0:1:7736:416:1:C00000:0:0:0:'},
  9:{'id':'TCM','name':'TCM','path':'1:0:1:76C7:40E:1:C00000:0:0:0:'},
  10:{'id':'HOLLYW','name':'HOLLYWOOD','path':'1:0:1:77C1:40A:1:C00000:0:0:0:'},
  11:{'id':'FOXGE','name':'FOX','path':'1:0:1:746F:3F0:1:C00000:0:0:0:'},
  12:{'id':'FOXCR','name':'FOX LIFE','path':'1:0:1:7468:3F0:1:C00000:0:0:0:'},
  13:{'id':'PARCH','name':'PARAMOUNT','path':'1:0:1:75F9:408:1:C00000:0:0:0:'},
  14:{'id':'AXN','name':'AXN','path':'1:0:1:7477:3F0:1:C00000:0:0:0:'},
  15:{'id':'SET','name':'AXN WHITE','path':'1:0:1:7471:3F0:1:C00000:0:0:0:'},
  16:{'id':'PCM','name':'COMEDY CENTRAL','path':'1:0:1:76C8:40E:1:C00000:0:0:0:'},
  17:{'id':'COSMO','name':'COSMO','path':'1:0:1:7730:416:1:C00000:0:0:0:'},
  18:{'id':'TNT','name':'TNT','path':'1:0:1:77C9:40A:1:C00000:0:0:0:'},
  19:{'id':'SCI-FI','name':'SYFY','path':'1:0:1:7796:424:1:C00000:0:0:0:'},
  20:{'id':'CL13','name':'CALLE 13','path':'1:0:1:7790:424:1:C00000:0:0:0:'},
  21:{'id':'AMC','name':'AMC','path':'1:0:1:76CF:40E:1:C00000:0:0:0:'},
  22:{'id':'CPPART','name':'MOVISTAR+ PARTIDAZO','path':'1:0:1:769C:41E:1:C00000:0:0:0:'},
  23:{'id':'LIGA','name':'LA LIGA TV','path':'1:0:1:7793:424:1:C00000:0:0:0:'},
  24:{'id':'BELIGA','name':'BEIN LALIGA','path':'1:0:1:7797:424:1:C00000:0:0:0:'},
  25:{'id':'BELIG1','name':'BEIN LALIGA1','path':'1:0:1:756B:412:1:C00000:0:0:0:'},
  26:{'id':'BELIG2','name':'BEIN LALIGA2','path':'1:0:1:7580:412:1:C00000:0:0:0:'},
  27:{'id':'CHUEFA','name':'BEIN SPORT','path':'1:0:1:757B:412:1:C00000:0:0:0:'},
  28:{'id':'BEMAX1','name':'BEIN MAX1','path':'1:0:1:757B:412:1:C00000:0:0:0:'},
  29:{'id':'GOL','name':'GOL','path':'1:0:1:74A3:41C:1:C00000:0:0:0:'},
  30:{'id':'CPFUT','name':'MOVISTAR FÚTBOL','path':'1:0:1:778E:424:1:C00000:0:0:0:'},
  31:{'id':'GOLF+','name':'MOVISTAR GOLF','path':'1:0:1:7789:424:1:C00000:0:0:0:'},
  32:{'id':'MVF1','name':'MOVISTAR FORMULA1','path':'1:0:1:74A4:41C:1:C00000:0:0:0:'},
  33:{'id':'MVMTGP','name':'MOVISTAR MOTOGP','path':'1:0:1:7739:416:1:C00000:0:0:0:'},
  34:{'id':'CPDEP','name':'MOVISTAR DEPORTES1','path':'1:0:1:778F:424:1:C00000:0:0:0:'},
  35:{'id':'CPD2','name':'MOVISTAR DEPORTES2','path':'1:0:1:760C:408:1:C00000:0:0:0:'},
  36:{'id':'ESP','name':'EUROSPORT 1','path':'1:0:1:74A1:41C:1:C00000:0:0:0:'},
  37:{'id':'ESP2','name':'EUROSPORT 2','path':'1:0:1:760E:408:1:C00000:0:0:0:'},
  38:{'id':'NATGEO','name':'NATIONAL GEOGRAPHIC','path':'1:0:1:778D:424:1:C00000:0:0:0:'},
  39:{'id':'CLASSD','name':'CLASSICA','path':'1:0:1:7602:408:1:C00000:0:0:0:'},
  40:{'id':'MEZZO','name':'MEZZO','path':'1:0:1:7699:41E:1:C00000:0:0:0:'},
  41:{'id':'MTV','name':'MTV','path':'1:0:1:74A2:41C:1:C00000:0:0:0:'},
  42:{'id':'40TV','name':'40TV','path':'1:0:1:76C5:40E:1:C00000:0:0:0:'},
  43:{'id':'TVE','name':'LA 1','path':'1:0:1:77C0:40A:1:C00000:0:0:0:'},
  44:{'id':'LA2','name':'LA 2','path':'1:0:1:77C2:40A:1:C00000:0:0:0:'},
  45:{'id':'A3','name':'ANTENA 3','path':'1:0:1:7604:408:1:C00000:0:0:0:'},
  46:{'id':'C4','name':'CUATRO','path':'1:0:1:77C7:40A:1:C00000:0:0:0:'},
  47:{'id':'T5','name':'TELECINCO','path':'1:0:1:77C3:40A:1:C00000:0:0:0:'},
  48:{'id':'FDFIC','name':'FDF','path':'1:0:1:77BC:40A:1:C00000:0:0:0:'},
  49:{'id':'SEXTA','name':'LA SEXTA','path':'1:0:1:77BF:40A:1:C00000:0:0:0:'},
  50:{'id':'BOING','name':'BOING','path':'1:0:1:749E:41C:1:C00000:0:0:0:'},
  51:{'id':'CLANTV','name':'CLAN TV','path':'1:0:1:77BE:40A:1:C00000:0:0:0:'},
  52:{'id':'DCH','name':'DISNEY CHANNEL','path':'1:0:1:76C3:40E:1:C00000:0:0:0:'}}

def ipm3ucheck():
  try:
    with open(options.listname, 'r+') as file:
      for line in file.readlines():
        ip = (re.findall(r'[0-9]+(?:\.[0-9]{1,3}){3}', line))
        if ip:
          speed = func_timeout(17, ipcheckspeed, args=([(ip)]))
          if speed:
            print('%s actualizada con IP = %s a %d KB/s' % (options.listname, str(ip).strip("['']"), speed))
            raise SystemExit(0)
  except IOError:
    pass
  return None

def ipreadfile():
  iplist = []
  localtime = time.asctime(time.localtime(time.time()))
  try:
    with open(options.filename, 'r+') as file:
      for line in file.readlines():
        ip = (re.findall(r'[0-9]+(?:\.[0-9]{1,3}){3}', line))
        if ip:
          iplist.append(str(ip).strip("['']"))
  except IOError:
    pass
  with open(options.filename, 'w') as file:
    file.write('%s\n' % (localtime))
    file.write(('*' * 40) + ('\n') + ('*' * 40) + ('\n'))
  return iplist

def ipshodansearch():
  company = {1:{'org':'Orange Espana', 'name':'ORANGE'},
    2:{'org':'Telefonica de Espana', 'name':'TELEFÓNICA'},
    3:{'org':'Jazz Telecom S.A.', 'name':'JAZZTEL'},
    4:{'org':'Vodafone Ono','name':'ONO'},
    5:{'org':'Vodafone Spain','name':'VODAFONE'}}
  serverversion = ['TwistedWeb', 'TwistedWeb/8.2.0', 'TwistedWeb/12.0.0',
    'TwistedWeb/13.2.0', 'TwistedWeb/14.0.2', 'TwistedWeb/16.4.0']
  ipshodanlist =[]
  for org in company.values():
    for server in serverversion:
      try:
        results = shodanapi.search("%s 200 ok org:'%s'" % (server, org['org']))
      except shodan.APIError as e:
        print('ShodanError: %s' % (e))
      else:
        for result in results['matches']:
          ipshodanlist.append(result['ip_str'])
  return ipshodanlist

def ipcheckips(ipmainlist):
  count = 0
  ipfounddict = {}
  bar = progressbar.ProgressBar(redirect_stdout=True, widgets=[ '[', progressbar.SimpleProgress(), '] ',
    progressbar.Bar(), ' (', progressbar.ETA(), ') ' ])
  for ip in bar(ipmainlist):
    found = False
    for item in ipfounddict.values():
      if ip in item['ip']:
        found = True
    if not found:
      speed = func_timeout(17, ipcheckspeed, args=([(ip)]), ipfounddict=ipfounddict)
      if speed:
        count += 1
        ipfounddict[count] = {'ip' : str(ip).strip("['']"), 'speed' : speed}
        ipwrite(ipfounddict, count)
        print('[%d] IP = %s  STREAM = ~%d KB/s' % (count, str(ip).strip("['']"), speed))
  return ipfounddict

def ipcheckspeed(ip):
  url = uricompose(scheme='http', host='%s' % (str(ip).strip("['']")),
    port='8001', path='/%s' % (channels[1]['path']))
  http = PoolManager(timeout = 2, retries=0)
  try:
    response = http.request('GET', url, preload_content=False)
    start = time.time()
    bytestream0 = (response.read(5242880))
    stop = time.time()
    response.close()
  except:
    return None
  else:
    if (len(bytestream0) == 5242880):
      channel0HasVideoAudio = checkVideoAudio(bytestream0)
      if channel0HasVideoAudio:
        try:
          url = uricompose(scheme='http', host='%s' % (str(ip).strip("['']")),
            port='8001', path='/%s' % (channels[24]['path']))
          http = PoolManager(timeout = 2, retries=0)
          response = http.request('GET', url, preload_content=False)
          bytestream24 = (response.read(512000))
          response.close()
          if (len(bytestream24) == 512000):
            channel24HasVideoAudio = checkVideoAudio(bytestream24)
            if channel24HasVideoAudio:
              speed = (int((len(bytestream0) / 1024) / (stop - start)))
              return speed
            else:
              return None
        except:
          return None

def checkVideoAudio(bytestream):
  try:
    with open('video', 'wb') as file:
      file.write(bytestream)
    mediaInfo = MediaInfo.parse(file.name)
    os.remove(file.name)
    if (mediaInfo.tracks[0].frame_count):
      return True
    else:
      return False
  except OSError as e:
    os.remove(file.name)
    print('MediaInfo: %s' % (e))
    raise SystemExit(1)
  except IOError as e:
    print('IOError: %s' % (e))
    raise SystemExit(1)

def ipwrite(ipfounddict, index):
  try:
    with open(options.filename, 'a') as file:
        file.write('[%d]  IP = %s  STREAM = %d KB/s\n' % (index, str(ipfounddict[index]['ip']).strip("['']"), ipfounddict[index]['speed']))
  except IOError as e:
    print('IOError: %s' % (e))
    raise SystemExit(1)
  return None

def ipbeststream(ipfounddict):
  indexspeed = {}
  for line in ipfounddict.items():
    indexspeed[line[0]] = line[1]['speed']
  speedlist = sorted(indexspeed.items(), key=operator.itemgetter(1), reverse=True)
  return speedlist[0][0]

def dom3u(ipfounddict, choose):
  try:
    with open(options.listname, 'w') as list:
      list.flush()
      list.write('#EXTM3U tvg-shift=3\n#EXTVLCOPT--http-reconnect=true\n')
    with open(options.listname,'a') as list:
      for channel in channels.values():
        list.write('\n#EXTINF:-1 tvg-id="%s" tvg-logo="" tvg-name="" group-title="",%s\n' % (channel['id'], channel['name']))
        list.write(uricompose(scheme='http', host='%s' % (str(ipfounddict['ip']).strip("['']")), port='8001', path='/%s' % (channel['path'])))
        list.write('\n')
    print('%s creada con [%d]' % (options.listname, choose))
  except IOError as e:
    print('IOError: %s' % (e))
    raise SystemExit(1)
  return None

def func_timeout(timeout, func, args = (), kwds = {}, default = None, ipfounddict = {}):
  pool = multiprocessing.Pool(processes = 1)
  result = pool.apply_async(func, args = args, kwds = kwds)
  try:
    val = result.get(timeout = timeout)
  except multiprocessing.TimeoutError:
    pool.terminate()
    pool.join()
    return default
  except KeyboardInterrupt:
    pool.terminate()
    pool.join()
    if (len(ipfounddict) > 0):
      choose = ipbeststream(ipfounddict)
      dom3u(ipfounddict[choose], choose)
    raise SystemExit(0)
  else:
    pool.close()
    pool.join()
    return val

if __name__ == '__main__':
  multiprocessing.freeze_support()
  ipmainlist = []
  ipm3ucheck()
  ipfilelist = ipreadfile()
  for ip in ipfilelist:
    ipmainlist.append(ip)
  ipshodanlist = ipshodansearch()
  for ip in ipshodanlist:
    ipmainlist.append(ip)
  print('Comprobando %d IPs [%d desde %s] y [%d desde Shodan] ...' % (
    len(ipmainlist), len(ipfilelist), options.filename, len(ipshodanlist)))
  ipfounddict = ipcheckips(ipmainlist)
  if (len(ipfounddict) > 0):
    choose = ipbeststream(ipfounddict)
    dom3u(ipfounddict[choose], choose)
  raise SystemExit(0)

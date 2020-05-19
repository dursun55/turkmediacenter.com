#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, re, sys, os, random
import xbmcplugin, xbmcgui
import xbmcaddon
import xbmc
import codecs
Addon = xbmcaddon.Addon( id = 'plugin.video.TMCVOD' )
_ADDON_PATH =   xbmc.translatePath(Addon.getAddonInfo('path'))
sys.path.append( os.path.join( _ADDON_PATH, 'resources', 'lib'))
addon_id = Addon.getAddonInfo('id')
from BeautifulSoup import BeautifulStoneSoup, MinimalSoup
from urllib import unquote_plus
from demjson3 import loads
import socket
import time
import imp
    
hos = int(sys.argv[1])
xbmcplugin.setContent(hos, 'movies')
busystring = xbmc.getLocalizedString(503).encode("utf8")
fanart  = _ADDON_PATH + '/fanart.jpg'
set_png = 'https://i.hizliresim.com/omoxit.png'
left = _ADDON_PATH + '/left.png'
right = _ADDON_PATH + '/right.png'
addon_icon = _ADDON_PATH + '/icon.png'
addon_v = Addon.getAddonInfo('version')
xbmc_headers = {'User-Agent':'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6'}
settings = xbmcaddon.Addon(id='plugin.video.TMCVOD')
username = settings.getSetting( "username" )
password = settings.getSetting( "userpassword" )
def write_mac():
    mac_settings = Addon.getSetting('mac')
    print mac_settings
    if mac_settings == "":   
        mac_address = xbmc.getInfoLabel('Network.MacAddress')
        i = 1
        while mac_address == busystring:
            print "while: %s" % i
            i = i+1
            mac_address = xbmc.getInfoLabel('Network.MacAddress') 
            time.sleep(1)
            if i == 10:
                break
        Addon.setSetting('mac', mac_address)
def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
		

		
def Categories(params):

    start = 'http://tmcwebcenter.com/tmc3.php'	

    try:
        url = urllib.unquote(params['link'])
    except Exception as ex:
        print 'error link = ', ex
        url = start
    try:
        req = urllib2.Request(url, None, xbmc_headers)
        http = urllib2.urlopen(req).read()
    except Exception as ex:
        print 'urllib2 error -> ' , ex
    http = http.replace('&nbsp;', ' ').replace('&amp;', '&')
    #print '==http==' + http
    if http != None and http != '':
        if http.find('#EXT') > -1:
            m3u(http)
        elif http.find('TUT') > -1: 
            Adult(http)			
        else:
            xml = BeautifulStoneSoup(http)
            n = 0
            playlist(xml)
    if url == start :
        uri = construct_request({
            'func': 'settings'
            })
        listitem=xbmcgui.ListItem('[COLOR FF00FFFF]Ayarlar[/COLOR]', iconImage = set_png)
        listitem.setInfo(type = 'settings', infoLabels={})
        if Addon.getSetting('fanart') == '0':		
            listitem.setProperty('fanart_image', set_png)
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    if Addon.getSetting('list') == '0':
        xbmc.executebuiltin('Container.SetViewMode(504)')
    if Addon.getSetting('list') == '1':
        xbmc.executebuiltin('Container.SetViewMode(500)')
    if Addon.getSetting('list') == '2':
        xbmc.executebuiltin('Container.SetViewMode(503)')
    if Addon.getSetting('list') == '3':
        xbmc.executebuiltin('Container.SetViewMode(515)')
    if Addon.getSetting('list') == '4':
        xbmc.executebuiltin('Container.SetViewMode(501)')
    xbmcplugin.endOfDirectory(hos)
	
def playlist(xml):
    n = 0
    link = None
    stream = None
    prev_title = ''
    next_title = ''
    construkt = {}
    prev_page_element = xml.find('prev_page_url')
    if prev_page_element:
        prev_url = prev_page_element.text.encode('utf-8')
        prev_page_text = prev_page_element.get('text')
        if prev_page_text:
            prev_page_text = prev_page_text.encode('utf-8')
            prev_title =  "[COLOR FF00FFFF]<-" + prev_page_text +'[/COLOR]'
            uri = construct_request({
                 'func': 'Categories',
                 'link':prev_url
                 })
            listitem=xbmcgui.ListItem(prev_title, left, left)
            if Addon.getSetting('fanart') == '0':			
                listitem.setProperty('Fanart_Image', left)
            xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    next_page_element = xml.find('next_page_url')
    if next_page_element:
        next_url = next_page_element.text.encode('utf-8')
        next_page_text = next_page_element.get('text')
        if next_page_text:
            next_page_text = next_page_text.encode('utf-8')
            next_title =  "[COLOR FF00FFFF]->" + next_page_text +'[/COLOR]'
            uri = construct_request({
                'func': 'Categories',
                'link':next_url
                })
            listitem=xbmcgui.ListItem(next_title, right, right)
            if Addon.getSetting('fanart') == '0':			
                listitem.setProperty('fanart_image', right)
            xbmcplugin.addDirectoryItem(hos, uri, listitem, True)

    for channel in xml.findAll('channel'):
        img_src = ''
        img_logo = ''
        description = ''
        titl = ''
        YaID = ''
        title = channel.find('title').text.encode('utf-8')
        title = title.replace('&', ' and ')
        title = re.compile('<[\\/\\!]*?[^<>]*?>').sub('', title)
        description = channel.find('description')
        if description:
            description = description.text.encode('utf-8')
            img_src_list = re.findall('src="(.*?)"', description) or re.findall("src='(.*?)'", description)
            if len(img_src_list) > 0:
                img_src = img_src_list[0]
            if img_src == None or img_src == '' or img_src.find('http') < 0 :
                img_src = fanart
            description = description.replace('<br>', '\n')
            description = description.replace('<br/>', '\n')
            description = description.replace('</h1>', '</h1>\n')
            description = description.replace('</h2>', '</h2>\n')
            description = description.replace('&nbsp;', ' ')
            description = re.compile('<[\\/\\!]*?[^<>]*?>').sub('', description)
        else:
            description = title
        if description == '':
            description = title
        piconname = channel.find('logo_30x30') or channel.find('logo')
        if piconname:
            img_logo = piconname.text
            if img_src == None or img_src == '' or img_src == fanart :
                img_src = img_logo

        n = n+1		
        stream_url = channel.find('stream_url')

        playlist_url = channel.find('playlist_url')
               
        if playlist_url:
            link = playlist_url.text.encode('utf-8')
            titl = "[COLOR FFFFFFFF]" + title + "[/COLOR]"
            
            construkt = {
                'func': 'Categories',
                'link': link
                }
                    
        if stream_url:
            stream = stream_url.text.encode('utf-8')
            titl = "[COLOR FF00FFFF]" + title + "[/COLOR]"
            
							
            construkt = {
                'func': 'Play',
                'stream': stream,
                'img': img_src,
                'title': title,
                'epgid': id
                }
                
        listitem=xbmcgui.ListItem(titl, iconImage = img_src, thumbnailImage = img_src)
        if Addon.getSetting('fanart') == '0':  		
            listitem.setProperty('fanart_image', img_src)
        listitem.setInfo(type = 'video', infoLabels={'title': titl, 'plot': description})
        uri = construct_request(construkt)
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)


def Adult(xml):

    if Addon.getSetting('adultPINonoff') == "0":
        keyboard = xbmc.Keyboard("", '[COLOR FF00FFFF]18 yasindan kucuklere burasi yasaktir.[/COLOR]',False)
        keyboard.doModal()
        if keyboard.isConfirmed():
                if ("12"==keyboard.getText()):		
                    dialog=xbmcgui.Dialog()

                else:
                      dialog=xbmcgui.Dialog()
                      dialog.ok("Error","Yanlis Sifre. Erisim reddedildi.")					
    try:
        url = urllib.unquote(params['link'])
        req = urllib2.Request(url, None, xbmc_headers)
        http = urllib2.urlopen(req).read()
    except Exception as ex:
        print 'urllib2 error -> ' , ex
    if ("12"==keyboard.getText()):

            xml = BeautifulStoneSoup(http)
            n = 0

            playlist(xml)

def m3u(xml):
    m3u = xml
    regex = re.findall('#EXTINF.*,(.*\\s)\\s*(.*)', m3u)
    if not len(regex) > 0:
        regex = re.findall('((.*.+)(.*))', m3u)
    for text in regex:
        img_src = ''
        description = ''
        YaID = ''
        id = ''
        title = text[0].strip()       
        title = "[COLOR FF00FFFF]" + title + "[/COLOR]"
        img_src = fanart
        if id != None:
            img_src = 'http://i.hizliresim.com/l3XX9r.png' % id   
        else:
            img_src = 'http://i.hizliresim.com/l3XX9r.png'
        url = text[1].strip()
        listitem=xbmcgui.ListItem(title, iconImage = img_src, thumbnailImage = img_src)
        if Addon.getSetting('fanart') == '0':		
            listitem.setProperty('fanart_image', fanart)
        listitem.setInfo(type = 'video', infoLabels={'title': title, 'plot': description})
        uri = construct_request({
            'func': 'Play',
            'title': title,
            'img': img_src,
            'stream': url,
            'epgid': id
            })
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
		
def settings(params):
    Addon.openSettings()
    return None

def Play(params):
    import urlresolver
    try:
        url = urllib.unquote(params['stream']).replace('&amp;', '&').replace(';', '')
    except:
        url = ''
        
    try:
        title = params['title']
    except:
        title = ''
    
    try:
        epgid = params['epgid']
    except:
        epgid = None
		
    try:
        img = params['img']
    except:
        img = None
		
    if "vk" in url:

	log_in='https://vk.com'	
        req = urllib2.Request(log_in)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0')
        req.add_header('Referer', log_in)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('name="login" id="quick_login_form" action=".*?">\s*<input type="hidden" name="act" value="([^"]+)".*?\s*.*?name="role" value="([^"]+)".*?\s*.*?id="quick_expire_input" value="".*?\s*.*?id="quick_recaptcha" value="".*?\s*.*?id="quick_captcha_sid" value="".*?\s*.*?id="quick_captcha_key" value="".*?\s*.*?name="_origin" value="([^"]+)".*?\s*.*?name="ip_h" value="([^"]+)".*?\s*.*?name="lg_h" value="([^"]+)"').findall(link)
        for act, role,_origin, ip_h, lg_h in match:
            log=('https://login.vk.com/?act='+act+'&role='+role+'&expire&recaptcha&captcha_sid&captcha_key&_origin='+_origin+'&ip_h='+ip_h+'&lg_h='+lg_h+'&email='+username+'&pass='+password)
			
        req = urllib2.Request(log)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        log_check=re.compile('parent.(onLoginDone).*?;').findall(link)
        if 'onLoginDone' in log_check:
            url= urlresolver.resolve(url)			
            xbmc.Player().play(url)
			
    elif "eporner" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)

    elif "xozilla" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	
		
    elif "katestube" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	
	
    elif "analdin" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	

    elif "xcafe.com" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	
			
    elif "porndoe" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	
			
    elif "pornwatchers" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	
			
    elif "vidmoly.to" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	
						
    elif "closeload" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	
									
    elif "uptostream" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	
			
    elif ".mp4" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)	

    elif "vidmoly.me" in url:
	url= url
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)		
				
    elif url:
	url= urlresolver.resolve(url)
	i = xbmcgui.ListItem(title)
	xbmc.Player().play(url, i)
	
	

    else:
        showMessage('Not playable stram', url, 2000)
		

		

def get_params(paramstring):
    param=[]
    if len(paramstring)>=2:
        params=paramstring
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    if len(param) > 0:
        for cur in param:
            param[cur] = urllib.unquote_plus(param[cur])
    return param

params = get_params(sys.argv[2])

if Addon.getSetting('mac') == None or Addon.getSetting('mac') == '':
	write_mac()	

if Addon.getSetting('requestTimeOut') != None and Addon.getSetting('requestTimeOut') != '':
    req_time = Addon.getSetting('requestTimeOut')
    if req_time == '0':
        sreq_time = 5
    elif req_time == '1':
        sreq_time = 10
    elif req_time == '2':
        sreq_time = 20
    else:
        sreq_time = 30
    
    socket.setdefaulttimeout(sreq_time)
else:
    socket.setdefaulttimeout(10)
    
try:
    func = params['func']
    del params['func']
except:
    func = None
    xbmc.log( '[%s]: Primary input' % addon_id, 1 )
    Categories(params)
    
if func != None:
    try: pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc:
        pfunc(params)



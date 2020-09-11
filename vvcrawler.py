#!/usr/bin/python3
#import argparse
from urllib.request import urlopen,urlretrieve
import urllib.parse
import os
from bs4 import BeautifulSoup
import re
from time import sleep
from colorama import init, Fore, Style
#---------------------------------------------------------------------------------
init(autoreset=True)
print(Fore.MAGENTA+Style.BRIGHT+r"""
     |
  /  |   \
 ;_/,L-,\_;     VIMP Video Crawler
\._/3  E\_./    
\_./(::)\._/
     ''
""")
while True:
    print("Pulse X en cualquier momento para salir")
    url=input(Fore.WHITE+'[+] Ingrese url de búsqueda: ')
    if url.upper()=='X':
        exit(0)
    if url.startswith('https') or url.startswith('http'):
        urlsplt = re.split('/+',url)
        hostname = urlsplt[0]+'//'+urlsplt[1]
    else:
        hostname = url.split('/')[0]
    try:
        req=urlopen(url)
    except Exception as ex:
        print(Fore.RED+'[!] Verifique que el URL esté correcto o revise su conexión')
        continue
    first_page = req.geturl()
    html = str(req.read())
    print(Fore.YELLOW+'[#] Buscando páginas...')
    link_pages=re.search('(?<=<!-- pages -->).*?(?=<!-- next page -->)',html,re.DOTALL)
    links_html = link_pages.group(0)
    soup =BeautifulSoup(links_html,'html.parser')
    tags = soup('a')
    links = list()
    links.insert(0,first_page)
    for tag in tags:
        links.append(tag.get('href',None))
    npages=len(links)
    print(Fore.CYAN+'[*] La busqueda cuenta con '+str(npages)+' páginas.')    
    for link in links:
        print(Fore.MAGENTA+'[#] Buscando videos en la página '+str(links.index(link)+1))
        try:
            req=urlopen(link)
        except Exception as ex:
            print(Fore.RED+'[!] Ha ocurrido un error buscando los videos:',ex)
            break
        html = req.read()
        soup = BeautifulSoup(html,'html.parser')
        tags = soup.find_all(attrs={"class":"mediaInfo"})
        for tag in tags:
            link = tag.a.get('href',None)
            link = link.split('/')
            video_hash = link[-1]
            video_link=hostname+'/getMedium/'+video_hash+'.m4v'
            title=link[2]
            if not os.path.exists(title):
                os.makedirs(title)
            try:
                print(Fore.YELLOW+'[#] Descargando '+title+'...')
                urllib.request.urlretrieve(video_link,title+'/'+title+'.m4v')
                print(Fore.GREEN+'[*] '+title+' descargado.')
                sleep(1)
            except Exception as ex:
                print(Fore.RED+'[!] Ha ocurrido un error descargando los videos:',ex)
                break
    print(Fore.CYAN+'[*] Todos los videos se han descargado satisfactoriamente.')

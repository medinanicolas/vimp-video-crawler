#!/usr/bin/python3
from urllib.request import urlopen, urlretrieve
import urllib.parse
import os, re, sys, argparse, random, string
from bs4 import BeautifulSoup
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
     ""
""")

argparser = argparse.ArgumentParser()
argparser.add_argument("-u", "--url", help="Search or video URL to download", metavar="URL", required=True)
argparser.add_argument("-o", "--out", help="Output directory", metavar="DIR")
args = argparser.parse_args()

def download(link):
    try:
        req = urlopen(link)
    except Exception as ex:
        print(Fore.RED+"[!] Ha ocurrido un error encontrando los videos:",ex)
        sys.exit()
    html = req.read()
    soup = BeautifulSoup(html,"html.parser")
    tags = soup.find_all(attrs={"class":"mediaInfo"})
    
    if not tags:
        print(Fore.RED+"[!] No se encontraron videos para descargar.")
        sys.exit() 

    for tag in tags:
        regex = "[a-z0-9]{32}"
        video_hash = re.search(regex, url)

        if video_hash:
            title = urlsplt[-2]
            video_hash = video_hash.group(0)
        else:
            link = tag.a.get("href", None)
            video_hash = re.search(regex, link).group(0)
            if not video_hash:
                print(Fore.RED+"[!] No se encontró el hash del video.")
                sys.exit()
            title=link.split("/")[-2]

        video_link = video_link = hostname+"/getMedium/"+video_hash+".m4v"

        if args.out:
            out = args.out
        else:
            out = title
        if not os.path.exists(out):
            os.makedirs(out)

        try:
            print(Fore.BLUE+"[#] Descargando "+title+"...")

            if os.path.exists(os.path.join(out, title+".m4v")):
                print(Fore.YELLOW+"[!] "+title+" ya existe, añadiendo carácteres aleatorios.")
                title += "_" + "".join(random.choice(string.ascii_letters + string.digits) for i in range(8))

            urllib.request.urlretrieve(video_link, out + "/" + title + ".m4v")
            print(Fore.GREEN+"[#] " + title + " descargado.")
            sleep(1)
        except Exception as ex:
            print(Fore.RED+"[!] Ha ocurrido un error descargando los videos:", ex)
            sys.exit()

url = args.url

if url[:5].lower() == "https" or url[:4].lower() == "http":
    urlsplt = re.split("/+", url)
    hostname = urlsplt[0]+"//"+urlsplt[1]
else:
    hostname = url.split("/")[0]
try:
    req = urlopen(url)
except Exception as ex:
    print(Fore.RED+"[!] Verifique que el URL esté correcto o revise su conexión")
    sys.exit()

first_page = req.geturl()

html = req.read().decode()

print(Fore.BLUE+"[#] Buscando páginas...")
link_pages = re.search("(?<=<!-- pages -->).*?(?=<!-- next page -->)", html, re.DOTALL)    

if link_pages:
    links_html = link_pages.group(0)
    soup = BeautifulSoup(links_html, "html.parser")
    tags = soup("a")

    links = [tag.get("href", None) for tag in tags]
    links.insert(0, first_page)

    print(Fore.BLUE+"[#] La busqueda cuenta con " + str(len(links)) + " páginas.")  
    

    for link in links:
        print(Fore.BLUE+"[#] Buscando videos en la página "+str(links.index(link)+1))
        download(link)
else:
    print(Fore.YELLOW+"[!] No se han encontrado páginas, intentando como video individual...")
    download(url)

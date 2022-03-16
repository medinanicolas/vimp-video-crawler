#!/usr/bin/python3
import os, re, sys, argparse, random, string
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
import asyncio, aiohttp, aiofiles
#---------------------------------------------------------------------------------
init(autoreset=True)
ascii_art = r"""
                                   _
       /      \         __      _\( )/_
    \  \  ,,  /  /   | /  \ |    /(O)\ 
     '-.`\()/`.-'   \_\\  //_/    _.._   _\(o)/_  //  \\
    .--_'(  )'_--.   .'/()\'.   .'    '.  /(_)\  _\\()//_
   / /` /`""`\ `\ \   \\  //   /   __   \       / //  \\ \
    |  |  ><  |  | VIMP     ,  |   ><   |  ,     | \__/ |
    \  \      /  / SCRAPPER. \  \      /  / .              _
   _    '.__.'    _\(O)/_   \_'--`(  )'--'_/     __     _\(_)/_
_\( )/_            /(_)\      .--'/()\'--.    | /  \ |   /(O)\
 /(O)\  //  \\     2022_     /  /` '' `\  \  \_\\  //_/
       _\\()//_     _\(_)/_    |        |      //()\\ 
 jgs  / //  \\ \     /(o)\      \      /       \\  //
       | \__/ |     VIMP VIDEO DOWNLADER
"""
print(Fore.MAGENTA+Style.BRIGHT+ascii_art)

argparser = argparse.ArgumentParser()
argparser.add_argument("-u", "--url", help="Search or video URL to download", metavar="URL", required=True)
argparser.add_argument("-o", "--out", help="Output directory", metavar="DIR")
args = argparser.parse_args()


async def get_urlinfo(url):
    if url[:5].lower() == "https" or url[:4].lower() == "http":
        urlsplt = re.split("/+", url)
        hostname = urlsplt[0]+"//"+urlsplt[1]
    else:
        hostname = url.split("/")[0]
    
    return hostname, urlsplt[-2]

async def search_pages(html):
    print(Fore.BLUE+"[#] Buscando páginas...")
    link_pages = re.search("(?<=<!-- pages -->).*?(?=<!-- next page -->)", html, re.DOTALL)
    try:
        return link_pages.group(0)
    except AttributeError as ex:
        return

async def do_soup(url, pages):
    soup = BeautifulSoup(pages, "html.parser")
    # link_tags = soup("a")

    links = [tag.get("href", None) for tag in soup("a")]
    links.insert(0, url)

    print(Fore.BLUE+"[#] La busqueda cuenta con " + str(len(links)) + " páginas.") 
    
    return links

async def get_videolink(link, session):
    async with session.get(link) as res:
        html = await res.text()
        soup =  BeautifulSoup(html, "html.parser")
        tag = soup.source
        link = tag["src"]
        fmt = tag["type"].split("/")[-1]
    return link, fmt

async def do_real_soup(url_info, session):
    link, url = url_info
    hostname, _ = await get_urlinfo(url)
    video_links = []

    async with session.get(link) as res:

        html = await res.text()
        soup = BeautifulSoup(html,"html.parser")
        tags = soup.find_all(attrs={"class":"mediaInfo"})

        if not tags:
            print(Fore.RED+"[!] No se encontraron videos para descargar.")
            sys.exit() 

        video_links_fmt = await asyncio.gather(*[asyncio.create_task(get_videolink(hostname + tag.a.get("href", None), session)) for tag in tags ])
        video_links = []
        for i,tup in enumerate(video_links_fmt):
            for tag in tags:
                video_links.append((tag.a.get("href", None).split("/")[-2],) + tup)
                video_links_fmt.pop(i)
                
    return video_links

async def download_file(video_info, session):

    video_link, out, title, fmt = video_info

    async with session.get(video_link) as res:

        if not os.path.exists(out):
            os.makedirs(out)
        try:
            print(Fore.BLUE+"[#] Descargando "+title+"...")

            if os.path.exists(os.path.join(out, title + "." + fmt)):
                print(Fore.YELLOW+"[!] "+title+" ya existe, añadiendo carácteres aleatorios.")
                title += "_" + "".join(random.choice(string.ascii_letters + string.digits) for i in range(8))

            async with aiofiles.open(os.path.join(out, title + "." + fmt), "wb") as video_file:
                async for data in res.content.iter_any():
                    await video_file.write(data)
            print(Fore.GREEN+"[#] " + title + " descargado.")

        except Exception as ex:
            print(Fore.RED+"[!] Ha ocurrido un error descargando los videos:", ex)
            sys.exit()

async def main():
    url = args.url
    out = args.out
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:

            html = await res.text()
            pages = await search_pages(html)

            tasks = []
            if pages:
                out = args.out
                page_links = await do_soup(url, pages)
                for link in page_links:
                    print(Fore.BLUE + "[#] Buscando videos en la página " + str(page_links.index(link)+1))
                    video_links = await do_real_soup([link, url], session)
                    for title, video_link, fmt in video_links:
                        if not args.out:
                            out = title
                        tasks.append(asyncio.create_task(download_file([video_link, out, title, fmt], session)))
                    await asyncio.gather(*tasks)
                   
            else:
                print(Fore.YELLOW+"[*] No se han encontrado páginas, intentando como fichero individual")
                _, title = await get_urlinfo(url)
                if not args.out:
                    out = title
                video_link, fmt = await get_videolink(url, session)
                await asyncio.create_task(download_file([video_link, out, title, fmt], session))

if __name__ == "__main__":
    asyncio.run(main())
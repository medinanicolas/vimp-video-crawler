# VVCrawler 🕷

_Vimp Video Crawler es una herramienta de web scraping para la descarga de archivos de video dentro de páginas que ocupen servicios VIMP_

_Está basada en expresiones regulares_
    
## Dependencias

* [Urllib](https://docs.python.org/3/library/urllib.html) - Librería python3
* [Bs4 (BeatifulSoup4)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Librería python3
* [Colorama](https://github.com/tartley/colorama) - Librería python3

# Uso
_vvcrawler se ejecuta mediante linea de comandos_

`$ python3 vvcrawler.py -u URL`

_Al ejecutarlo se debe establecer un enlace de búsqueda dentro de VIMP o un enlace de video individual_

_En caso de ser una búsqueda, la herramienta analizará todas las páginas de la búsqueda y procederá a descargar los videos_


![demo](demo/demo.gif)

## Licencia
[LICENCE](docs/LICENCE) - GNU General Public License v3.0 

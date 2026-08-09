# -*- coding: utf-8 -*-
import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# Otteniamo Handle e Base URL dall'avvio di Kodi
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def build_url(query):
    """Costruisce un URL compatibile con Kodi unendo la BASE_URL e i parametri."""
    return BASE_URL + '?' + urllib.parse.urlencode(query)

def show_main_menu():
    """Genera la schermata principale dell'addon."""

    # Voce 1: Cerca Film o Serie TV
    url_search = build_url({'action': 'search'})
    li_search = xbmcgui.ListItem('🔍 Cerca Film o Serie TV')
    # isFolder=True indica a Kodi che cliccando si aprirà una nuova lista
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url_search, listitem=li_search, isFolder=True)

    # Voce 2: Continua a guardare
    url_resume = build_url({'action': 'continue_watching'})
    li_resume = xbmcgui.ListItem('▶ Continua a Guardare')
    #Mettiamo un'icona di default nativa per abbellire
    li_resume.setArt({'icon': 'DefaultVideoPlaylists.png'})
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url_resume, listitem=li_resume, isFolder=True)

    # Termina la generazione della lista per mostrarla a schermo
    xbmcplugin.endOfDirectory(HANDLE)

def router(paramstring):
    """
    Legge i parametri dell'URL e decide quale schermata o azione eseguire.
    """
    # Analizza la stringa e la converte in un dizionario Python
    params = dict(urllib.parse.parsse_qsl(paramstring))
    action = params.get('action')

     if not action:
        # Se non c'è nessuna action, siamo nella Home. Mostriamo il menu principale.
        show_main_menu()

    elif action == 'search':
        # TODO: Implementeremo la barra di ricerca e la chiamata allo scraper
        xbmcgui.Dialog().ok("KodFlix", "Menu Ricerca in arrivo!")

    elif action == 'continue_watching':
        # TODO: Implementeremo la lettura dal Database e la lista degli episodi
        xbmcgui.Dialog().ok("KodFlix", "Menu Continua a Guardare in arrivo!")

    elif action == 'play':
        # TODO: Avvieremo la riproduzione e il monitoraggio per il Resume
        pass

if __name__ == '__main__':
    # sys.argv[2] contiene i parametri dell'URL (es: "?action=search").
    # Usiamo [1:] per tagliare il "?" iniziale.
    router(sys.argv[2][1:])
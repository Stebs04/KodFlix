# -*- coding: utf-8 -*-                                                                                                                                                      
"""                                                                                                                                                                          
Modulo principale e Router di avvio per KodFlix.                                                                                                                             
Gestisce la visualizzazione dei menu principali, della sezione 'Continua a Guardare'                                                                                         
e l'instradamento delle richieste verso il Player.                                                                                                                           
"""                                                                                                                                                                          
                                                                                                                                                                                
import sys                                                                                                                                                                   
import urllib.parse                                                                                                                                                          
import xbmcgui                                                                                                                                                               
import xbmcplugin                                                                                                                                                            
                                                                                                                                                                                
# Importiamo i moduli core dell'addon                                                                                                                                        
from core import database                                                                                                                                                    
try:                                                                                                                                                                         
    from core.player import KodFlixPlayer                                                                                                                                    
except ImportError:                                                                                                                                                          
    from core.player import KodFLixPlayer as KodFlixPlayer                                                                                                                   
                                                                                                                                                                                
# Otteniamo Handle numerico della finestra e Base URL generati da Kodi                                                                                                       
HANDLE = int(sys.argv[1])                                                                                                                                                    
BASE_URL = sys.argv[0]                                                                                                                                                       
                                                                                                                                                                                
                                                                                                                                                                                
def build_url(query):                                                                                                                                                        
    """                                                                                                                                                                      
    Costruisce un URL compatibile con Kodi unendo la BASE_URL e i parametri query.                                                                                           
    Esempio di output: plugin://plugin.video.kodflix/?action=continue_watching                                                                                               
    """                                                                                                                                                                      
    return BASE_URL + '?' + urllib.parse.urlencode(query)                                                                                                                    
                                                                                                                                                                                
                                                                                                                                                                                
def show_main_menu():                                                                                                                                                        
    """                                                                                                                                                                      
    Genera e visualizza la schermata Home (menu principale) dell'addon.                                                                                                      
    """                                                                                                                                                                      
    # 1. Voce: Ricerca Film e Serie TV                                                                                                                                       
    url_search = build_url({'action': 'search'})                                                                                                                             
    li_search = xbmcgui.ListItem('🔍 Cerca Film o Serie TV')                                                                                                                 
    li_search.setArt({'icon': 'DefaultAddonsSearch.png'})                                                                                                                    
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url_search, listitem=li_search, isFolder=True)                                                                            
                                                                                                                                                                                
    # 2. Voce: Continua a guardare                                                                                                                                           
    url_resume = build_url({'action': 'continue_watching'})                                                                                                                  
    li_resume = xbmcgui.ListItem('▶ Continua a Guardare')                                                                                                                    
    li_resume.setArt({'icon': 'DefaultVideoPlaylists.png'})                                                                                                                  
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url_resume, listitem=li_resume, isFolder=True)                                                                            
                                                                                                                                                                                
    # Chiude la directory e ordina a Kodi di mostrare la lista                                                                                                               
    xbmcplugin.endOfDirectory(HANDLE)                                                                                                                                        
                                                                                                                                                                                
                                                                                                                                                                                
def show_continue_watching():                                                                                                                                                
    """                                                                                                                                                                      
    Legge dal database SQLite tutti i contenuti memorizzati nella sezione 'Continua a Guardare'                                                                              
    e crea i ListItem iniettando la proprietà nativa 'ResumeTime' di Kodi.                                                                                                   
    """                                                                                                                                                                      
    items = database.get_continue_watching_list()                                                                                                                            
                                                                                                                                                                                
    # Se non ci sono contenuti in cronologia, avvisa l'utente con una notifica discreta                                                                                      
    if not items:                                                                                                                                                            
        xbmcgui.Dialog().notification("KodFlix", "Nessun contenuto in sospeso", xbmcgui.NOTIFICATION_INFO, 3000)                                                             
        xbmcplugin.endOfDirectory(HANDLE)                                                                                                                                    
        return                                                                                                                                                               
                                                                                                                                                                                
    for item in items:                                                                                                                                                       
        tmdb_id = item['tmdb_id']                                                                                                                                            
        title = item['title']                                                                                                                                                
        season = int(item['season'])                                                                                                                                         
        episode = int(item['episode'])                                                                                                                                       
        poster_url = item.get('poster_url', '')                                                                                                                              
                                                                                                                                                                                
        # Recupera il minutaggio salvato (se presente)                                                                                                                       
        resume_time = database.get_resume_point(tmdb_id, season, episode)                                                                                                    
                                                                                                                                                                                
        # Formatta il titolo (es: Breaking Bad - S01E03 oppure Inception per i film)                                                                                         
        if season > 0 and episode > 0:                                                                                                                                       
            label = f"{title} - S{season:02d}E{episode:02d}"                                                                                                                 
            media_type = 'episode'                                                                                                                                           
        else:                                                                                                                                                                
            label = title                                                                                                                                                    
            media_type = 'movie'                                                                                                                                             
                                                                                                                                                                                
        # Costruisce l'URL di riproduzione con i metadati necessari                                                                                                          
        url = build_url({                                                                                                                                                    
            'action': 'play',                                                                                                                                                
            'tmdb_id': tmdb_id,                                                                                                                                              
            'title': title,                                                                                                                                                  
            'season': str(season),                                                                                                                                           
            'episode': str(episode),                                                                                                                                         
            'poster_url': poster_url                                                                                                                                         
        })                                                                                                                                                                   
                                                                                                                                                                                
        li = xbmcgui.ListItem(label)                                                                                                                                         
                                                                                                                                                                                
        # Assegna locandine e miniature                                                                                                                                      
        if poster_url:                                                                                                                                                       
            li.setArt({                                                                                                                                                      
                'poster': poster_url,                                                                                                                                        
                'thumb': poster_url,                                                                                                                                         
                'icon': poster_url                                                                                                                                           
            })                                                                                                                                                               
                                                                                                                                                                                
        # Imposta le info video                                                                                                                                              
        li.setInfo('video', {                                                                                                                                                
            'title': label,                                                                                                                                                  
            'mediatype': media_type,                                                                                                                                         
            'season': season if season > 0 else None,                                                                                                                        
            'episode': episode if episode > 0 else None                                                                                                                      
        })                                                                                                                                                                   
                                                                                                                                                                                
        # Iniezione del Resume Time nativo di Kodi                                                                                                                           
        # In questo modo la skin mostrerà la barra di avanzamento e il popup "Riprendi da mm:ss"                                                                             
        if resume_time > 0:                                                                                                                                                  
            li.setProperty('ResumeTime', str(resume_time))                                                                                                                   
            try:                                                                                                                                                             
                # API Kodi 19+ Matrix                                                                                                                                        
                li.getVideoInfoTag().setResumePoint(resume_time)                                                                                                             
            except AttributeError:                                                                                                                                           
                pass                                                                                                                                                         
                                                                                                                                                                                
        # Segnala a Kodi che l'elemento è riproducibile direttamente                                                                                                         
        li.setProperty('IsPlayable', 'true')                                                                                                                                 
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=False)                                                                                     
                                                                                                                                                                                
    xbmcplugin.setContent(HANDLE, 'episodes')                                                                                                                                
    xbmcplugin.endOfDirectory(HANDLE)                                                                                                                                        
                                                                                                                                                                                
                                                                                                                                                                                
def play_media(params):                                                                                                                                                      
    """                                                                                                                                                                      
    Gestisce l'avvio della riproduzione e aggancia il KodFlixPlayer per il monitoraggio.                                                                                     
    """                                                                                                                                                                      
    video_url = params.get('video_url')                                                                                                                                      
    title = params.get('title', 'Video')                                                                                                                                     
    tmdb_id = params.get('tmdb_id', '')                                                                                                                                      
    season = int(params.get('season', 0))                                                                                                                                    
    episode = int(params.get('episode', 0))                                                                                                                                  
    poster_url = params.get('poster_url', '')                                                                                                                                
                                                                                                                                                                                
    media_info = {                                                                                                                                                           
        'tmdb_id': tmdb_id,                                                                                                                                                  
        'title': title,                                                                                                                                                      
        'season': season,                                                                                                                                                    
        'episode': episode,                                                                                                                                                  
        'poster_url': poster_url                                                                                                                                             
    }                                                                                                                                                                        
                                                                                                                                                                                
    # Se non c'è ancora un URL video reale (perché lo scraper non è ancora collegato)                                                                                        
    if not video_url:                                                                                                                                                        
        xbmcgui.Dialog().ok(                                                                                                                                                 
            "KodFlix",                                                                                                                                                       
            f"Pronto per la riproduzione:\n[B]{title}[/B]\n\n"                                                                                                               
            "La ricerca e lo scraping dei flussi video verranno implementati nel prossimo task."                                                                             
        )                                                                                                                                                                    
        return                                                                                                                                                               
                                                                                                                                                                                
    # Se invece è presente un URL video, avvia la riproduzione e il monitor del resume                                                                                       
    li = xbmcgui.ListItem(title)                                                                                                                                             
    li.setPath(video_url)                                                                                                                                                    
    li.setProperty('IsPlayable', 'true')                                                                                                                                     
                                                                                                                                                                                
    xbmcplugin.setResolvedUrl(HANDLE, True, li)                                                                                                                              
                                                                                                                                                                                
    # Avvia il player e il monitoraggio continuo                                                                                                                             
    player = KodFlixPlayer(media_info=media_info)                                                                                                                            
    player.start_playback_monitor()                                                                                                                                          
                                                                                                                                                                                
                                                                                                                                                                                
def router(paramstring):                                                                                                                                                     
    """                                                                                                                                                                      
    Router dell'addon: decodifica la query string ed esegue la relativa azione.                                                                                              
    """                                                                                                                                                                      
    params = dict(urllib.parse.parse_qsl(paramstring))                                                                                                                       
    action = params.get('action')

    if not action:
        # Se non ci sono parametri nell'URL, siamo nella Home
        show_main_menu()

    elif action == 'continue_watching':
        show_continue_watching()

    elif action == 'search':
        xbmcgui.Dialog().ok("KodFlix", "Il modulo di Ricerca e Scraping verrà integrato nel prossimo step.")

    elif action == 'play':
        play_media(params)


if __name__ == '__main__':
    # sys.argv[2] contiene la query string (es: "?action=continue_watching")
    router(sys.argv[2][1:])
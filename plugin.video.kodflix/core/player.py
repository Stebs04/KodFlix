#-*- coding: utf-8 -*-
'''
Modulo player per KodFlix
Estende xbmc.Player di Kodi per monitorare la riproduzione video in tempo reale,
calcolare lo stato di completamento e salvare il punto di ripresa nel database SQLite
'''
import xbmc 
from core import database

class KodFLixPlayer(xbmc.Player):
    """                                                                                                                                                                      
    Player personalizzato con tracciamento continuo del minutaggio.                                                                                                          
                                                                                                                                                                                
    Gestisce la logica di resume:                                                                                                                                            
    - Se visto per >= 90%: segna come completato e avanza all'episodio successivo (per le serie TV).                                                                         
    - Se visto tra il 5% e il 90%: salva il timestamp esatto (secondi) per riprendere la visione.                                                                            
    - Se visto per < 5%: ignorato (uscita accidentale o test iniziale).                                                                                                      
    """

    def __init__(self, media_info=None):
        """                                                                                                                                                                  
        Inizializza il player con i metadati del contenuto in riproduzione.                                                                                                  
                                                                                                                                                                                
        :param media_info: Dizionario contenente i metadati:                                                                                                                 
                            - tmdb_id (str): ID univoco TMDB del film o serie                                                                                                 
                            - title (str): Titolo del film o della serie                                                                                                      
                            - season (int): Numero della stagione (0 per i film)                                                                                              
                            - episode (int): Numero dell'episodio (0 per i film)                                                                                              
                            - poster_url (str): URL della locandina                                                                                                           
        """

        super().__init__()
        self.media_info = media_info or {}
        self.played_time = 0.0
        self.total_time = 0.0

    def start_playback_monitor(self):
        """                                                                                                                                                                  
        Ciclo di monitoraggio continuo durante la riproduzione.                                                                                                              
                                                                                                                                                                                
        Nota architetturale su Kodi:                                                                                                                                         
        Quando l'utente preme 'Stop', Kodi distrugge il playback prima che l'evento                                                                                          
        `onPlayBackStopped` termini; tentare di chiamare `self.getTime()` in quel momento                                                                                    
        restituisce 0 o solleva un'eccezione.                                                                                                                                
        Questo loop campiona regolarmente il minutaggio ogni secondo finché il video è attivo.                                                                               
        """          
        monitor = xbmc.Monitor()

        #Attesa attiva: Aspetta che il flusso video parti effettivamente
        while not self.isPlayingVideo() and not monitor.abortRequested():
            if monitor.waitForAbort(0.5):
                return 

        #Loop principale: campiona il minutaggio ogni secondo
        while self.isPlayingVideo() and not monitor.abortRequested():
            try:
                self.played_time = self.getTime()
                self.total_time = self.getTotalTime()

            except Exception:
                pass

            # waitForAbort(1.0) attende 1 secondo senza bloccare il thread di sistema di Kodi
            if monitor.waitForAbort(1.0):
                break

        #Riproduzione terminata o interrotta: Elabora i dati e li salva
        self._handle_playback_finished()

    def _handle_playback_finished(self):
        """                                                                                                                                                                  
        Valuta la percentuale di completamento del video e aggiorna il database SQLite.                                                                                      
        """          

        #Se la durata non è valida non si può calcolare la percentuale
        if self.total_time <= 0:
            return

        tmdb_id = self.media_info.get('tmdb_id')
        if not tmdb_id:
            return 

        season = int(self.media_info.get('season', 0))                                                                                                                       
        episode = int(self.media_info.get('episode', 0))                                                                                                                     
        title = self.media_info.get('title', '')                                                                                                                             
        poster_url = self.media_info.get('poster_url', '')                                                                                                                   
        is_tvshow = bool(season > 0 or episode > 0)                 

        #Calcolo del rapporto di visione 

        progress_ratio = self.played_time / self.total_time

        if progress_ratio >= 0.90:
            # Caso A: Video completato (soglia >= 90%)                                                                                                                       
            # Azzeriamo il punto di ripresa per questo episodio specifico                                                                                                       
            database.save_resume_point(tmdb_id, season, episode, 0.0, self.total_time)

            if is_tvshow:                                                                                                                                                    
                # Per le Serie TV: avanziamo all'episodio successivo nel 'Continua a Guardare'                                                                               
                next_episode = episode + 1                                                                                                                                   
                database.update_continue_watching(                                                                                                                           
                    tmdb_id=tmdb_id,                                                                                                                                         
                    title=title,                                                                                                                                             
                    season=season,                                                                                                                                           
                    episode=next_episode,                                                                                                                                    
                    poster_url=poster_url                                                                                                                                    
                )

        elif progress_ratio >= 0.05:                                                                                                                                         
            # Caso B: Video interrotto a metà (tra 5% e 90%)                                                                                                                 
            # Salviamo il minutaggio esatto per il tasto "Riprendi da..."                                                                                                    
            database.save_resume_point(tmdb_id, season, episode, self.played_time, self.total_time)                                                                          
                                                                                                                                                                                
            # Manteniamo l'episodio corrente nella home del 'Continua a Guardare'                                                                                            
            database.update_continue_watching(                                                                                                                               
                tmdb_id=tmdb_id,                                                                                                                                             
                title=title,                                                                                                                                                 
                season=season,                                                                                                                                               
                episode=episode,                                                                                                                                             
                poster_url=poster_url                                                                                                                                        
            )

        else:
            # Caso C: Uscita immediata (< 5%)                                                                                                                                
            # Considerato avvio accidentale; non modifichiamo lo stato del database                                                                                          
            pass



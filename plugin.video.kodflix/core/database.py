# -*- coding: utf-8 -*-
import os
import sqlite3
import xbmc
import xbmcaddon

# Gestione della compatibilitá tra Kodi 18 e Kodi 19+ 
try:
    import xbmcvfs
    translatePath = xbmcvfs.translatePath
except:
    translatePath = xbmc.translatePath

ADDON = xbmcaddon.Addon()
# 'profile' è la cartella userdata dell'addon, dove è corretto e sicuro salvare i database
PROFILE_DIR = translatePath(ADDON.getAddonInfo('profile'))
DB_FILE = os.path.join(PROFILE_DIR, 'kodflix.db')

def _get_connection():
    """Ritorna una connessione al DB SQLite. Crea la cartella se non esiste."""
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR)
    
    conn = sqlite3.connect(DB_FILE)
    # row_factory ci permette di accedere alle colonne restituite come un dizionario (per nome)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inizializza le tabelle necessarie (safe da chiamare più volte grazie a IF NOT EXISTS)."""
    conn = _get_connection()
    cursor = conn.cursor()

    # 1. Tabella per salvare i resume point esatti (minuti/secondi)
    # Usiamo tmdb_id + season + episode come chiave primaria unica
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_points (
            tmdb_id TEXT,
            season INTEGER,
            episode INTEGER,
            played_time REAL,
            total_time REAL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tmdb_id, season, episode)
        )
    ''')

    # 2. Tabella per i metadati della UI "Continua a guardare" (menu principale)
    # Qui salviamo la "Serie TV", quindi la chiave primaria è solo tmdb_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS continue_watching (
            tmdb_id TEXT PRIMARY KEY,
            title TEXT,
            season INTEGER,
            episode INTEGER,
            poster_url TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def save_resume_point(tmdb_id, season, episode, played_time, total_time):
    """Salva il tempo di riproduzione (per riprendere da dove ci si è fermati)."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute('''
            INSERT OR REPLACE INTO resume_points (tmdb_id, season, episode, played_time, total_time, last_updated)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (str(tmdb_id), int(season), int(episode), float(played_time), float(total_time)))
    conn.commit()
    conn.close()

def get_resume_point(tmdb_id, season, episode):
    """Recupera il tempo salvato in precedenza (in secondi). Ritorna 0.0 se non c'è."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT played_time FROM resume_points
        WHERE tmdb_id = ? AND season = ? AND episode = ?
    ''', (str(tmdb_id), int(season), int(episode)))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row['played_time']
    return 0.0

def update_continue_watching(tmdb_id, title, season, episode, poster_url):
    """Aggiorna la sezione 'Continua a guardare' con l'ultimo episodio che stiamo vedendo."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO continue_watching (tmdb_id, title, season, episode, poster_url, last_updated)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (str(tmdb_id), str(title), int(season), int(episode), str(poster_url)))
    conn.commit()
    conn.close()

def get_continue_watching_list():
    """Ritorna la lista completa per la schermata 'Continua a Guardare', ordinata dal più recente."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM continue_watching
        ORDER BY last_updated DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    # Convertiamo l'oggetto sqlite3.Row in una normale lista di dizionari Python
    return [dict(row) for row in rows]

# Eseguito automaticamente ogni volta che importiamo questo file, garantendo che le tabelle esistano!
init_db()
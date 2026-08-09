# Obiettivo
Creare un nuovo addon per Kodi per la ricerca e lo streaming di Film e Serie TV, basato su un addon esistente.

## Requisiti Core
- **Funzionalità di base**: Ricerca, scraping e riproduzione (basati sull'addon di riferimento).
- **Nuova Funzionalità: Continua a Guardare (Continue Watching)**:
  - Sezione di riepilogo (Widget/Home) che indica l'ultimo episodio/stagione visti per le Serie TV.
  - Salvataggio del "resume point" (minuti/secondi) per riprendere la visione di film ed episodi esattamente da dove interrotta.

## Criteri di Successo
- L'addon si installa e si avvia correttamente su Kodi.
- Le funzionalità di ricerca, scraping e riproduzione funzionano come nel progetto originale.
- Il sistema "Continua a guardare" traccia correttamente le serie e permette di riprendere la visione in base al resume point.
- Il codice è ben strutturato, leggibile e documentato.

## Architettura "Continua a guardare" (Continue Watching)
In base all'analisi del progetto originale, ecco come implementeremo questa funzionalità chiave:

**1. Salvataggio del Resume Point (Tempo di riproduzione)**
- Il progetto originale intercetta già lo stop della riproduzione e salva il tempo (`played_time`) tramite un loop `while` (`platformcode/xbmc_videolibrary.py`) che controlla `xbmc.Player().getTime()`. 
- Sfrutteremo questo stesso loop (o un'estensione più pulita della classe `xbmc.Player` con gli hook `onPlayBackStopped`), salvando il minutaggio in un database custom SQLite gestito dall'addon (file `db.sqlite`, tramite `SqliteDict`).
- Quando un video viene listato, andremo a leggere il DB e inietteremo il tempo salvato nel `ListItem` usando la proprietà nativa `ResumeTime` di Kodi (es: `listitem.setProperty('ResumeTime', str(resume_time))`). Kodi mostrerà automaticamente il popup "Riprendi da...".

**2. Sezione "Continua a guardare" per le Serie TV**
- Creeremo una nuova tabella/sezione nel database SQLite dell'addon (es. `db['continue_watching']`).
- Al completamento di un episodio (quando `getTime() > 90%` di `getTotalTime()`), si contrassegna l'episodio come Visto e **si inserisce nella tabella l'episodio successivo** per quella serie, includendo metadati completi (tmdb_id, stagione, episodio, titolo, poster, timestamp di ultimo aggiornamento).
- Se la visione viene interrotta a metà (es. al 50%), il record si aggiornerà per riproporre l'episodio corrente con il relativo *Resume Time*.
- Verrà creato un menu dedicato (`channel`) nell'addon chiamato **"Continua a guardare"** che preleverà gli elementi da questo DB custom, ordinandoli per data, e generando un elenco `ListItem` che potremo eventualmente collegare ai widget della Home di Kodi.

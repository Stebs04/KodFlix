# Piano d'Azione

- [x] **FASE 1: Inizializzazione della Documentazione**
  - [x] Creare `TASK.md`, `PLAN.md`, `AGENTS.md`.

- [x] **FASE 2: Analisi del Progetto di Riferimento**
  - [x] Esplorare l'alberatura del progetto originale (`C:\Users\DeaDS\Documents\Programming projects\addon`).
  - [x] Analizzare file principali (`launcher.py`, `default.py`, ecc.).
  - [x] Analizzare la logica di scraping, ricerca e riproduzione (cartelle `core/`, `channels/`, `platformcode/`).
  - [x] Aggiornare `PLAN.md` con le scoperte sull'architettura originale.

- [x] **FASE 3: Progettazione Architettura e "Continua a Guardare"**
  - [x] Ideare la strategia per il Continue Watching (uso DB SQLite nativo Kodi vs DB custom dell'addon, gestione `resume` in `ListItem`).
  - [x] Spiegare e annotare la strategia nel `TASK.md` o in questa chat, e attendere approvazione dell'utente.

- [ ] **FASE 4: Sviluppo Core del Nuovo Addon (In corso)**
  - [x] Creare la struttura base del nuovo addon (`addon.xml`, icon, fanart, etc.).
  - [ ] Implementare/Adattare la logica di base (ricerca, scraping, riproduzione).
  - [x] Implementare il database/tracciamento del "Continua a Guardare".
  - [ ] Implementare la gestione del resume point in riproduzione intercettando `xbmc.Player()`.

- [ ] **FASE 5: Sviluppo UI e Integrazione**
  - [ ] Creare la sezione / menu "Continua a guardare" nell'interfaccia dell'addon.
  - [ ] (Opzionale) Esportazione verso i widget della Home di Kodi.
  - [ ] Testing finale e debug.

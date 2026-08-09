# Regole di Comportamento

1. **Mai indovinare il codice**: Usa sempre i tool di lettura (`list_dir`, `view_file`, `grep_search`) per esaminare il codice dell'addon di riferimento. Non assumere la struttura dei file o il nome delle variabili.
2. **Documentazione**: Documenta bene il codice Python (docstring per funzioni e classi, commenti per blocchi logici complessi).
3. **Gestione Resume**: Per il sistema "Continua a Guardare", assicurati di usare correttamente le API di Kodi (es. le API di `xbmc.Player()` per intercettare lo stop, `xbmcgui.ListItem` per settare i metadati di resume, o un DB locale custom SQLite).
4. **Struttura Modulare**: Mantieni la logica separata in moduli ben distinti (UI, DB, Scraper, Player) per facilitare la manutenzione.
5. **Aggiornamento Continuo**: Tieni sempre aggiornati `TASK.md` e `PLAN.md` man mano che il progetto evolve e si completano i vari step.

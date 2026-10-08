# Progress tracking
## Decision Log for the progect

| Data | login | Decisione |
| ---- | ----- | --------- |
| 2026-15-08 | *fedegugl* |Libreria grafica conforme a MLX: niente `pygame.font` avanzato/primitive con fill, audio ed equivalenze da verificare |
| 2026-08-19 | *fedegugl* |`mazegenerator.py` è il pacchetto A-Maze-ing assegnato — trattato come dipendenza esterna non modificabile |
| 2026-08-27 | *fedegugl* | `ConfigFileNotFound` in `parsey.py` resta come difesa in profondità voluta, non è ridondanza da togliere |
| 2026-08-28 | *fedegugl* | Riuso di `MissingLevelError` per il check minimo-10-livelli (VI.7 del subject) |
| 2026-08-28 | *fedegugl* | Movimento fluido futuro (player + fantasmi) basato su waypoint a centro-cella, non collisione continua a pixel |
| 2026-08-29 | *fedegugl* | **BUG CRITICO** : costanti `WALL_LEFT/TOP/RIGHT/BOTTOM` in `game_page.py` non corrispondono alla convenzione reale del pacchetto `mazegenerator`|
| 2026-08-29 | *fedegugl* | Rendering muri: cornice esterna a linea doppia, muri interni a linea singola con segmenti accorciati, tile di intersezione dedicati per i vertici|
| 2026-08-30 | *fedegugl* | Bug di rotazione 90° negli asset muro/intersezione: risolto con tabelle di traduzione mask→file in `GamePage`, senza toccare i 32 PNG |
| 2026-08-31 | *fedegugl* | Asset wall/intersection rigenerati (1600px) sostituiti con un set finale (36px) verificato al 100% su tutti i 16 mask di intersezione|
| 2026-09-04 | *gcerrete*, *fedegugl* | Allienamento progetto: Discussione su separazione netta tra ui e core del progetto |
| 2026-09-07 | *gcerrete*, *fedegugl* | Refactoring `Game_page.py`: separate completamente la logica ui da quella del core |
| 2026-09-08 | *gcerrete* | Logica Ghost implementata, aggiustamenti della logica del player. Collegato player e Ghost per implementazione collisioni |
| 2026-09-09 | *fedegugl* | Ampliamento della logica di animazione per gestione delle scene allinterno di `instruction_page.py` e `main_menu.py` |
| 2026-09-10 | *gcerrete* | Unica Classe gestisce tutti i ghost|
| 2026-09-10 | *gcerrete* | Utilizzo di algoritmo BFS per il moviment dei ghost|
| 2026-09-11 | *fedegugl* | Allineamento della repository e primo push su git scolastico: Ora i file sono alllineati a stato corrente |
| 2026-09-11 | *fedegugl* | Inserimento della animazione della pagina delle istruzioni |
| 2026-09-10 | *gcerrete* | Ampliamento della classe delle pacgum, differenza con le superpacgum|
| 2026-09-12 | *gcerrete* | Cycle ghost: normal, frightened, eated. To complete with graphic
| 2026-09-13 | *fedegugl* | Completamento della pagina main_menu: tre stati che gestiscono l animazione della scena introduttiva|
| 2026-09-13 | *gcerrete* | Portati oggetti ghost nel metodo Draw di entity_renderer. Il fine e di gestire lo stato grafico di ghosts normal, frightened, eated.
| 2026-09-13 | *fedegugl* | Refactoring di gestione della ui ed eliminazione del codce morto o ridondante |
| 2026-09-14 | *fedegugl* | Completamento della impostazione della gafica di game_page: pannelli, HUD ed eliiazione delle cherry che vengono sostituite dal '42' |
| 2026-09-15 | *gcerrete* | Stati dei ghost, frighened, eaten, normal, connessi alle relative immagini. flake8 complete, mypy 90% complete. Minor: ripristinato il collegamento ai cheat settings. Superpacgum disegnate piu grandi.
| 2026-09-16 | *fedegugl* *gcerrete* | Aggiornato piano UI tramite call: Eiminazione delle logiche di animanzione. UI minimale e funzionale |
| 2026-09-17 | *fedegugl* | Assemblamento di Menupausa -> Game_page -> Menu_pausa - adesso il timer del livello rspetta la logica della pausa |
| 2026-09-17 | *gcerrete* | Debug della paralisi dei fantasmi e implementazione collisioni tra pacman e fantasmi |
| 2026-09-18 | *fedegugl* | Allineamento della logica del tra pause menu e pagina impostazioni (cheating) -  mypy e flake migliorati|
| 2026-09-18 | *gcerrete* *fedegugl*  | rimozione della logica dello speed del ghst dal progetto - rimossa chiave in json |
| 2026-09-18 | *gcerrete* *fedegugl*  | Cmbiamento cheat-page level skip - ora abbiamo debug button da cui e possibile fare evel skip|
| 2026-09-18 | *gcerrete* | Implementate tutte le cheat settings. Implementato respawn a distanza dopo collisione pacman-ghost. Corretti alcuni mypy, corretto il respawn dei ghost: adesso tornano ai rispettivi corner.|
| 2026-09-19 | *fedegugl* | Aggiustare la grafica di tutte le pagine presenti - tutte le pagine funzionati |
| 2026-09-19 | *gcerrete* | ---- |
| 2026-09-20 | *fedegugl* | Ultimo controllo della logica della UI e del flusso del player - UI Stato complete - logic pending |
| 2026-09-20 | *gcerrete* | ---- |
| 2026-09-22 | *fedegugl* | **UI Stato complete** - logic pending |
| 2026-09-23 | *fedegugl* | **END - mypy flake8** file src/ui/configUI/ui_config.py e directory configUI - logic pending |
| 2026-09-23 | *fedegugl* | **END - ciclo logica degli stati tra menu** Preparato lo spazio per la logica del cheatig state - logic pending |
| 2026-09-23 | *gcerrete* | soluzione del pacman - player ora si gira correttamente. Risolto sovrapposizione dei ghost |
| 2026-09-24 | *fedegugl* | **END - mypy flake8** file directory  src/ui/pages - logic pending |
| 2026-09-24 | *fedegugl* | **END - UI screen end game** Grafica allineata e conforme file directory src/ui/pages/end_screen.py - logic pending |
| 2026-09-24 | *fedegugl* | **CORE** Recuperata logica del flash del ghost - *UI RISOLTA* Lasciati commeni tecnici per *CORE* - logic pending|
| 2026-09-25 | *fedegugl* | ~~**UI STATO CLOSED**  Allinemento finale della UI Con logica generale - logic pending~~ |
| 2026-09-25 | *fedegugl* *gcerrete*| **RIUNIONE END WEEK** - Discussione su come procedere nei prossimi giorni. |
| 2026-09-26 | *gcerrete* | **next level implementato** Pacman inizia al centro al passagio di livello. passaggio livello successivo, gestione pacman, ghost, pacgum, maze. Risolto respawn e sovrapposizione ghosts. Gestita grafica perdita lives. Connessa cheat page a game_page e pacman
| 2026-09-28 | *fedegugl* | **UI STATO CLOSED**  Allinemento finale della UI Con logica generale - logic pending |
| 2026-09-29 | *fedegugl* | Testing della ui, nessun bug rilevato. Aggiustmenti e ripristino di pagine ui perse nel push nella repository| 
| 2026-09-29 | *gcerrete* | Sound added for pacman death and next level. Debug implemented in settings. Extra lives setting implemented. flashing ghost implemented.
Last life loss implemented, back to main menu. |
| 2026-09-30 | *fedegugl* | Revisione docstring, colegamento della facciata statica del game over - logic pnding|
| 2026-09-30 | *fedegugl* | Aggiustamenti in redering e completamento doctring|
| 2026-09-29 | *fedegugl* *gcerrete* | **BUG CRITICO** : timer non si riavvia a nuovo livello. Timer bug solved. Victory page connected and funcioning. New pacman coordinates y->p_row x->p_col. Ghost coordinates changed in: x->g_col , y->g_row. **BUG CRITICO** Not squared maze crashes. |
| 2026-10-01 | *fedegugl* | Completamento del rendering dei ghost - allineato con quello di pacman e documentato, logica di core da aggiornare al nuovo render - LOGIC pending|
| 2026-10-01 | *fedegugl* | **BUG CRITICO** : pacgum e super pacgum non sono divisi, controllato cambiando di due colore estremamente diversi, vienne sempre usato il pacgum sprite|
| 2026-10-01 | *fedegugl* *gcerrete* | **BUG CRITICO** : i fantasmi se in fear mode o mangiati non lasciano a pac man mangiare |
| 2026-10-01 | *fedegugl* | **BUG CRITICO** : i super pacgum hanno un comportamento anomalo - se mangi un super pacgum hai dei secondi a dispoizione ma se ne mangi un altro mentre i fantasmi sono in fear mode il contatore dovrebbe ripartire da capo e darti i soliti secondi. (e.g mangi sp, 30 sec concessi, ne consumi 20, nei restati 10 sec mangi un altro sp riparti da 30 sec)|
| 2026-10-01 | *gcerrete* | Modificato pacgums, pacman, game_page, ghost. Bug dimensioni scambiate risolto. Bug timer super pacgums risolto, il timer riparte anche mangiando una superpacgum mentre i ghosts sono in fear. Risolto Bug pacgum non mangiato mentre e sovrapposto ad un ghost in frighten o fear.
| 2026-10-02 | *gcerrete* | Analisi sul miglior modo di separare movimento pacman / ghost.
| 2026-10-03 | *gcerrete* | Trovati e risolti altri bug su scambio dimensioni maze. Refactoring su nomi coordinate, rinominandole in row col.
| 2026-10-04 | *gcerrete* | Separato movimento pacman dal movimento ghost. Inizio a lavorare su implementazione movimento fluido.
| 2026-10-01 | *fedegugl* | **REFACTORING** : allineamento delle title del maze. dimensioni allineate a 64 x 64 |
| 2026-10-02 | *fedegugl* | **BUG CRITICO** : il render del maze non ha rispettato le specifiche: refactoring per eviatre doppie stampe |
| 2026-10-03 | *fedegugl* | Risolto bug doppia stampa, aggiunto togle fullscreem, aggiornato asset managwer per allinearsi alla nuova logica di generazione |
| 2026-10-05 | *gcerrete* | Ghost fluid movement function correctly. Debugging. Minor bugs fixed.
| 2026-10-05 | *gcerrete* | Next level bug on varied maze dimension: solved.
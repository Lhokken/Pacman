# Progress tracking

## Decision Log for the progect

| Data | login | Decisione |
| ---- | ----- | --------- |
| 2026-15-08 | *fedegugl* | Libreria grafica conforme a MLX: niente `pygame.font` avanzato/primitive con fill, audio ed equivalenze da verificare |
| 2026-08-19 | *fedegugl* | `mazegenerator.py` è il pacchetto A-Maze-ing assegnato — trattato come dipendenza esterna non modificabile |
| 2026-08-27 | *fedegugl* | `ConfigFileNotFound` in `parsey.py` resta come difesa in profondità voluta, non è ridondanza da togliere |
| 2026-08-28 | *fedegugl* | Riuso di `MissingLevelError` per il check minimo-10-livelli (VI.7 del subject) |
| 2026-08-28 | *fedegugl* | Movimento fluido futuro (player + fantasmi) basato su waypoint a centro-cella, non collisione continua a pixel |
| 2026-08-29 | *fedegugl* | **BUG CRITICO** : costanti `WALL_LEFT/TOP/RIGHT/BOTTOM` in `game_page.py` non corrispondono alla convenzione reale del pacchetto `mazegenerator` |
| 2026-08-29 | *fedegugl* | Rendering muri: cornice esterna a linea doppia, muri interni a linea singola con segmenti accorciati, tile di intersezione dedicati per i vertici |
| 2026-08-30 | *fedegugl* | Bug di rotazione 90° negli asset muro/intersezione: risolto con tabelle di traduzione mask→file in `GamePage`, senza toccare i 32 PNG |
| 2026-08-31 | *fedegugl* | Asset wall/intersection rigenerati (1600px) sostituiti con un set finale (36px) verificato al 100% su tutti i 16 mask di intersezione |
| 2026-09-04 | *gcerrete*, *fedegugl* | Allienamento progetto: Discussione su separazione netta tra ui e core del progetto |
| 2026-09-07 | *gcerrete*, *fedegugl* | Refactoring `Game_page.py`: separate completamente la logica ui da quella del core |
| 2026-09-08 | *gcerrete* | Logica Ghost implementata, aggiustamenti della logica del player. Collegato player e Ghost per implementazione collisioni |
| 2026-09-09 | *fedegugl* | Ampliamento della logica di animazione per gestione delle scene allinterno di `instruction_page.py` e `main_menu.py` |
| 2026-09-10 | *gcerrete* | Unica Classe gestisce tutti i ghost |
| 2026-09-10 | *gcerrete* | Utilizzo di algoritmo BFS per il moviment dei ghost |
| 2026-09-11 | *fedegugl* | Allineamento della repository e primo push su git scolastico: Ora i file sono alllineati a stato corrente |
| 2026-09-11 | *fedegugl* | Inserimento della animazione della pagina delle istruzioni |
| 2026-09-10 | *gcerrete* | Ampliamento della classe delle pacgum, differenza con le superpacgum |
| 2026-09-12 | *gcerrete* | Cycle ghost: normal, frightened, eated. To complete with graphic |
| 2026-09-13 | *fedegugl* | Completamento della pagina main_menu: tre stati che gestiscono l animazione della scena introduttiva |
| 2026-09-13 | *gcerrete* | Portati oggetti ghost nel metodo Draw di entity_renderer. Il fine e di gestire lo stato grafico di ghosts normal, frightened, eated. |
| 2026-09-13 | *fedegugl* | Refactoring di gestione della ui ed eliminazione del codce morto o ridondante |
| 2026-09-14 | *fedegugl* | Completamento della impostazione della gafica di game_page: pannelli, HUD ed eliiazione delle cherry che vengono sostituite dal '42' |
| 2026-09-15 | *gcerrete* | Stati dei ghost, frighened, eaten, normal, connessi alle relative immagini. flake8 complete, mypy 90% complete. Minor: ripristinato il collegamento ai cheat settings. Superpacgum disegnate piu grandi. |
| 2026-09-16 | *fedegugl* *gcerrete* | Aggiornato piano UI tramite call: Eiminazione delle logiche di animanzione. UI minimale e funzionale |
| 2026-09-17 | *fedegugl* | Assemblamento di Menupausa -> Game_page -> Menu_pausa - adesso il timer del livello rspetta la logica della pausa |
| 2026-09-17 | *gcerrete* | Debug della paralisi dei fantasmi e implementazione collisioni tra pacman e fantasmi |
| 2026-09-18 | *fedegugl* | Allineamento della logica del tra pause menu e pagina impostazioni (cheating) -  mypy e flake migliorati |
| 2026-09-18 | *gcerrete* *fedegugl* | rimozione della logica dello speed del ghst dal progetto - rimossa chiave in json |
| 2026-09-18 | *gcerrete* *fedegugl* | Cmbiamento cheat-page level skip - ora abbiamo debug button da cui e possibile fare evel skip |
| 2026-09-18 | *gcerrete* | Implementate tutte le cheat settings. Implementato respawn a distanza dopo collisione pacman-ghost. Corretti alcuni mypy, corretto il respawn dei ghost: adesso tornano ai rispettivi corner. |
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
| 2026-09-25 | *fedegugl* *gcerrete* | **RIUNIONE END WEEK** - Discussione su come procedere nei prossimi giorni. |
| 2026-09-26 | *gcerrete* | **next level implementato** Pacman inizia al centro al passagio di livello. passaggio livello successivo, gestione pacman, ghost, pacgum, maze. Risolto respawn e sovrapposizione ghosts. Gestita grafica perdita lives. Connessa cheat page a game_page e pacman
| 2026-09-28 | *fedegugl* | **UI STATO CLOSED**  Allinemento finale della UI Con logica generale - logic pending |
| 2026-09-29 | *fedegugl* | Testing della ui, nessun bug rilevato. Aggiustmenti e ripristino di pagine ui perse nel push nella repository |
| 2026-09-29 | *gcerrete* | Sound added for pacman death and next level. Debug implemented in settings. Extra lives setting implemented. flashing ghost implemented. Last life loss implemented, back to main menu. |
| 2026-09-30 | *fedegugl* | Revisione docstring, colegamento della facciata statica del game over - logic pnding |
| 2026-09-30 | *fedegugl* | Aggiustamenti in redering e completamento doctring. |
| 2026-09-29 | *fedegugl* *gcerrete* | **BUG CRITICO** : timer non si riavvia a nuovo livello. Timer bug solved. Victory page connected and funcioning. New pacman coordinates y->p_row x->p_col. Ghost coordinates changed in: x->g_col , y->g_row. **BUG CRITICO** Not squared maze crashes. |
| 2026-10-01 | *fedegugl* | Completamento del rendering dei ghost - allineato con quello di pacman e documentato, logica di core da aggiornare al nuovo render - LOGIC pending |
| 2026-10-01 | *fedegugl* | **BUG CRITICO** : pacgum e super pacgum non sono divisi, controllato cambiando di due colore estremamente diversi, vienne sempre usato il pacgum sprite |
| 2026-10-01 | *fedegugl* *gcerrete* | **BUG CRITICO** : i fantasmi se in fear mode o mangiati non lasciano a pac man mangiare |
| 2026-10-01 | *fedegugl* | **BUG CRITICO** : i super pacgum hanno un comportamento anomalo - se mangi un super pacgum hai dei secondi a dispoizione ma se ne mangi un altro mentre i fantasmi sono in fear mode il contatore dovrebbe ripartire da capo e darti i soliti secondi. (e.g mangi sp, 30 sec concessi, ne consumi 20, nei restati 10 sec mangi un altro sp riparti da 30 sec) |
| 2026-10-01 | *gcerrete* | Modificato pacgums, pacman, game_page, ghost. Bug dimensioni scambiate risolto. Bug timer super pacgums risolto, il timer riparte anche mangiando una superpacgum mentre i ghosts sono in fear. Risolto Bug pacgum non mangiato mentre e sovrapposto ad un ghost in frighten o fear. |
| 2026-10-02 | *gcerrete* | Analisi sul miglior modo di separare movimento pacman / ghost. |
| 2026-10-03 | *gcerrete* | Trovati e risolti altri bug su scambio dimensioni maze. Refactoring su nomi coordinate, rinominandole in row col. |
| 2026-10-04 | *gcerrete* | Separato movimento pacman dal movimento ghost. Inizio a lavorare su implementazione movimento fluido. |
| 2026-10-01 | *fedegugl* | **REFACTORING** : allineamento delle title del maze. dimensioni allineate a 64 x 64 |
| 2026-10-02 | *fedegugl* | **BUG CRITICO** : il render del maze non ha rispettato le specifiche: refactoring per eviatre doppie stampe |
| 2026-10-03 | *fedegugl* | Risolto bug doppia stampa, aggiunto togle fullscreem, aggiornato asset managwer per allinearsi alla nuova logica di generazione |
| 2026-10-05 | *gcerrete* | Ghost fluid movement function correctly. Debugging. Minor bugs fixed. |
| 2026-10-06 | *gcerrete* | Next level bug on varied maze dimension: solved. Flake8 mypy. ok. |
| 2026-10-10 | *gcerrete* | Refactor pacman findspawn and life loss. |
| 2026-10-12 | *gcerrete* | Risolto bug indice livelli, adesso 10 livelli effettivi anziche 9. Passaggio highscore da dict a lista di tuple. Ordine per punteggio e savefile mantenuto. Gestione errore score negativi aggiunta. Row col in pacgums sincronizzate. |
| 2026-10-12 | *fedegugl* | **BUG IN MAKEFILE** :  install non allienato con UV |
| 2026-10-12 | *fedegugl* | **DECISIONE IN MAKEFILE** :  allineato install con UV |
| 2026-10-12 | *fedegugl* | **BUG UI CAMBIO LIVELLO** : durante il cambio livello (next_level()) la UI si rompe visivamente. Da verificare in simulazione il ricalcolo di layout, tile, asset e pannelli quando cambiano le dimensioni del maze. |
| 2026-10-12 | *fedegugl* | **BUG INSERIMENTO NOME** : un carattere non presente nei bitmap font (per esempio una lettera accentata) viene accettato e poi fa fallire il rendering della schermata finale. |
| 2026-10-12 | *fedegugl* | **DECISIONE INPUT NOME** : limitare i caratteri a quelli supportati dagli asset, escludendo gli accenti; rispettare il subject consentendo lettere, numeri e spazi fino a 10 caratteri. |
| 2026-10-12 | *fedegugl* | **BUG GESTIONE ERRORI ASSET** : verificare i `print` usati nei percorsi di errore e sostituirli con messaggi gestiti e coerenti con il logging, senza interrompere la UI. |
| 2026-10-12 | *fedegugl* | **BUG PACGUM** : pacgum e super-pacgum non risultano allineate all'animazione delle entita; la super-pacgum viene disegnata usando la pacgum normale ingrandita invece del proprio asset. |
| 2026-10-12 | *fedegugl* | **DECISIONE DIMENSIONE FINESTRA** : rilevare la risoluzione desktop all'avvio e non permettere alla finestra di scendere sotto l'80% di tale risoluzione; se l'utente tenta di ridurla sotto soglia, mostrare il messaggio di finestra troppo piccola e proteggere il rendering della cornice doppia. |
| 2026-10-12 | *fedegugl* | **CHECK ASSET INTERSECTIONS** : verificare graficamente l'allineamento dei tile di intersezione rispetto al centro del title e ai muri; il difetto asset precedente e' ritenuto risolto, ma va ricontrollato dopo il cambio livello. |
| 2026-10-12 | *fedegugl* | **BLOCCO PACKAGING** : l'archivio in `packaging/` contiene una wheel annidata e il target `make install` non riesce a installarla; manca inoltre `requirements.txt`. Adeguare l'installazione alla wheel assegnata e riprovare in ambiente pulito. |
| 2026-10-12 | *fedegugl* | **RISOLTO - MAKEFILE** : `install` usa `uv sync` e installa la wheel A-Maze-ing contenuta nello zip; `lint` e `lint-strict` eseguono i comandi espliciti del subject senza mascherare gli errori. Verificati parsing dei target e dry-run della wheel. |
| 2026-10-12 | *fedegugl* | **RISOLTO - CAMBIO LIVELLO/UI** : riprodotto l'uso dell'indice del livello precedente e la mancata sincronizzazione di tile, asset e pannelli. La transizione ora seleziona il livello successivo, riallinea layout e manager e termina correttamente su VictoryPage. Test headless su livelli di dimensioni diverse superato. |
| 2026-10-12 | *fedegugl* | **RISOLTO - PRIMO FRAME GHOST** : i nomi dei ghost erano assegnati solo al primo aggiornamento AI, ma letti dal renderer prima del primo update. Assegnati alla creazione in GamePage; primo draw headless superato senza fixture. |
| 2026-10-12 | *fedegugl* | **RISOLTO - HIGH SCORE/ERRORI ASSET** : highscore mancante o JSON corrotto non blocca l'avvio; record invalidi vengono ignorati singolarmente; errori di salvataggio usano logging. AssetError nel loop produce messaggio pulito senza traceback. Test headless dei casi d'errore superati. |
| 2026-10-12 | *fedegugl* | **RISOLTO - PACGUM SOTTO I GHOST** : il renderer nascondeva la gomma appena il ghost sceglieva la cella di destinazione, prima di raggiungerla visivamente. La gomma resta statica finché Pac-Man non la mangia; il ghost viene disegnato sopra. |
| 2026-10-12 | *fedegugl* | **RISOLTO - SUPER-PACGUM SPRITE** : le super-pacgum usano `super_pacgum_img` gia' scalata invece della pacgum normale ingrandita a dimensione fissa. Verificati asset distinti, centro cella comune e fallback in assenza dello sprite super. |
| 2026-10-12 | *fedegugl* | **RISOLTO - FALSE FRIGHTEN** : il punteggio positivo in una cella d'angolo (per esempio mangiando un ghost) riattivava il frighten anche senza consumare una super-pacgum. Rimosso il trigger duplicato: solo `PacgumsManagement.try_to_eat()` su una super-pacgum non mangiata attiva i ghost. Verificato con Data Debug attivo e disattivo. |
| 2026-10-12 | *fedegugl* | **RISOLTO - DATA DEBUG** : attivando il cheat dopo aver gia' mangiato almeno 10 gomme, il livello avanzava subito al resume. Il conteggio ora parte dal numero di gomme presenti all'attivazione e richiede 10 nuove gomme; baseline azzerata al livello successivo. Rimossa la scorciatoia menu `V` che apriva una vittoria fittizia. |
| 2026-10-12 | *fedegugl* | **RISOLTO - HUD LIVELLO** : aggiunto il livello corrente (numerazione da 1) accanto al timer usando bitmap font; il valore si aggiorna alla transizione di livello. Test headless superato. |
| 2026-10-12 | *fedegugl* | **RISOLTO - LIMITE FINESTRA** : applicato minimo pari all'80% della risoluzione desktop rilevata all'avvio. Il resize sotto soglia viene ripristinato senza overlay, evitando che il messaggio copra menu o gioco; routing verificato su tutte le scene e in pausa/cooldown. La conformita' usa solo API gia' presenti in `mlx_compliance.md`. |
| 2026-10-12 | *fedegugl* | **RISOLTO - ANIMAZIONE PLAYER/MLX** : generate sequenze PNG pre-orientate per le quattro direzioni nelle cartelle esistenti; rimosse rotazioni runtime. I frame ora avanzano con clock monotono in ciclo ping-pong, indipendente dal tile; posizione ancora interpolata. Ghost disegnati sopra il player in caso di overlap. Test frame, draw e type-check superati. |
| 2026-10-12 | *fedegugl* | **VERIFICATO - CENTRO MAZE / ASSET INTERSECTIONS** : il renderer posiziona le intersezioni sul centro geometrico del vertice della griglia. La discrepanza residua e' attribuita all'allineamento dei pixel nelle sprite, non al calcolo. |
| 2026-10-12 | *fedegugl* | **DA FARE - ALLINEAMENTO SPRITE MAZE** : allineare gli asset di intersezione e cornice double ai centri calcolati e poi ricontrollare visivamente in gioco. Punto rimandato all'ultimo step. |
| 2026-10-12 | *fedegugl* | **DA DISCUTERE - SCALING MLX** : animazione player collegata a PNG orientati, ma AssetManager ridimensiona ancora le immagini a runtime. Verificare il vincolo di scaling in `assets/mlx_compliance.md` e decidere gestione/asset alle dimensioni target. |
| 2026-10-13 | *fedegugl* | **RISOLTO - SCALING MLX / FLUIDITÀ** : scaling nearest-neighbor su buffer RGBA con NumPy, mapping centrato dei pixel e cache del logo per evitare resize nel loop frame. Rimosse le chiamate `pygame.transform.scale/smoothscale` e `pygame.key.set_repeat(200, 100)`. Verificata la grafica; equivalenze buffer, Info, flip e limiti endian/line_length documentati in `assets/mlx_compliance.md`. Punto specifico chiuso; non equivale alla certificazione dell'intero audit API Pygame/MLX. |
| 2026-10-13 | *fedegugl* | **ALLINEMANETO - collisioni GHOST** : collision_check() e stata aggiornata, piccoli bug impedivano delle collisioni in casi limite |
| 2026-10-13 | *fedegugl* | **RISOLTO - MOVIMENTO ANOMALO GHOST** : Aggiunta del metodo _resolve_single_step() per evutare movimenti diagonali dei ghost |
| 2026-10-13 | *fedegugl* | **BUG** : PRIMO BUTTONS in impostazioni delle impostazioni si attiva sempre senza input utente |
| 2026-10-13 | *fedegugl* | **BUG** : BUTTONS fullscreen si rompe sullo screen del pc della scuola |
| 2026-10-13 | *fedegugl* | **BUG RISOLTO - COLLISIONI** : IN diagonale i conti erano troppo permissivi, modificato overlap in pacman.py|
| 2026-10-13 | *fedegugl* | **MODIFICA - ghost** : quando sono in angolo per qualche secondo non provocano collisioni, permette a pacman di sopravvivere|
| 2026-10-14 | *fedegugl* | **MODIFICA - SUPERPACGUMS** : Aggiunta di un punteggio piu alto se la pacgums viene mangiata (allineamanto alla pagina istruzioni)|
| 2026-10-13 | *fedegugl* | **RESTRICTED FUNCTION FOUND - MACRO** : FULLSCREEN e VIDEORESIZE in coda rimozione macro rimanennti |
| 2026-10-14 | *fedegugl* | **RESTRICTED FUNCTION FOUND - GETSIZE()** : in coda rimozione Funzioni proibite rimaneti |
| 2026-10-14 | *fedegugl* | **RESTRICTED FUNCTION FOUND - get_ticks()** : in coda rimozione Funzioni proibite rimaneti |
| 2026-10-14 | *fedegugl* | **RESTRICTED FUNCTION FOUND - Rect** : in coda rimozione Funzioni proibite rimaneti |
| 2026-10-14 | *fedegugl* | **RESTRICTED FUNCTION FOUND - monotonic()** : in coda rimozione Funzioni proibite rimaneti |
| 2026-10-14 | *fedegugl* | **RIMOZIONE DEAD CODE** : _draw_too_small_hint RIMOSSA |
| 2026-10-14 | *fedegugl* | **BUG - GHOST** : se la pacgum viene presa nel momento in cui stiamo attuando il conto alla rovescia per il ritorno allo stato normale, l immagne rimane quella della sbagliata (quella del ending fear)|
| 2026-10-14 | *fedegugl* | **BUG - GHOST** : Nei livelli oltre quello 01 si verifica che lo stato fear a volte finisce senza passare dallo stato finale (quella del ending fear)|
| 2026-10-14 | *fedegugl* | **BUG - GHOST** : a cambio livello non fanno respaw immediato nelle loro postazioni|
| 2026-10-13 | *fedegugl* | **DECISIONE - UI** : Rimozione logica relativa al resume menu - Non abbiamo piu l' overlay |
| 2026-10-13 | *fedegugl* | **DECISIONE - MACRO** : FULLSCREEN tolta |
| 2026-10-14 | *gcerrete* | second pacgum bug, not flash ending, solved. |
| 2026-10-14 | *gcerrete* | On pacman death all ghost respawn to their corners. mypy error: pygame.surface vs pygame.surface.surface: solved. |
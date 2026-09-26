# Progect plan

## Settimana 1 — Fondamenta

### #1 — Setup repo e outillage [setup]

**Assegnato:** *fedegugl* *gcerrete*
**Descrizione:** Struttura repo, `.gitignore` Python, README scheletro, licenza se richiesta.
**Criteri di accettazione:**

- [x] Repo Git inizializzato con struttura cartelle (`src/`, `tests/`, `docs/project-management/`)
- [x] `.gitignore` esclude `__pycache__`, `.mypy_cache`, `venv/`, ecc.
- [x] README.md con prima riga italic richiesta dal subject

### #2 — Makefile [setup]

**Assegnato:** *fedegugl*
**Criteri di accettazione:**

- [ \X] `make install` installa dipendenze
- [X] `make run` lancia il gioco
- [X] `make debug` lancia con pdb
- [X] `make clean` rimuove cache
- [X] `make lint` esegue flake8 + mypy con i flag richiesti dal subject
- [X] `make lint-strict` (opzionale) con `--strict`

### #3 — Config flake8/mypy [setup]

**Assegnato:** *fedegugl*
**Criteri di accettazione:**

- [X] `setup.cfg` o `.flake8` con regole concordate
- [X] `mypy.ini` con i flag richiesti (`--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`)

### #4 — Verifica conformità libreria grafica (MLX-equivalente) [research]

**Assegnato:** *fedegugl* *gcerrete*
**Criteri di accettazione:**

- [X] Deciso: niente `pygame.font` avanzato → bitmap font o immagini pre-renderizzate
- [X] Deciso: audio sì/no e giustificazione
- [X] Spike di 1-2h: finestra + immagine + key hook funzionante

### #5 — Lettura interfaccia pacchetto A-Maze-ing [research]

**Assegnato:** *fedegugl*
**Criteri di accettazione:**

- [X] Pacchetto installato via `make install`
- [X] Documentate le funzioni/classi esposte (parametri `PERFECT`, `seed`, `width`, `height`)
- [X] Note su formato di output del labirinto (matrice? lista di celle? muri?)

### #6 — Adapter A-Maze-ing → formato interno [feature]

**Assegnato:** *fedegugl* *gcerrete*
**Dipende da:** #5
**Criteri di accettazione:**

- [X] Modulo `maze_loader.py` che chiama il pacchetto as-is
- [X] Conversione output in struttura dati interna (es. griglia 2D di celle wall/floor)
- [X] Gestione errore pulita se il generatore fallisce (no traceback)
- [X] `PERFECT=False` usato come richiesto

### #7 — Parser config JSON-con-commenti [feature]

**Assegnato:** *fedegugl*
**Criteri di accettazione:**

- [X] Supporta righe che iniziano con `#` come commenti
- [X] Parsing JSON standard altrimenti
- [X] Funzione riusabile, testata con file di esempio

### #8 — Validazione config + default robusti [feature]

**Assegnato:** *fedegugl*
**Dipende da:** #7
**Criteri di accettazione:**

- [X] Chiavi mancanti → default sicuro + log chiaro
- [X] Valori invalidi → clamp a default + log chiaro
- [X] Chiavi sconosciute ignorate silenziosamente
- [X] Nessun traceback in nessun caso testato

### #9 — Entry point CLI [feature]

**Assegnato:** *fedegugl*
**Dipende da:** #7, #8
**Criteri di accettazione:**

- [X] `python3 pac-man.py config.json` funziona
- [X] File mancante / non-JSON gestito con messaggio chiaro, no crash

### #10 — Rendering base labirinto [feature]

**Assegnato:** *fedegugl* *gcerrete*
**Dipende da:** #4, #6
**Criteri di accettazione:**

- [X] Finestra si apre e disegna muri/corridoi del labirinto generato
- [X] Usa solo funzioni conformi (da #4)

[GOAL] **Milestone settimana 1:** si lancia da CLI, si legge il config, si genera e disegna un labirinto (seed fisso).

---

## Settimana 2 — Gameplay core

### #11 — Player: movimento su griglia [feature]

**Assegnato:** *fedegugl*
**Criteri di accettazione:**

- [X] Movimento 4 direzioni con frecce/WASD
- [X] Collisione con muri (non ci passa attraverso)
- [X] Player parte al centro del labirinto

### #12 — Player: vite e respawn [feature]

**Assegnato:** *fedegugl* *gcerrete*
**Dipende da:** #11
**Criteri di accettazione:**

- [v] 3 vite iniziali (da config)
- [v] Perde vita se toccato da ghost
- [ ] Respawn al centro dopo perdita vita
- [ ] Game over quando vite = 0

### #13 — Ghosts: movimento autonomo [feature]

**Assegnato:** *gcerrete*
**Criteri di accettazione:**

- [x] 4 ghost, uno per angolo, si muovono nei corridoi autonomamente
- [x] Non attraversano muri

### #14 — Ghosts: comportamento chase [feature]

**Assegnato:** *gcerrete*
**Dipende da:** #13
**Criteri di accettazione:**

- [v] Almeno un comportamento definito (es. distanza euclidea verso player)
- [ ] Comportamento documentato nel README

### #15 — Ghosts: stato edible/eaten + respawn [feature]

**Assegnato:** *gcerrete*
**Dipende da:** #13, #14
**Criteri di accettazione:**

- [v] Ghost scappa quando edible
- [ ] Ghost mangiato torna al proprio angolo dopo N secondi (config)

### #16 — Pacgum: piazzamento e eating [feature]

**Assegnato:** *fedegugl* *gcerrete*
**Criteri di accettazione:**

- [X] Pacgum piazzati nella maggior parte dei corridoi
- [X] Eating rimuove il pacgum e aggiunge punti (da config)

### #17 — Super-pacgum: piazzamento e effetto [feature]

**Assegnato:** *gcerrete*
**Dipende da:** #15, #16
**Criteri di accettazione:**

- [X] Super-pacgum nei 4 angoli
- [ ] Eating rende i ghost edible per un tempo limitato
- [ ] Punti assegnati correttamente

### #18 — Scoring hook centrale [feature]

**Assegnato:** *gcerrete*
**Dipende da:** #16, #17
**Criteri di accettazione:**

- [ ] Un solo punto nel codice che aggiorna lo score (pacgum/super/ghost)
- [ ] Score non decresce mai

[GOAL] **Milestone settimana 2:** un livello è giocabile end-to-end (si può morire o vincere il livello).

---

## Settimana 3 — Loop di gioco e persistenza

### #19 — Macchina a stati del gioco [feature]

**Assegnato:** *fedegugl*
**Criteri di accettazione:**

- [X] Stati: Menu, Playing, Paused, GameOver, Victory
- [x] Transizioni pulite senza stati "fantasma"

### #20 — Main menu [feature]

**Assegnato:** *fedegugl*
**Dipende da:** #19
**Criteri di accettazione:**

- [X] Start Game / View Highscores / Instructions / Exit

### #21 — HUD in-game [feature]

**Assegnato:** *fedegugl*
**Criteri di accettazione:**

- [X] Score, vite, livello, tempo rimanente sempre visibili

### #22 — Pause menu [feature]

**Assegnato:** *fedegugl*
**Dipende da:** #19
**Criteri di accettazione:**

- [X] Resume / Torna al menu principale

### #23 — Game Over / Victory screen [feature]

**Assegnato:** *fedegugl*
**Dipende da:** #19
**Criteri di accettazione:**

- [v] Mostra score finale
- [v] Prompt inserimento nome giocatore

### #24 — Highscore system [feature]

**Assegnato:** *gcerrete*
**Criteri di accettazione:**

- [ ] Persistenza su file JSON
- [ ] Top 10 con nome + punteggio
- [ ] Nome: max 10 caratteri, alfanumerico + spazi
- [ ] Score: intero non-negativo
- [ ] Robusto a file mancante/corrotto (no crash)
- [ ] Load a inizio partita, save a fine partita

### #25 — Progressione multi-livello [feature]

**Assegnato:** *gcerrete* *fedegugl*
**Dipende da:** #6
**Criteri di accettazione:**

- [V] Almeno 10 livelli
- [V] Livello 1 con seed fisso (42), successivi random
- [V] Timer per livello (config `level_max_time`)
- [ ] Comportamento a timeout definito (es. restart livello)
- [ ] Score e vite mantenuti tra livelli

### #26 — Cheat mode [feature]

**Assegnato:** *gcerrete*
**Criteri di accettazione:**

- [v] Invincibilità
- [v] Skip livello
- [v] Freeze ghost
- [v] Extra vite
- [v] Attivabile facilmente (es. tasto dedicato), utile per peer review

[GOAL] **Milestone settimana 3:** loop completo Main Menu → gioco → vittoria/sconfitta → nome → highscore → menu.

---

## Settimana 4 — Robustezza, doc, packaging (07–11/09)

### #27 — Audit gestione errori [quality]

**Assegnato:** *fedegugl* *gcerrete*
**Criteri di accettazione:**

- [ ] Tutti i punti di I/O (file, config, maze package) in try/except
- [ ] Nessun crash riproducibile in nessun test manuale

### #28 — Type hints + mypy pulito [quality]

**Assegnato:** *fedegugl* *gcerrete*
**Criteri di accettazione:**

- [ ] `make lint` passa senza errori

### #29 — Docstring PEP 257 [quality]

**Assegnato:** *fedegugl* *gcerrete*
**Criteri di accettazione:**

- [ ] Tutte le funzioni/classi pubbliche documentate

### #30 — Test pytest [quality]

**Assegnato:** *fedegugl* *gcerrete*
**Criteri di accettazione:**

- [ ] Test su config parser (validi/invalidi)
- [ ] Test su highscore (edge case nomi/punteggi)
- [ ] Test su scoring

### #31 — README completo [docs]

**Assegnato:** *fedegugl*
**Criteri di accettazione:**

- [X] Prima riga italic con login richiesti
- [ ] Sezioni: Description, Instructions, Resources+AI, Configuration, Highscore, Maze Generation, Implementation, Architecture, Project Management
- [X] Scritto in inglese

### #32 — Packaging su piattaforma pubblica [deploy]

**Assegnato:** *gcerrete*
**Criteri di accettazione:**

- [ ] Build funzionante su itch.io (o Steam), unlisted/private
- [ ] Istruzioni minime incluse nel pacchetto
- [ ] Script/spec di packaging alla root del repo

### #33 — Cartella project management [docs]

**Assegnato:** *fedegugl* *gcerrete*
**Criteri di accettazione:**

- [X] Timeline/Gantt/Kanban
- [X] Progress tracking
- [X] Risk analysis
- [X] Team organization
- [X] Acceptance test plan
- [X] Sintesi blocchi/conflitti

### #34 — Mock defense [quality]

**Assegnato:** *fedegugl* *gcerrete*
**Criteri di accettazione:**

- [ ] Ognuno sa spiegare ogni modulo scritto dall'altro
- [ ] Prova di una "recode instruction" a sorpresa tra voi due

[GOAL] **Milestone finale:** progetto consegnabile, giocabile, documentato, senza crash noti.

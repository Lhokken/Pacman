"""Game specifications."""

from enum import Enum

# ===========================================================================
#   Chapter IV - Game specifications
# ===========================================================================
# ===========================================================================
#   ARCHITECTURE NOTE - CORE vs UI
# ===========================================================================
# This file is the gameplay orchestrator. It should be responsible for the
# game domain, not for presentation.
#
# Keep here:
#   - level creation and maze adaptation
#   - player/ghost/pacgum placement rules
#   - score, lives, timers, win/lose conditions
#   - progression between levels and match state transitions
#
# Keep out of here:
#   - pygame window creation
#   - screen resizing/layout
#   - rendering, widgets, fonts, and asset loading
#   - UI scene switching and visual drawing
#
# This separation is intentional: the UI layer decides how the game is shown,
# while the core/orchestrator decides how the game behaves.
#
# A page/scene may temporarily hold some gameplay state during development,
# but the long-term design should move that state into this core layer.
#

# ---------------------------------------------------------------------------
#  MESSAGGIO PRECEDENTE SU SLACK
# ---------------------------------------------------------------------------
# 1 `__init__`              : crea o riceve `GameManager`, `Renderer`,
#                             `UIManager`, `LayoutManager`;
# 2 `handle_events`         : inoltra a `InputManager` / `GameManager`;
# 3 `on_pause` / `on_resume`: delega a `GameManager`;
# 4 `update`                : chiama `game_manager.update()`;
# 5 `on_resize`             : delega a `LayoutManager`;
# 6 `draw`                  : chiama `renderer.draw()` e `ui_manager.draw()`.
#
# ===========================================================================

# ---------------------------------------------------------------------------
#  RESPONSIBILITY SPLIT
# ---------------------------------------------------------------------------
# UI layer: (quello che abbiamo in src/ui)
#   - draw maze, player, ghosts, HUD, panels
#   - handle window resize and scene transitions
#   - receive keyboard input and forward it to gameplay
#   - do not own gameplay rules or long-lived match state


class LevelNext:
    """Inizialmente pensato per src/core/game/game.py."""

    # ==========================================================
    #   Chapter IV - Game specifications
    # ==========================================================
    #   VI.7 Game progression
    # ----------------------------------------------------------
    # • The game consists of multiple levels (at least 10).
    # • Each level has a time limit (e.g., 90 seconds).
    # • If the time limit is reached, you can decide what happens
    #   (e.g., restart the level, end the game, etc.).
    # • If the player completes a level, they move to the next level.
    # • The player keeps their score and remaining lives between levels.
    # • The game ends when all levels are completed or when the player
    #   loses all lives.
    # • During the game, the player can pause and resume the game.
    # • When the game ends (win or lose), the final score is displayed,
    #   and the player canenter their name to save the highscore.
    # • After the game ends, the player is returned to the main menu
    # ----------------------------------------------------------

    # ==========================================================
    #   ARCHITECTURE NOTE - COSTRUISCI LV N
    # ==========================================================
    # 1. Adattarsi all'interfaccia di A-Maze-ing per ottenere la geometria
    # grezza muri e corridoi. Questa parte è vincolata dal V.4: non puoi
    # modificare il pacchetto, il tuo loader si adatta a lui. È puro
    # "adapter pattern": traduci l'output del pacchetto esterno in una
    # struttura che il resto del tuo gioco capisce.
    #
    # 2 Applicare le regole di popolamento specifiche di Pac-Man sopra quella
    # geometria: dove vanno i pacgum (nella maggior parte dei corridoi — non
    # tutti, quindi c'è una regola di distribuzione da decidere), dove i 4
    # super-pacgum (angoli), dove i 4 fantasmi (angoli), dove il player (cx).

    # ==========================================================
    # 1 `__init__` : crea o riceve da generatore esterno
    # ==========================================================

    # ==========================================================
    # 2. Cobfigurazione file json
    # ==========================================================

    # ==========================================================
    # 3. convesrione griglia
    # ==========================================================

    # 4. deve sapere dove sta il player
    # 5. deve sapere dove sta i ghost
    # 6. deve sapere tempo max (da json)
    # 7. deve sapere il seed (json ma poi lo cambiamo a lv 2)


class GameState(Enum):
    """Gestisce la logica che gia abbiamo in ui, va solo spostata."""

    # Noi abbiamo gi ala logica dello stato del game, non pensavo
    # fosse CORE related, dobbiamo spostare qui il codice, puoi
    # eliminare la calsse ma la logica dovrebbe rimanere la seguente
    MENU = 0
    PLAY = 1
    PAUSE = 3
    NEXT = 4
    WIN = 5
    LOSE = 6


class GameManager:
    """The gameplay orchestrator.

    It is responsible for the game domain, not for presentation.
    """

    # GameManager ----------------------------------------------
    #   - owns the actual match state
    #   - score, lives, level index, timer, win/lose conditions
    #   - updates gameplay logic each frame
    #   - does not draw the screen or own layout logic
    # ----------------------------------------------------------
    # ==========================================================
    #   Game play state
    # ==========================================================
    # ==========================================================
    # 1 `__init__` : crea o riceve `GameManager`, `Renderer`,
    #                `UIManager`, `LayoutManager`;
    # ==========================================================

    # ----------------------------------------------------------
    # 2 `handle_events`: inoltra a `InputManager` / `GameManager`
    # ----------------------------------------------------------
    # Handle input e ripetuto in tutte le pagine, va messo qui
    # e richiamato all occorrenza

    def handle_input(self):
        """Fa TODO: Docstring."""
        pass

    # ----------------------------------------------------------
    # 3 `on_pause` / `on_resume`: delega a `GameManager`;
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # 4 `update`                : chiama `game_manager.update()`
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # 5 `on_resize`             : delega a `LayoutManager`;
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # 6 `draw` : chiama `renderer.draw()` e `ui_manager.draw()`.
    # ----------------------------------------------------------
    def render(self):
        """Fa TODO: Docstring."""
        pass


class Orchestra:
    """Orchestra tutto quello sopra."""

    # Orchestrator ---------------------------------------------
    #   - owns the flow of the game
    #   - creates levels and transitions between them
    #   - decides when to pause, resume, advance, finish or restart
    #   - coordinates the lifecycle of the whole game session
    # ----------------------------------------------------------
    # ==========================================================
    #   Flusso e ciclo della partita
    # ==========================================================
    # 1. crea livello
    # 2. avanza livello
    # 3. controllo status game (vittoria o game over)
    # 4. aggiornare score vite
    # 5. cabiare stat del gioco

# --------------------------------------------------------------------------
#  PROJECT NOTE: CURRENT MIXED RESPONSIBILITIES
# --------------------------------------------------------------------------
# Today the game page is doing too much at once. In the current UI code we
# still find:
#   - maze creation
#   - player and ghost spawning
#   - pacgum generation and scoring
#   - timer management
#   - frame-by-frame state update
#   - scene transitions and pause logic
#
# These are gameplay responsibilities and should live in the core/orchestrator.
# The UI page should instead only own:
#   - asset/font loading
#   - responsive layout and screen metrics
#   - event handling for keys/window resize
#   - rendering of the current state
#   - HUD/panels drawing
#
# In short: UI = present the state; Core = own the state and rules.

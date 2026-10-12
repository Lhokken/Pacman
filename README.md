# Pac-Man: Architecture and UI Components

A modular, clean, and extensible Python re-creation of the classic **Pac-Man** arcade game built with Pygame and customized for 42 School. The project features dynamic maze generation, configurable level rules, custom ghost AI, bitmap font rendering, responsive UI layouts, and structured command-line interface (CLI) error handling.

---

## Table of Contents
- [Description](#description)
- [Instructions](#instructions)
- [Resources](#resources)
- [Configuration](#configuration)
- [Highscore](#highscore)
- [Maze Generation](#maze-generation)
- [Implementation](#implementation)
- [General Software Architecture](#general-software-architecture)

---

## Description

**Pac-Man: Architecture and UI Components** is a software project developed to deliver an authentic, scalable, and fully configurable Pac-Man gameplay experience. The primary goal of the project is to combine low-level game mechanics (tile-based movement, BFS pathfinding for ghosts, dead-end removal, power pellets) with a robust UI architecture featuring custom layout math, screen responsiveness, and decoupled scene management.

### Key Features
- **Dynamic Maze Generation:** Procedurally generated mazes with dead-end removal (`braid`) and embedded "42" logo wall patterns.
- **Configurable Gameplay:** JSON configuration file support for lives, points, level counts, maze dimensions, seeds, and level timers.
- **Custom Ghost AI:** Four distinct ghosts (Blinky, Pinky, Inky, Clyde) implementing state transitions between `NORMAL` (chasing/hunting), `FRIGHTENED` (fleeing), and `EATEN` (respawning via BFS).
- **Pure Surface Rendering & Bitmap Fonts:** Pixel-perfect UI rendering powered by custom PNG glyph bitmap fonts without relying on TTF engine abstractions.
- **Robust CLI & Validation:** Strict command-line validation and JSON comment-stripping parser that gracefully reports errors without dumping raw Python tracebacks.

---

## Instructions

### Prerequisites
- **Python:** Python 3.8 or higher.
- **Pygame:** Version 2.0 or higher.

To install Pygame on your system:
```bash
pip install pygame
```

### Installation
Clone the repository and navigate into the project root directory:
```bash
git clone <repository_url>
cd pac-man
```

### Execution
The game requires exactly one positional command-line argument: the path to a valid `.json` configuration file.

```bash
python3 pac-man.py config.json
```

#### Debug Mode
To enable full Python stack tracebacks and verbose logging during development or testing, run with the `PACMAN_DEBUG` environment variable set to `1`:
```bash
PACMAN_DEBUG=1 python3 pac-man.py config.json
```

---

## Resources

### References
- **Pac-Man Dossier (Jammag):** Comprehensive reference on original arcade Pac-Man timings, ghost targeting logic, and cell mechanics.
- **Pygame Documentation:** Surface blitting, event handling, sprite transformation, and display scaling API references.
- **Breadth-First Search (BFS) Pathfinding:** Standard graph search algorithms for grid-based pathfinding and shortest path calculation.
- **42 School Project Specifications:** Normative requirements regarding modular design, defensive error handling, and clean CLI architecture.

### AI Usage Description
Artificial Intelligence tools were utilized as a collaborative assistant during specific software engineering tasks:
1. **Refactoring & Code Quality:** AI assisted in analyzing layout ratio calculations and standardizing docstrings across UI modules (`GameLayout`, `MenuLayout`, `PauseLayout`).
2. **Defensive Logic & Edge Cases:** Assisted in auditing post-validation checks (e.g., cross-field validation of pacgum count vs. walkable maze area) and boundary handling.
3. **Documentation:** Generating technical summaries, architecture diagrams, and structuring the `README.md` file based on codebase static analysis.

---

## Configuration

The application loads its parameters from a JSON configuration file. Lines starting with `#` are automatically stripped as comments prior to parsing.

### Configuration Structure & Defaults

| Key | Type | Default | Valid Range / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `lives` | `int` | `3` | `1` to `99` | Starting lives for Pac-Man. |
| `seed` | `int` | `42` | `0` to `2^32 - 1` | Random seed for reproducible maze generation. |
| `pacgum` | `int` | `42` | `0` to `1000` | Target pacgum threshold per level. |
| `points_per_pacgum` | `int` | `10` | `0` to `100,000` | Score awarded per small pac-gum eaten. |
| `points_per_super_pacgum` | `int` | `50` | `0` to `100,000` | Score awarded per super pac-gum (power pellet). |
| `points_per_ghost` | `int` | `200` | `0` to `100,000` | Score awarded when eating a frightened ghost. |
| `level_max_time` | `int` | `90` | `1` to `3600` (seconds) | Duration allowed per level before game over. |
| `highscore_filename` | `string` | `"highscores.json"` | Non-empty `.json` string | File path used for saving and loading top scores. |
| `levels` | `array` | `[{"width": 21, "height": 21}]` | Minimum 10 levels required | List of objects defining level dimensions (`width` x `height`, min `5x5`). |

### Example `config.json`
```json
{
  # Game settings
  "lives": 3,
  "seed": 42,
  "pacgum": 42,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "level_max_time": 180,
  "highscore_filename": "highscores.json",
  "levels": [
    { "width": 21, "height": 21 },
    { "width": 21, "height": 21 },
    { "width": 23, "height": 23 },
    { "width": 23, "height": 23 },
    { "width": 25, "height": 25 },
    { "width": 25, "height": 25 },
    { "width": 27, "height": 27 },
    { "width": 27, "height": 27 },
    { "width": 29, "height": 29 },
    { "width": 29, "height": 29 }
  ]
}
```

---

## Highscore

### Mechanism
The highscore system persists player achievements locally across game sessions:
1. **Loading:** Upon boot, `GameEntry` reads the designated file (`highscore.txt` / `highscores.json`). It validates entries to ensure scores are non-negative integer values. Valid entries are populated into `GameApp.HIGHSCORE` as `(name, score)` tuples.
2. **Name Entry:** Upon reaching `GameOverPage` or `VictoryPage`, players are prompted to enter a 1 to 5 character alphanumeric name using fixed slot rendering and interactive cursor guidance.
3. **Saving & Capping:** Submitting a score appends the record to `GameApp.HIGHSCORE`, sorts the entries in descending order by score, clamps the array to the top 10 positions, and serializes the leaderboard back to disk.

### Design Rationale
- **Lightweight File Persistence:** Storing scores as simple JSON structures avoids database overhead while remaining human-readable and easy to inspect or reset.
- **Top 10 Capping:** Restricting the leaderboard to 10 entries guarantees instant sorting/serialization performance and cleanly aligns with the static 10-row `HighScorePage` UI layout.
- **Fail-Safe Integrity:** Invalid or corrupted records trigger fallback warnings without causing application crashes, ensuring robust player experience.

---

## Maze Generation

Maze generation is managed by the custom `MazeGenerator` class.

### Generation Pipeline
1. **Empty Grid Initialization:** Constructs an initial grid enclosed by perimeter wall bitmasks.
2. **'42' Logo Embedding:** Inscribes the "42" pattern into the center of the grid, converting designated cells into solid walls (`mask = 15`) to serve as a signature central obstacle.
3. **Iterative Depth-First Carving:** Carves corridors using an explicit stack-based DFS traversal. Using an explicit stack instead of recursion prevents Python recursion limit exceptions (`RecursionError`) on large mazes.
4. **Braiding (Dead-End Elimination):** In standard mode (`perfect=False`), the `_braid()` method identifies dead-ends (cells with 3 surrounding walls) and carves an additional opening to adjacent non-obstacle cells. This creates loops, guaranteeing that Pac-Man is never trapped in a dead-end corridor.
5. **Solvability & Path Calculation:** Executes a Breadth-First Search (`_find_short_path`) from entry to exit to calculate the shortest path string (e.g. `"NNEESW"`) and confirm that the maze is fully navigable.

---

## Implementation

### Tile-Based Responsive Rendering
The maze layout is represented as a 2D matrix of integer wall bitmasks (`WALL_TOP=1`, `WALL_RIGHT=2`, `WALL_BOTTOM=4`, `WALL_LEFT=8`).
- `GameLayout` computes column widths and calculates an optimal `tile_size` based on screen dimensions and padding constraints.
- `MazeRenderer` queries preloaded tile surfaces from `AssetManager` (intersections, single walls, double outer borders) to assemble the visual maze dynamically.

### Movement & Waypoint Interpolation
- Pac-Man and ghosts transition between grid cells over fixed duration windows (`MOVE_DURATION_MS`).
- Renderers calculate smooth sub-pixel rendering coordinates (`_player_pixel_state`, `_build_ghost_infos`) using linear time interpolation between `from_col/row` and `to_col/row`.

### Ghost Behavior & AI
Each ghost maintains an independent state (`NORMAL`, `FRIGHTENED`, `EATEN`):
- **Hunting (`NORMAL`):** Uses BFS pathfinding combined with a random perturbation factor (`rand`) to target Pac-Man while introducing unpredictable movement patterns.
- **Fleeing (`FRIGHTENED`):** Calculates escape directions opposing Pac-Man's current position (`get_flight_run`).
- **Eaten (`EATEN`):** Executes BFS pathfinding to navigate back to its designated corner cell for immediate respawn.

### Custom Bitmap Font System
To maintain MLX compliance and eliminate external font dependencies:
- `BitmapFont` loads individual PNG glyphs organized in color directories (`bianco`, `giallo`).
- Text rendering blits pre-scaled sprite glyphs onto transparent Pygame surfaces without using `pygame.font.Font`.

---

## General Software Architecture

The codebase follows a modular architecture separating CLI orchestration, core game logic, resource management, layout metrics, and scene rendering.

```
pac-man/
├── pac-man.py                   # Main entry point & boot sequence (GameEntry)
├── src/
│   ├── cli/                     # Command-line interface orchestration & validation
│   │   ├── cli.py               # CLIApplication orchestrator
│   │   ├── cli_args_parser.py   # Argument parser (_NoExitArgumentParser)
│   │   ├── cli_validator_input.py # Input path & JSON validator
│   │   ├── cli_error_handler.py # Central error handler (traceback suppression)
│   │   └── cli_exceptions.py    # CLI exception hierarchy & exit codes
│   │
│   ├── core/                    # Core gameplay engine & configuration parsing
│   │   ├── timer.py             # Monotonic time countdown manager
│   │   ├── parsing/
│   │   │   ├── parsey.py        # ConfigLoader & GameConfig JSON parser
│   │   │   ├── parser_validator.py # PostValidation cross-field checks
│   │   │   └── parser_exceptions.py # Custom configuration exceptions
│   │   ├── entities/
│   │   │   ├── pacman.py        # PacmanPlayer movement & collision logic
│   │   │   ├── ghost.py         # GhostBase AI states & pathfinding (BFS)
│   │   │   ├── pacgums.py       # PacgumsManagement (pellet tracking)
│   │   │   └── entity_exceptions.py # Core entity exceptions
│   │   └── mazegenerator.py     # Procedural maze generator & braiding
│   │
│   └── ui/                      # Presentation layer & Pygame UI
│       ├── app.py               # GameApp main loop & scene manager
│       ├── scene.py             # Scene base class (lifecycle hooks)
│       ├── components/          # Reusable UI widgets
│       │   ├── bitmap_font.py   # PNG glyph font renderer
│       │   ├── button.py        # Keyboard-navigable text button
│       │   ├── hud.py           # In-game countdown HUD
│       │   └── panels.py        # Side panels (Score, Lives, Highscore, Logo)
│       ├── layout/              # Pure math layout calculators
│       │   ├── game_layout.py   # 3-column responsive screen layout
│       │   ├── game_page_layout.py # GamePage metrics wrapper
│       │   ├── menu_layout.py   # Main menu block positioning
│       │   ├── pause_layout.py  # Pause menu layout
│       │   ├── cheat_layout.py  # Settings menu layout
│       │   ├── end_screen_layout.py # Victory/GameOver page metrics
│       │   ├── hight_score_layout.py # Highscore table layout
│       │   └── instructions_layout.py # Instruction page metrics
│       ├── managers/            # Asset, Font, and Panel lifecycle managers
│       │   ├── asset_manager.py # Sprite loading, caching, and scaling
│       │   ├── font_manager.py  # Preset bitmap font instance registry
│       │   ├── panel_manager.py # Side panel orchestration
│       │   └── asset_exceptions.py # Asset loading exceptions
│       ├── pages/               # Game scene screens
│       │   ├── main_menu.py     # MainMenu scene
│       │   ├── game_page.py     # Active gameplay scene
│       │   ├── pause_menu.py    # Pause menu scene
│       │   ├── cheat.py         # Cheat & settings scene
│       │   ├── Instruction_page.py # Instructions scene
│       │   ├── hight_score.py   # HighScorePage scene
│       │   └── end_screen.py    # EndScreenPage (GameOverPage & VictoryPage)
│       └── renderers/           # Specialized drawing delegation
│           ├── renderer.py      # Static rendering helper methods
│           ├── maze_renderer.py # Tile-based maze rendering
│           └── entity_renderer.py # Pac-Man, Ghost, & Pellet renderers
```

### Key Subsystem Relationships

1. **Boot Sequence:** `pac-man.py` (`main`) → `CLIErrorHandler.run()` → `GameEntry.run()` → `CLIApplication.run()` parses CLI args, validates path via `CLIValidator`, loads JSON via `ConfigLoader`, runs `PostValidation`, and initializes `GameApp`.
2. **Scene & State Management:** `GameApp` maintains the active `Scene` (`current_scene`). Scene transitions occur via `app.switch_scene()`, which executes lifecycle hooks (`on_pause`, `on_resize`, `on_resume`).
3. **Gameplay Loop (`GamePage`):**
   - **Events:** Keyboard inputs are forwarded to `PacmanPlayer.handle_event()`.
   - **Update:** `GamePage.update()` advances player movement, updates ghost timers/AI (`GhostBase.team_ghost()`), checks pellet consumption (`PacgumsManagement.try_to_eat()`), updates side panels (`PanelManager`), and monitors win/loss conditions (`VictoryPage`/`GameOverPage`).
   - **Draw:** Delegated to `MazeRenderer.draw()` for grid rendering, `EntityRenderer.draw()` for player and pellets, `EntityRenderer.draw_ghosts()` for animated ghosts, `PanelManager.draw()` for UI side panels, and `HUD.draw()` for level time tracking.

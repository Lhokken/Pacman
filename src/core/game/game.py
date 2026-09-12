"""IL GAME LOOP PRNCIPALE.

Controllo dello stato corrente  e delega update/draw allo stato attivo

il gam e sis truttura tramite l orchestatore che produce ogni livello
gestendo ogni livello della
"""

# ===========================================================================
#   Chapter IV - Game specifications
# ===========================================================================
#   VI.7 Game progression
# ---------------------------------------------------------------------------
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

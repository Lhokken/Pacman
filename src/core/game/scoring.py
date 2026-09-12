"""Scoring."""
# ==========================================================================
#   Chapter IV - Mandatory part
# ==========================================================================
#   V.5 Highscore system
# --------------------------------------------------------------------------

# You must implement a persistent highscore system.
# The exact implementation is up to you, but document it in the README.
# It must:
# • Be stored as you choose (e.g., json file on project, on disk, etc.).
# • Be robust to file errors (missing file, invalid format, etc.).
# • Handle player names (max 10 characters, alphanumeric and spaces only).
# • Handle scores (non-negative integers)
# • Keep the top 10 highscores, with player names and scores.
# • Load highscores at game start and save them at game end.
# • Allow players to enter their name when they end the game (win or lose).
# • Display highscores in the main menu.

# ===========================================================================
#   Chapter IV - Game specifications
# ===========================================================================
# - VI.6 Scoring
# ---------------------------------------------------------------------------
# • The score increases when:
#   ◦ Eating a pacgum (+X points).
#   ◦ Eating a super-pacgum (+Y points).
#   ◦ Eating an edible ghost (+Z points).
# • The score does not decrease.

# ABSTRACT CALAS PER PUNTI + CLASSI COLLEGATE

# --------------------------------------------------------------------------
# Punti base
# --------------------------------------------------------------------------

# Nel labirinto ci sono 244 punti e Pac-Man deve mangiarli tutti per passare
# al round successivo:

#   - I 240 punti piccoli valgono 10 punti ciascuno
#   - I 4 punti grandi e lampeggianti, meglio conosciuti come energizzanti
#     valgono 50 punti ciascuno.

# Questo permette di ottenere un totale di 2.600 punti.

# --------------------------------------------------------------------------
# Punti extra
# --------------------------------------------------------------------------

# FIRST METHOD -------------------------------------------------------------
#
# Ogni volta che Pac-Man mangia uno dei quattro punti energizzanti:
#
#   - Il primo fantasma catturato dopo essere stato mangiato vale sempre
#     200 punti
#
#   - Ogni fantasma aggiuntivo catturato dallo stesso energizzatore varrà
#     il doppio dei punti rispetto al precedente: 400, 800 e 1.600 punti,
#     rispettivamente.
#
#   - Se tutti e quattro i fantasmi vengono catturati presso tutti e quattro
#     gli energizzatori, si possono guadagnare ulteriori 12.000 punti in questi
#     primi livelli.
#
#   il "tempo blu" dei fantasmi si ridurrà a uno o due secondi al massimo,
#   rendendo molto più problematico catturarli tutti e quattro prima che scada
#   il tempo su questi tabelloni. 19 lv non piu disponibile

# SECOND METHOD -------------------------------------------------------------

# Il secondo modo per aumentare il punteggio in ogni round è mangiare i simboli
# bonus che appaiono direttamente sotto il recinto dei mostri due volte pe
# round per ottenere punti aggiuntivi:

#   - Il primo frutto bonus appare dopo aver eliminato 70 punti dal labirinto
#   - il secondo appare dopo averne eliminati 170. Ogni frutto vale da 100 a
#     5.000 punti, a seconda del livello in cui il giocatore si trova.
#
#  Ogni volta che appare un frutto, il tempo in cui rimane sullo schermo prima
#  di scomparire è sempre compreso tra nove e dieci secondi. La durata esatta
#  è variabile e non diventa prevedibile con l'uso di schemi. Questo di solito
#  passa inosservato, dato che la maggior parte degli schemi è progettata per
#  mangiare il frutto bonus il più velocemente possibile dopo che è stato
#  attivato per apparire.

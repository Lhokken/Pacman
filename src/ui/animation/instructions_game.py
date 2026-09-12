"""Attract animation for the Intro / Title page.

Ghosts chase Pac-Man and everyone exits off the right edge, in loop.
"""

from __future__ import annotations

from pygame.surface import Surface
from src.ui.animation.base_animation import AnimationScene


class IstructionPage(AnimationScene):
    """Presentation of animation in Inastruction page.

    parade -> eating -> info
    """

    # =======================================================================
    #   Timings (in frames at 60 FPS)
    # =======================================================================
    STATE0_DURATION = 180              # 3 seconds for character presentation
    PARADE_SPEED = 3.0                 # Parade speed (pixels per frame)
    PACMAN_SPEED = 4.0                 # Pacman speed (pixel for frame)
    EAT_PAUSE_FRAMES = 10              # Pause before next ghost
    FLOATING_SCORE_LIFE = 90           # Floating Score

    # Private Methods--------------------------------------------------------
    # =======================================================================
    #   Animation setup
    # =======================================================================
    def _reset_animation(self) -> None:
        """Reset all entities to their initial positions and state."""
        # Ghost static images (list of 4 Surfaces, may be None) -------------
        self.ghost_imgs = self.assets.ghost_images
        self.pacman_imgs = self.assets.player_frames        # walk cycle
        self.pacman_img = self.assets.player_img            # static fallback
        # -------------------------------------------------------------------
        #   DATA
        # -------------------------------------------------------------------
        #   Ghost data ------------------------------------------------------
        ghost_info = [
            {
                "name": "BLINKY",
                "nickname": "Shadow",
                "x": 180,
                "score": 200
            },
            {
                "name": "PINKY",
                "nickname": "Speedy",
                "x": 340,
                "score": 400
            },
            {
                "name": "INKY",
                "nickname": "Bashful",
                "x": 500,
                "score": 800
            },
            {
                "name": "CLYDE",
                "nickname": "Pokey",
                "x": 660,
                "score": 1600
            },
        ]

        #   Ghost info -----------------------------------------------------
        self.ghosts: list[dict] = []
        for i, info in enumerate(ghost_info):
            img = self.ghost_imgs[i] if i < len(self.ghost_imgs) else None
            self.ghosts.append({
                "img": img,
                "name": info["name"],
                "nickname": info["nickname"],
                "target_x": info["x"],
                "score": info["score"],
                "x": -100,
                "y": self.screen_height // 2,
                "reached": False,
                "eaten": False,
            })

        #   Pac-Man data ---------------------------------------------------
        self.pacman = {
            "x": -50,
            "y": self.screen_height // 2,
            "target_x": 0,
            "moving": False,
            "frame_idx": 0,
            "frame_timer": 0,
        }

        #   Floating scores ------------------------------------------------
        self.floating_scores: list[dict] = []

        # ------------------------------------------------------------------
        #   State machine
        # ------------------------------------------------------------------
        # 0: presentation, 1: parade, 2: eating, 3: info
        self.state = 0
        self.timer = 0
        self.eat_index = 0

    # Private methods -------------------------------------------------------
    # =======================================================================
    #   LOGICA UPDTE
    # =======================================================================
    def _update_state(self) -> None:
        """Title.

        TODO: Inserisci descrizione.
        """
        self.timer += 1
        # ------------------------------------------------------------------
        #   STATE 0: Character presentation
        # ------------------------------------------------------------------
        if self.state == 0:
            if self.timer >= self.STATE0_DURATION:
                self.state = 1
                self.timer = 0

        # ------------------------------------------------------------------
        #   STATE 1: Ghost parade
        # ------------------------------------------------------------------
        elif self.state == 1:
            all_reached = True
            for g in self.ghosts:
                if not g["reached"]:
                    if not self._move_entity(g, self.PARADE_SPEED):
                        all_reached = False
                    else:
                        g["reached"] = True
            if all_reached and self.timer > 60:  # 1 second pause
                self.state = 2
                self.timer = 0
                self.eat_index = 0
                # Move Pac-Man to first ghost
                self.pacman["target_x"] = self.ghosts[0]["x"]
                self.pacman["moving"] = True

        # ------------------------------------------------------------------
        #   STATE 2: Eating ghosts
        # ------------------------------------------------------------------
        elif self.state == 2:
            # --------------------------------------------------------------
            # Move Pac-Man if needed
            # --------------------------------------------------------------
            if self.pacman["moving"]:
                if self._move_entity(self.pacman, self.PACMAN_SPEED):
                    self.pacman["moving"] = False
                    # Eat current ghost
                    current = self.ghosts[self.eat_index]
                    if not current["eaten"]:
                        current["eaten"] = True
                        # Create floating score
                        self.floating_scores.append({
                            "x": current["x"],
                            "y": current["y"] - 30,
                            "text": str(current["score"]),
                            "life": self.FLOATING_SCORE_LIFE,
                        })
                        # Prepare next ghost
                        if self.eat_index + 1 < len(self.ghosts):
                            self.eat_index += 1
                            self.pacman["target_x"] = (
                                self.ghosts[self.eat_index]["x"]
                            )
                            self.pacman["moving"] = True
                            self.timer = 0
                        else:
                            # All eaten, move to info state after delay
                            self.state = 3
                            self.timer = 0
            # -----------------------------------------------------------------
            #   Update floating scores
            # -----------------------------------------------------------------
            for score in self.floating_scores[:]:
                score["y"] -= 1.5
                score["life"] -= 1
                if score["life"] <= 0:
                    self.floating_scores.remove(score)

            # -----------------------------------------------------------------
            #   Update Pac-Man animation frames
            # -----------------------------------------------------------------
            self.pacman["frame_timer"] += 1
            if self.pacman["frame_timer"] > 5:
                self.pacman["frame_timer"] = 0
                self.pacman["frame_idx"] = (
                    (self.pacman["frame_idx"] + 1) % len(self.pacman_imgs)
                )

        # ------------------------------------------------------------------
        #   STATE 3: Info and credits
        # ------------------------------------------------------------------
        elif self.state == 3:
            # After 5 seconds, restart animation
            if self.timer > 300:
                self._reset_animation()

        # Always update floating scores if in state 2 (already done above)
        # But also needed if state transitions out of 2, so keep above.

    # commento logica -------------------------------------------------------
    def _update_eating(self) -> None:
        """Title.

        TODO: Inserisci descrizione.
        """
        if self.pacman["moving"]:
            if self._move_entity(self.pacman, self.PACMAN_SPEED):
                self.pacman["moving"] = False
                current = self.ghosts[self.eat_index]
                if not current["eaten"]:
                    current["eaten"] = True
                    self.floating_scores.append({
                        "x": current["x"],
                        "y": current["y"] - 30,
                        "text": str(current["score"]),
                        "life": self.FLOATING_SCORE_LIFE,
                    })
                    if self.eat_index + 1 < len(self.ghosts):
                        self.eat_index += 1
                        self.pacman["target_x"] = (
                            self.ghosts[self.eat_index]["x"]
                        )
                        self.pacman["moving"] = True
                        self.timer = 0
                    else:
                        self.state, self.timer = 3, 0

        for score in self.floating_scores[:]:
            score["y"] -= 1.5
            score["life"] -= 1
            if score["life"] <= 0:
                self.floating_scores.remove(score)

        self.pacman["frame_timer"] += 1
        if self.pacman["frame_timer"] > 5 and self.pacman_imgs:
            self.pacman["frame_timer"] = 0
            self.pacman["frame_idx"] = (
                (self.pacman["frame_idx"] + 1) % len(self.pacman_imgs)
            )

    # =======================================================================
    #   DRAW PARADE
    # =======================================================================
    #   State Scene --------------------------------------------------------
    def _draw_state(self, screen: Surface) -> None:
        """Title.

        TODO: Inserisci descrizione.
        """
        if self.state == 0:
            self._draw_presentation(screen)
        elif self.state == 1 or self.state == 2:
            self._draw_parade_and_eat(screen)
        elif self.state == 3:
            self._draw_info(screen)
        if self.state == 2:
            self._draw_floating_scores(screen)

    #   commento logica ----------------------------------------------------
    def _draw_presentation(self, screen: Surface) -> None:
        """State 0: show ghost images with nickname and name."""
        # ------------------------------------------------------------------
        # Title
        # ------------------------------------------------------------------
        title = self.font_big.render("CHARACTERS")
        screen.blit(title, title.get_rect(center=(self.screen_width // 2, 60)))

        # ------------------------------------------------------------------
        # Ghosts in a row
        # ------------------------------------------------------------------
        for i, g in enumerate(self.ghosts):

            # commento -----------------------------------------------------
            x = 150 + i * 160
            y = 250
            if g["img"]:
                rect = g["img"].get_rect(center=(x, y))
                screen.blit(g["img"], rect)

            # Nickname and name --------------------------------------------
            nick = self.font_big.render(g["nickname"])
            screen.blit(nick, nick.get_rect(center=(x, y + 50)))
            name = self.font_title.render(g["name"])
            screen.blit(name, name.get_rect(center=(x, y + 80)))
        # ------------------------------------------------------------------
        # Instruction hint
        # ------------------------------------------------------------------
        hint = self.font_white.render("Press ESC to return to menu")
        screen.blit(
            hint,
            hint.get_rect(
                center=(self.screen_width // 2, self.screen_height - 40)
            ),
        )

    # ----------------------------------------------------------------------
    #    DRAW PARADE
    # ----------------------------------------------------------------------
    def _draw_parade_and_eat(self, screen: Surface) -> None:
        """State 1/2: draw moving ghosts and Pac-Man."""
        # Draw ghosts (skip eaten ones)
        for g in self.ghosts:
            if g["eaten"]:
                continue
            if g["img"]:
                rect = g["img"].get_rect(center=(int(g["x"]), int(g["y"])))
                screen.blit(g["img"], rect)
        # ------------------------------------------------------------------
        # Draw Pac-Man (if on screen)
        # ------------------------------------------------------------------
        p = self.pacman
        if p["x"] > 0:
            frame = (self.pacman_imgs[p["frame_idx"] % len(self.pacman_imgs)]
                     if self.pacman_imgs else self.pacman_img)
            if frame:
                screen.blit(frame, frame.get_rect(
                    center=(int(p["x"]), int(p["y"]))))

        text = self.font_white.render("Pac-Man eats ghosts for points!")
        screen.blit(text, text.get_rect(
            center=(self.screen_width // 2, self.screen_height - 50)))

        # ------------------------------------------------------------------
        # Optional: display "Pac-Man eats ghosts for points!"
        # ------------------------------------------------------------------
        text = self.font_white.render("Pac-Man eats ghosts for points!")
        screen.blit(
            text,
            text.get_rect(
                center=(self.screen_width // 2, self.screen_height - 50)
            ),
        )

        # LASCIARE ESC INDICAZIONE TORNARE AL MENU
        #   EATS GHOST FOR POINT
        #   Descrizione animazione:
        #   pacman ragiunge il power gum alla fine della linea
        #   i ghist diventano spaventati e tornano indietro
        #   mentre i ghost tornano indietri e lui li insege e li
        #   mangia
        #   PREMI ESC PER TORNARE AL MENU
        # TODO: creare una sequenza separata in cui Pac-Man viene inseguito
        # TODO: usare la sequenza di inseguimento come animazione del MainMenu
        # TODO: fare in modo che la sequenza del menu possa ripartire in loop
        # TODO: permettere il disegno dell'animazione dentro un'area limitata

    # ----------------------------------------------------------------------
    #    DRAW PARADE
    # ----------------------------------------------------------------------
    def _draw_floating_scores(self, screen: Surface) -> None:
        """ Draw floating scores on top of everything.
          (only in state 2)
        """
        for score in self.floating_scores:
            alpha = min(255, score["life"] * 4)
            surf = self.font_big.render(score["text"])
            surf.set_alpha(alpha)
            rect = surf.get_rect(center=(score["x"], score["y"]))
            screen.blit(surf, rect)

    #   commento logica ----------------------------------------------------
    def _draw_info(self, screen: Surface) -> None:
        """State 3: show pacgum, super-pacgum, and credits."""
        # ------------------------------------------------------------------
        # Title
        # ------------------------------------------------------------------
        title = self.font_big.render("SCORE POINTS")
        screen.blit(
            title, title.get_rect(center=(self.screen_width // 2, 80))
        )

        # ------------------------------------------------------------------
        # Pacgum
        # ------------------------------------------------------------------
        if self.assets.pacgum_img:
            img = self.assets.pacgum_img
            x = self.screen_width // 2 - 100
            y = 200
            screen.blit(img, img.get_rect(center=(x, y)))
            label = self.font_white.render("10 pts")
            screen.blit(label, label.get_rect(center=(x + 120, y)))

        # ------------------------------------------------------------------
        #   Super-pacgum
        # ------------------------------------------------------------------
        if self.assets.super_pacgum_img:
            y = 300
            screen.blit(self.assets.super_pacgum_img,
                        self.assets.super_pacgum_img.get_rect(center=(x, y)))
            label = self.font_white.render("50 pts")
            screen.blit(label, label.get_rect(center=(x + 120, y)))

        # ------------------------------------------------------------------
        #   Bonus Fruits
        # ------------------------------------------------------------------
        #   TODO: Mettere la cherry

        # ------------------------------------------------------------------
        #   Credits
        # ------------------------------------------------------------------
        credits = self.font_white.render("Created for 42 Pac-Man project")
        screen.blit(
            credits,
            credits.get_rect(center=(self.screen_width // 2, 450)),
        )

        # ------------------------------------------------------------------
        #   Hint
        # ------------------------------------------------------------------
        hint = self.font_white.render("ESC to return to menu")
        screen.blit(
            hint,
            hint.get_rect(
                center=(self.screen_width // 2, self.screen_height - 40)
            ),
        )

"""
GameEngine: owns the basket and all falling objects.

Catch detection requires the object to reach basket height, the basket
stays fully on screen, spawning is varied and capped, and Space triggers
a temporary basket speed boost.
"""

import random
import pygame

from game.basket import Basket
from game.falling_object import FallingObject
from game.collision import is_caught
from game.renderer import WIDTH, HEIGHT

SPAWN_MIN_FRAMES = 30
SPAWN_MAX_FRAMES = 75
MAX_OBJECTS = 6
MIN_SPAWN_SEPARATION = 60   # min horizontal distance from the previous spawn
SPAWN_MARGIN = 20
MAX_MISSES = 5


class GameEngine:
    def __init__(self):
        self.basket = Basket(x=WIDTH / 2, y=HEIGHT - 30)
        self.objects = []
        self.frames_until_spawn = 0
        self.last_spawn_x = None
        self.score = 0
        self.misses = 0
        self.game_over = False

    def _spawn_object(self):
        if len(self.objects) >= MAX_OBJECTS:
            return
        lo, hi = SPAWN_MARGIN, WIDTH - SPAWN_MARGIN
        x = random.randint(lo, hi)
        for _ in range(10):
            if self.last_spawn_x is None or abs(x - self.last_spawn_x) >= MIN_SPAWN_SEPARATION:
                break
            x = random.randint(lo, hi)
        self.last_spawn_x = x
        self.objects.append(FallingObject(x=x, y=-14, speed=random.randint(3, 5)))

    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        direction = int(bool(keys_pressed[pygame.K_RIGHT])) - int(bool(keys_pressed[pygame.K_LEFT]))
        self.basket.move(direction, WIDTH)

    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self.__init__()
        elif not self.game_over and key == pygame.K_SPACE:
            self.basket.activate_boost()

    def update(self):
        if self.game_over:
            return

        self.basket.tick()

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_object()
            self.frames_until_spawn = random.randint(SPAWN_MIN_FRAMES, SPAWN_MAX_FRAMES)

        for obj in self.objects:
            obj.update()

        basket_rect = self.basket.get_rect()
        remaining = []
        for obj in self.objects:
            if is_caught(basket_rect, obj):
                self.score += 1
            else:
                remaining.append(obj)
        self.objects = remaining

        missed = [o for o in self.objects if o.is_past_bottom(HEIGHT)]
        if missed:
            self.objects = [o for o in self.objects if not o.is_past_bottom(HEIGHT)]
            self.misses += len(missed)
            if self.misses >= MAX_MISSES:
                self.game_over = True

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.basket, self.objects)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_text(surface, font, f"Misses: {self.misses}/{MAX_MISSES}", (10, 36))

        if self.basket.is_boosted:
            secs = self.basket.boosted_frames / 60
            renderer.draw_text(surface, font, f"SPEED BOOST! {secs:.1f}s", (10, 62), (255, 220, 80))
        elif self.basket.cooldown_frames > 0:
            secs = self.basket.cooldown_frames / 60
            renderer.draw_text(surface, font, f"Boost recharging {secs:.1f}s", (10, 62), (160, 160, 160))
        else:
            renderer.draw_text(surface, font, "Boost ready: press SPACE", (10, 62), (120, 220, 120))

        if self.game_over:
            renderer.draw_banner(surface, font, f"Game Over! Final score: {self.score}. Press R to restart.")

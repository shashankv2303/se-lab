"""
Basket: the player-controlled catcher at the bottom of the screen.
"""

import pygame

BOOST_MULTIPLIER = 2.0
BOOST_DURATION_FRAMES = 180    # 3 seconds at 60 FPS
BOOST_COOLDOWN_FRAMES = 300    # 5 seconds before it can be used again


class Basket:
    def __init__(self, x, y, width=90, height=24, speed=5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.boosted_frames = 0
        self.cooldown_frames = 0
        self.normal_speed = speed
        self.boost_speed = speed * BOOST_MULTIPLIER

    @property
    def is_boosted(self):
        return self.boosted_frames > 0

    @property
    def current_speed(self):
        return self.boost_speed if self.is_boosted else self.normal_speed

    def activate_boost(self):
        if self.boosted_frames == 0 and self.cooldown_frames == 0:
            self.boosted_frames = BOOST_DURATION_FRAMES
            self.cooldown_frames = BOOST_COOLDOWN_FRAMES

    def tick(self):
        if self.boosted_frames > 0:
            self.boosted_frames -= 1
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1

    def move(self, direction, screen_width):
        """direction: -1 (left), 0, or +1 (right). Keeps basket fully on screen."""
        self.x += direction * self.current_speed
        half = self.width / 2
        self.x = max(half, min(screen_width - half, self.x))

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2), int(self.y - self.height / 2),
            self.width, self.height,
        )

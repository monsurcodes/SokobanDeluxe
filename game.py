import pygame
import os
from pytmx.util_pygame import load_pygame

from settings import FPS, DISPLAY_RESOLUTION
from player import Player
from boxes import Box, CollisionBox


class Game:
    def __init__(self):
        # general setup
        pygame.init()
        pygame.display.set_caption("Sokoban Deluxe")
        self.screen = pygame.display.set_mode(DISPLAY_RESOLUTION)
        self.clock = pygame.time.Clock()
        self.running = True

        # all sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.box_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        
        # box marker points
        self.box_marker_points = []
        
        self.setup_map()

    def setup_map(self, level=1):
        tmx_data = load_pygame(os.path.join("levels", f"{level}_level.tmx"))
        
        # spawn player
        for obj in tmx_data.get_layer_by_name("BoxMarkers"):
            if obj.name == "player":
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.box_sprites)
            elif obj.name == "box_point":
                self.box_marker_points.append((obj.x, obj.y))
        
        # spawn collision boxes
        for x,y,image in tmx_data.get_layer_by_name("Collisions").tiles():
            CollisionBox(
                (x * 64, y * 64),
                image,
                (self.all_sprites, self.collision_sprites)
            )
            
        # spawn boxes
        for x,y,image in tmx_data.get_layer_by_name("Boxes").tiles():
            Box(
                (x * 64, y * 64),
                image,
                self.box_marker_points,
                self.player,
                self.collision_sprites,
                self.box_sprites,
                (self.all_sprites, self.box_sprites)
            )
            
    def run(self):
        while self.running:
            # delta time
            dt = self.clock.tick(FPS) / 1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update
            self.all_sprites.update(dt)

            # draw
            self.screen.fill("grey")
            self.all_sprites.draw(self.screen)

            # update screen
            pygame.display.update()

        pygame.quit()

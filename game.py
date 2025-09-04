import pygame
import os
import sys
from pytmx.util_pygame import load_pygame

from settings import FPS, DISPLAY_RESOLUTION
from player import Player
from boxes import Box, CollisionBox

from utils.save_game import load_game_level, save_game

class Game:
    def __init__(self):
        # general setup
        pygame.init()
        pygame.display.set_caption("Sokoban Deluxe")
        self.screen = pygame.display.set_mode(DISPLAY_RESOLUTION)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # game settings
        self.game_level = load_game_level()

        # all sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.box_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        
        # box marker points
        self.box_marker_points = []
        
        self.setup_map()

    def setup_map(self):
        if not os.path.exists(os.path.join("levels", f"{self.game_level}_level.tmx")):
            print("No more levels available. You've completed the game!")
            self.running = False
            pygame.quit()
            sys.exit()
            
        tmx_data = load_pygame(os.path.join("levels", f"{self.game_level}_level.tmx"))
        
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
                    pygame.quit()
                    self.running = False

            # update
            self.all_sprites.update(dt)

            # draw
            self.screen.fill("grey")
            self.all_sprites.draw(self.screen)
            
            # check level completion
            if self.player.level_completed:
                print(f"Level {self.game_level} completed!")
                self.all_sprites.empty()
                self.box_sprites.empty()
                self.collision_sprites.empty()
                self.box_marker_points.clear()
                self.running = False
                save_game(self.game_level + 1)

            # update screen
            pygame.display.update()

import pygame
import os
import sys
import time
from pytmx.util_pygame import load_pygame

from settings import FPS, DISPLAY_RESOLUTION, WIDTH, HEIGHT
from player import Player
from boxes import Box, CollisionBox

from utils.save_game import load_game_level, save_game
from utils.button import Button

class Game:
    def __init__(self):
        # general setup
        pygame.init()
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
        
        # restart stuff
        self.restart_btn = Button(
            image=pygame.image.load(os.path.join("assets", "button", "RestartRect.png")).convert_alpha(),
            pos=(WIDTH - 120, 30),
            text_input="Restart",
            font=pygame.font.Font(os.path.join("assets", "fonts", "font.ttf"), 20),
            base_color="#d7fcd4",
            hovering_color="white",
        )
        
        self.setup_map()
        
    def unload_map(self):
        self.all_sprites.empty()
        self.box_sprites.empty()
        self.collision_sprites.empty()
        self.box_marker_points.clear()
        
    def display_text(self, text, size, color, position):
        self.screen.fill("black")
        font = pygame.font.Font(os.path.join("assets", "fonts", "font.ttf"), size)
        text = font.render(text, True, color)
        text_rect = text.get_rect(center=position)
        self.screen.blit(text, text_rect)
        pygame.display.update()

    def setup_map(self):
        if not os.path.exists(os.path.join("levels", f"{self.game_level}_level.tmx")):
            self.unload_map()

            # levels completed screen
            self.display_text("You have completed all levels!", 32, "White", (WIDTH // 2, HEIGHT // 2))
            save_game(1) # reset to level 1
            
            time.sleep(2) # wait for player to read message
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
            
            # mouse position
            mouse_position = pygame.mouse.get_pos()

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.restart_btn.checkForInput(mouse_position):
                        self.running = False

            # update
            self.all_sprites.update(dt)

            # draw
            game_bg = pygame.image.load(os.path.join("assets", "images", "game_bg.jpg")).convert()
            game_bg = pygame.transform.scale(game_bg, DISPLAY_RESOLUTION)
            self.screen.blit(game_bg, (0, 0))
            self.all_sprites.draw(self.screen)
            
            # restart button
            
            self.restart_btn.changeColor(mouse_position)
            self.restart_btn.update(self.screen)
            
            # check level completion
            if self.player.level_completed:
                self.unload_map()
                
                # game over screen
                self.display_text("Level Completed!", 32, "White", (WIDTH // 2, HEIGHT // 2))

                # increment level
                save_game(self.game_level + 1)
                
                time.sleep(2) # wait for player to read message
                self.running = False

            # update screen
            pygame.display.update()

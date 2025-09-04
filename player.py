import pygame
import os


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        position,
        groups,
        collision_groups: pygame.sprite.Group,
        box_groups: pygame.sprite.Group,
    ):
        super().__init__(groups)

        self.image = pygame.image.load(
            os.path.join("assets", "images", "player.png")
        ).convert_alpha()
        self.rect = self.image.get_frect(center=position)
        self.hitbox_rect = self.rect.inflate(-10, -10)

        # movement
        self.speed = 2000
        self.direction = pygame.math.Vector2(0, 0)
        
        # grid movement
        self.grid_size = 64
        self.is_moving = False
        self.target_position = None

        # collision
        self.collision_groups = collision_groups

        # boxes
        self.box_groups = box_groups
        

    def input(self):
        # Only accept input if not currently moving
        if not self.is_moving:
            keys = pygame.key.get_just_pressed()
            self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
                keys[pygame.K_LEFT] or keys[pygame.K_a]
            )
            self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(
                keys[pygame.K_UP] or keys[pygame.K_w]
            )
            # Don't normalize for grid movement - keep as -1, 0, or 1
            if self.direction.x != 0:
                self.direction.y = 0  # Prevent diagonal movement
            elif self.direction.y != 0:
                self.direction.x = 0

    def move(self, dt):
        # If there's input and not currently moving
        if (self.direction.x != 0 or self.direction.y != 0) and not self.is_moving:
            # Calculate target grid position
            target_x = self.hitbox_rect.x + (self.direction.x * self.grid_size)
            target_y = self.hitbox_rect.y + (self.direction.y * self.grid_size)
            
            # Create target rect for collision checking
            target_rect = pygame.Rect(target_x, target_y, self.hitbox_rect.width, self.hitbox_rect.height)
            
            # Check if target position is free
            if self.is_target_position_free(target_rect):
                # Store direction for box pushing
                move_direction = pygame.math.Vector2(self.direction.x, self.direction.y)
                
                # Move to target position instantly
                self.hitbox_rect.x = target_x
                self.hitbox_rect.y = target_y
                self.rect.center = self.hitbox_rect.center
                
                # Try to push boxes if any
                self.push_boxes(move_direction)
        
        # Reset direction after processing
        self.direction.x = 0
        self.direction.y = 0

    def is_target_position_free(self, target_rect):
        # Check collision with walls/obstacles
        for sprite in self.collision_groups:
            if sprite.rect.colliderect(target_rect):
                return False
        
        # Check collision with boxes - if there's a box, check if it can be pushed
        for box in self.box_groups:
            if box.rect.colliderect(target_rect):
                # Calculate where the box would go if pushed
                box_target_x = box.rect.x + (self.direction.x * self.grid_size)
                box_target_y = box.rect.y + (self.direction.y * self.grid_size)
                box_target_rect = pygame.Rect(box_target_x, box_target_y, box.rect.width, box.rect.height)
                
                # Check if box can be pushed (no wall or other box in the way)
                box_can_move = True
                for wall in self.collision_groups:
                    if wall.rect.colliderect(box_target_rect):
                        box_can_move = False
                        break
                
                if box_can_move:
                    for other_box in self.box_groups:
                        if other_box != box and other_box.rect.colliderect(box_target_rect):
                            box_can_move = False
                            break
                
                return box_can_move
        
        return True
    
    def push_boxes(self, move_direction):
        # Push any boxes that are in the player's current position
        for box in self.box_groups:
            if box.rect.colliderect(self.hitbox_rect):
                # Move the box by one grid cell in the direction
                box.rect.x += move_direction.x * self.grid_size
                box.rect.y += move_direction.y * self.grid_size

    def check_collision(self, direction):
        for sprite in self.collision_groups:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == "horizontal":
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                elif direction == "vertical":
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom

    def update(self, dt):
        self.input()
        self.move(dt)

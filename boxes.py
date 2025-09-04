import pygame
import os

class Box(pygame.sprite.Sprite):
    def __init__(
        self,
        position,
        surface,
        marker_points,
        player_sprite: pygame.sprite.Sprite,
        collision_boxes: pygame.sprite.Group,
        same_type_boxes: pygame.sprite.Group,
        groups,
    ):
        super().__init__(groups)
        self.surface = surface
        self.alt_surface = pygame.image.load(os.path.join("assets", "graphics", "box-dark.png")).convert_alpha()
        self.image = self.surface
        self.rect = self.image.get_frect(topleft=position)
        self.player_sprite = player_sprite
        self.collision_boxes = collision_boxes
        self.same_type_boxes = same_type_boxes
        self.marker_points = marker_points

    def move_with_player(self):
        if self.rect.colliderect(self.player_sprite.hitbox_rect):
            # Get grid dimensions based on box size
            grid_width = self.rect.width
            grid_height = self.rect.height

            # Calculate target grid position
            target_rect = self.rect.copy()

            if self.player_sprite.direction.x != 0:
                if self.player_sprite.direction.x > 0:
                    target_rect.x += grid_width  # Move one grid cell right
                elif self.player_sprite.direction.x < 0:
                    target_rect.x -= grid_width  # Move one grid cell left

                # Check if target position is free
                if self.is_target_position_free(target_rect):
                    self.rect = target_rect
                    # Adjust player position to stay aligned
                    if self.player_sprite.direction.x > 0:
                        self.player_sprite.hitbox_rect.right = self.rect.left
                    else:
                        self.player_sprite.hitbox_rect.left = self.rect.right
                else:
                    # Block player movement if box can't move
                    if self.player_sprite.direction.x > 0:
                        self.player_sprite.hitbox_rect.right = self.rect.left
                    else:
                        self.player_sprite.hitbox_rect.left = self.rect.right

            elif self.player_sprite.direction.y != 0:
                if self.player_sprite.direction.y > 0:
                    target_rect.y += grid_height  # Move one grid cell down
                elif self.player_sprite.direction.y < 0:
                    target_rect.y -= grid_height  # Move one grid cell up

                # Check if target position is free
                if self.is_target_position_free(target_rect):
                    self.rect = target_rect
                    # Adjust player position to stay aligned
                    if self.player_sprite.direction.y > 0:
                        self.player_sprite.hitbox_rect.bottom = self.rect.top
                    else:
                        self.player_sprite.hitbox_rect.top = self.rect.bottom
                else:
                    # Block player movement if box can't move
                    if self.player_sprite.direction.y > 0:
                        self.player_sprite.hitbox_rect.bottom = self.rect.top
                    else:
                        self.player_sprite.hitbox_rect.top = self.rect.bottom

    def is_target_position_free(self, target_rect):
        # Check collision with walls/obstacles
        for sprite in self.collision_boxes:
            if sprite.rect.colliderect(target_rect):
                return False

        # Check collision with other boxes
        for other_box in self.same_type_boxes:
            if other_box != self and other_box.rect.colliderect(target_rect):
                return False

        return True

    def is_colliding_box(self, direction):
        # check collisions with collision boxes
        for sprite in self.collision_boxes:
            if sprite.rect.colliderect(self.rect):
                if direction == "horizontal":
                    if self.player_sprite.direction.x > 0:
                        self.rect.right = sprite.rect.left
                        self.player_sprite.hitbox_rect.right = self.rect.left
                    if self.player_sprite.direction.x < 0:
                        self.rect.left = sprite.rect.right
                        self.player_sprite.hitbox_rect.left = self.rect.right
                elif direction == "vertical":
                    if self.player_sprite.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                        self.player_sprite.hitbox_rect.bottom = self.rect.top
                    if self.player_sprite.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
                        self.player_sprite.hitbox_rect.top = self.rect.bottom

        # check collisions with same type boxes
        for other_box in self.same_type_boxes:
            if other_box != self and other_box.rect.colliderect(self.rect):
                if direction == "horizontal":
                    if self.player_sprite.direction.x > 0:
                        self.rect.right = other_box.rect.left
                        self.player_sprite.hitbox_rect.right = self.rect.left
                    if self.player_sprite.direction.x < 0:
                        self.rect.left = other_box.rect.right
                        self.player_sprite.hitbox_rect.left = self.rect.right
                elif direction == "vertical":
                    if self.player_sprite.direction.y > 0:
                        self.rect.bottom = other_box.rect.top
                        self.player_sprite.hitbox_rect.bottom = self.rect.top
                    if self.player_sprite.direction.y < 0:
                        self.rect.top = other_box.rect.bottom
                        self.player_sprite.hitbox_rect.top = self.rect.bottom

    def check_marker_point(self):
        on_marker = False
        for point in self.marker_points:
            if self.rect.collidepoint(point):
                on_marker = True
                break

        if on_marker:
            self.image = self.alt_surface
        else:
            self.image = self.surface
            
    def check_level_completion(self):
        for point in self.marker_points:
            if not any(box.rect.collidepoint(point) for box in self.same_type_boxes):
                return False
        return True

    def update(self, dt):
        self.move_with_player()
        self.check_marker_point()
        self.player_sprite.level_completed = self.check_level_completion()


class CollisionBox(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(topleft=position)

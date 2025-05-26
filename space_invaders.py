import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Clock for controlling game speed
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Simple rectangle for the player
        self.image = pygame.Surface([50, 30])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - 25
        self.rect.y = SCREEN_HEIGHT - 50
        self.speed = 5
        self.cooldown = 0
        self.cooldown_time = 15  # Frames between shots

    def update(self):
        # Get keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        # Decrease cooldown timer
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        if self.cooldown == 0:
            self.cooldown = self.cooldown_time
            return Bullet(self.rect.centerx, self.rect.top)
        return None

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Simple rectangle for the enemy
        self.image = pygame.Surface([40, 40])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.direction

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([5, 10])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        # Remove if it goes off the top of the screen
        if self.rect.bottom < 0:
            self.kill()
class Game:
    def __init__(self):
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)

        # Create enemies
        self.create_enemies()

        # Game variables
        self.score = 0
        self.game_over = False
        self.enemy_direction = 1
        self.enemy_move_down = False
        self.font = pygame.font.SysFont(None, 36)

    def create_enemies(self):
        # Create a grid of enemies
        for row in range(5):
            for column in range(10):
                enemy = Enemy(column * 70 + 50, row * 50 + 50)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = self.player.shoot()
                    if bullet:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True
    def run_logic(self):
        if not self.game_over:
            # Update all sprites
            self.all_sprites.update()

            # Check if any enemy has reached the edge
            self.enemy_move_down = False
            for enemy in self.enemies:
                if enemy.rect.right >= SCREEN_WIDTH:
                    self.enemy_direction = -1
                    self.enemy_move_down = True
                elif enemy.rect.left <= 0:
                    self.enemy_direction = 1
                    self.enemy_move_down = True

            # Move enemies down if needed
            if self.enemy_move_down:
                for enemy in self.enemies:
                    enemy.rect.y += 20
                    enemy.direction = self.enemy_direction

            # Update enemy direction
            for enemy in self.enemies:
                enemy.direction = self.enemy_direction

            # Check for bullet collisions with enemies
            hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
            for hit in hits:
                self.score += 10

            # Check if enemies reached the bottom
            for enemy in self.enemies:
                if enemy.rect.bottom >= SCREEN_HEIGHT - 50:
                    self.game_over = True

            # Check if all enemies are destroyed
            if len(self.enemies) == 0:
                self.create_enemies()

    def display_frame(self):
        # Clear the screen
        screen.fill(BLACK)
        # Draw all sprites
        self.all_sprites.draw(screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw game over message if needed
        if self.game_over:
            game_over_text = self.font.render("GAME OVER - Press ESC to exit", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))

        # Update the display
        pygame.display.flip()

def main():
    game = Game()
    done = False

    # Main game loop
    while not done:
        done = not game.process_events()
        game.run_logic()
        game.display_frame()
        clock.tick(60)  # 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

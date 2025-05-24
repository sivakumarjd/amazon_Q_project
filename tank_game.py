import pygame
import math
import random

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
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle Tank 90s")

# Clock for controlling game speed
clock = pygame.time.Clock()

# Load images
def load_image(name, scale=1):
    try:
        image = pygame.Surface((30, 30))
        if name == "player_tank":
            image.fill(GREEN)
        elif name == "enemy_tank":
            image.fill(RED)
        elif name == "wall":
            image.fill(GRAY)
        elif name == "bullet":
            image = pygame.Surface((8, 8))
            image.fill(WHITE)

        if scale != 1:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
        return image
    except pygame.error as e:
        print(f"Unable to load image: {e}")
        return pygame.Surface((30, 30))

# Tank class
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, image, bullet_image, is_player=False):
        super().__init__()
        self.image = image
        self.original_image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.direction = 0  # 0: up, 1: right, 2: down, 3: left
        self.bullet_image = bullet_image
        self.is_player = is_player
        self.shoot_delay = 500  # milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.health = 3

    def update(self, walls):
        old_x, old_y = self.rect.x, self.rect.y

        if self.is_player:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.direction = 0
                self.rect.y -= self.speed
            elif keys[pygame.K_RIGHT]:
                self.direction = 1
                self.rect.x += self.speed
            elif keys[pygame.K_DOWN]:
                self.direction = 2
                self.rect.y += self.speed
            elif keys[pygame.K_LEFT]:
                self.direction = 3
                self.rect.x -= self.speed
        else:
            # Simple AI for enemy tanks
            if random.randint(0, 30) == 0:
                self.direction = random.randint(0, 3)

            if self.direction == 0:
                self.rect.y -= self.speed
            elif self.direction == 1:
                self.rect.x += self.speed
            elif self.direction == 2:
                self.rect.y += self.speed
            elif self.direction == 3:
                self.rect.x -= self.speed

            # Random shooting
            if random.randint(0, 50) == 0:
                self.shoot()

        # Rotate image based on direction
        if self.direction == 0:  # Up
            self.image = pygame.transform.rotate(self.original_image, 0)
        elif self.direction == 1:  # Right
            self.image = pygame.transform.rotate(self.original_image, -90)
        elif self.direction == 2:  # Down
            self.image = pygame.transform.rotate(self.original_image, 180)
        elif self.direction == 3:  # Left
            self.image = pygame.transform.rotate(self.original_image, 90)

        # Check for collisions with walls
        wall_hit = pygame.sprite.spritecollide(self, walls, False)
        if wall_hit:
            self.rect.x, self.rect.y = old_x, old_y

        # Keep tank on screen
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > SCREEN_HEIGHT - self.rect.height:
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.centery,
                           self.direction, self.bullet_image, self.is_player)
            return bullet
        return None

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, image, is_player):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.direction = direction
        self.speed = 7
        self.is_player = is_player

    def update(self):
        if self.direction == 0:  # Up
            self.rect.y -= self.speed
        elif self.direction == 1:  # Right
            self.rect.x += self.speed
        elif self.direction == 2:  # Down
            self.rect.y += self.speed
        elif self.direction == 3:  # Left
            self.rect.x -= self.speed

        # Remove if it goes off-screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

# Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Game class
class Game:
    def __init__(self):
        # Load images
        self.player_image = load_image("player_tank")
        self.enemy_image = load_image("enemy_tank")
        self.wall_image = load_image("wall")
        self.bullet_image = load_image("bullet")

        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Create player
        self.player = Tank(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, 3,
                          self.player_image, self.bullet_image, True)
        self.all_sprites.add(self.player)

        # Create walls
        self.create_level()

        # Game state
        self.game_over = False
        self.score = 0
        self.level = 1
        self.font = pygame.font.SysFont(None, 36)

    def create_level(self):
        # Clear existing sprites
        for enemy in self.enemies:
            enemy.kill()
        for wall in self.walls:
            wall.kill()

        # Create walls
        for i in range(20):
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = random.randint(0, SCREEN_HEIGHT - 30)
            wall = Wall(x, y, self.wall_image)
            self.walls.add(wall)
            self.all_sprites.add(wall)

        # Create enemies
        for i in range(3 + self.level):
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = random.randint(0, 200)
            enemy = Tank(x, y, 2, self.enemy_image, self.bullet_image)
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
                elif event.key == pygame.K_r and self.game_over:
                    self.__init__()
        return True

    def run_logic(self):
        if not self.game_over:
            # Update player
            self.player.update(self.walls)

            # Update enemies
            for enemy in self.enemies:
                enemy.update(self.walls)
                bullet = enemy.shoot()
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)

            # Update bullets
            self.bullets.update()

            # Check for bullet collisions with tanks
            for bullet in self.bullets:
                # Player bullets hitting enemies
                if bullet.is_player:
                    enemy_hit = pygame.sprite.spritecollide(bullet, self.enemies, False)
                    if enemy_hit:
                        bullet.kill()
                        for enemy in enemy_hit:
                            enemy.health -= 1
                            if enemy.health <= 0:
                                enemy.kill()
                                self.score += 100
                # Enemy bullets hitting player
                else:
                    if pygame.sprite.collide_rect(bullet, self.player):
                        bullet.kill()
                        self.player.health -= 1
                        if self.player.health <= 0:
                            self.game_over = True

                # Bullets hitting walls
                wall_hit = pygame.sprite.spritecollide(bullet, self.walls, False)
                if wall_hit:
                    bullet.kill()

            # Check if all enemies are defeated
            if len(self.enemies) == 0:
                self.level += 1
                self.create_level()

    def display_frame(self):
        screen.fill(BLACK)

        # Draw all sprites
        self.all_sprites.draw(screen)

        # Display score and health
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, [10, 10])

        health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
        screen.blit(health_text, [10, 50])

        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, [SCREEN_WIDTH - 150, 10])

        # Game over message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER - Press R to Restart", True, RED)
            screen.blit(game_over_text, [SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2])

        pygame.display.flip()
# Main function
def main():
    game = Game()
    done = False

    # Main game loop
    while not done:
        done = not game.process_events()
        game.run_logic()
        game.display_frame()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

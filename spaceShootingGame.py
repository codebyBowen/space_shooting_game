import pygame
import random
import math
from PIL import Image, ImageDraw

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 480, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("太空射击游戏")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

def create_pixel_art(width, height, pixel_data):
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for y, row in enumerate(pixel_data):
        for x, color in enumerate(row):
            if color is not None:
                draw.point((x, y), fill=color)
    return image

def pil_to_pygame(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    py_image = pygame.image.fromstring(data, size, mode)
    return py_image

# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_pixels = [
            [None, None, None, BLUE, None, None, None],
            [None, None, BLUE, BLUE, BLUE, None, None],
            [None, BLUE, BLUE, BLUE, BLUE, BLUE, None],
            [BLUE, BLUE, BLUE, BLUE, BLUE, BLUE, BLUE],
            [BLUE, BLUE, BLUE, BLUE, BLUE, BLUE, BLUE],
            [None, None, YELLOW, YELLOW, YELLOW, None, None],
            [None, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, None],
        ]
        pil_image = create_pixel_art(7, 7, player_pixels)
        self.image = pil_to_pygame(pil_image.resize((35, 35), Image.NEAREST))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5
        self.powerups = {"spread": 0, "rapid": 0, "damage": 0, "size": 0}

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

# Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx=0, damage=1, size=4):
        super().__init__()
        bullet_pixels = [
            [None, YELLOW, YELLOW, None],
            [YELLOW, YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW, YELLOW],
            [None, YELLOW, YELLOW, None],
        ]
        pil_image = create_pixel_art(4, 4, bullet_pixels)
        self.image = pil_to_pygame(pil_image.resize((size, size * 2), Image.NEAREST))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.dx = dx
        self.dy = -7
        self.damage = damage

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.bottom < 0:
            self.kill()

# Enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        enemy_pixels = [
            [None, None, RED, RED, RED, None, None],
            [None, RED, RED, RED, RED, RED, None],
            [RED, RED, RED, RED, RED, RED, RED],
            [RED, None, RED, RED, RED, None, RED],
            [RED, None, None, RED, None, None, RED],
            [None, RED, None, None, None, RED, None],
        ]
        pil_image = create_pixel_art(7, 6, enemy_pixels)
        self.image = pil_to_pygame(pil_image.resize((35, 30), Image.NEAREST))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Elite Enemy
class EliteEnemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        elite_enemy_pixels = [
            [None, None, None, (128,0,128), None, None, None],
            [None, None, (128,0,128), (128,0,128), (128,0,128), None, None],
            [None, (128,0,128), (128,0,128), (128,0,128), (128,0,128), (128,0,128), None],
            [(128,0,128), (128,0,128), (255,255,0), (128,0,128), (255,255,0), (128,0,128), (128,0,128)],
            [(128,0,128), (128,0,128), (128,0,128), (128,0,128), (128,0,128), (128,0,128), (128,0,128)],
            [None, None, (255,255,0), (255,255,0), (255,255,0), None, None],
            [None, (255,255,0), (255,255,0), (255,255,0), (255,255,0), (255,255,0), None],
        ]
        pil_image = create_pixel_art(7, 7, elite_enemy_pixels)
        self.image = pil_to_pygame(pil_image.resize((35, 35), Image.NEAREST))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = 0
        self.health = 5
        self.hover_time = 0
        self.hover_duration = 180
        self.fire_interval = 30

    def update(self):
        if self.rect.y < 100:
            self.rect.y += 1
        elif self.hover_time < self.hover_duration:
            self.hover_time += 1
        else:
            self.rect.y += 0.5
        if self.rect.top > HEIGHT:
            self.kill()

# Power-up
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(["spread", "rapid", "damage", "size"])
        powerup_pixels = [
            [None, None, GREEN, GREEN, GREEN, None, None],
            [None, GREEN, GREEN, GREEN, GREEN, GREEN, None],
            [GREEN, GREEN, GREEN, WHITE, GREEN, GREEN, GREEN],
            [GREEN, GREEN, WHITE, WHITE, WHITE, GREEN, GREEN],
            [GREEN, GREEN, GREEN, WHITE, GREEN, GREEN, GREEN],
            [None, GREEN, GREEN, GREEN, GREEN, GREEN, None],
            [None, None, GREEN, GREEN, GREEN, None, None],
        ]
        pil_image = create_pixel_art(7, 7, powerup_pixels)
        self.image = pil_to_pygame(pil_image.resize((21, 21), Image.NEAREST))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = 0
        self.speed = 1

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Star (for background)
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.randint(1, 3)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (self.x, self.y), self.size)

# Game class
class Game:
    def __init__(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.elite_enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.stars = [Star() for _ in range(100)]  # Create 100 stars for the background

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.shoot()

            self.update()
            self.draw()

        pygame.quit()

    def update(self):
        self.all_sprites.update()

        # Update stars
        for star in self.stars:
            star.update()

        # Spawn enemies
        if random.random() < 0.02 and len(self.enemies) < 5:
            self.enemies.add(Enemy())
            self.all_sprites.add(self.enemies.sprites()[-1])

        # Spawn elite enemies
        if random.random() < 0.005 and len(self.elite_enemies) < 2:
            self.elite_enemies.add(EliteEnemy())
            self.all_sprites.add(self.elite_enemies.sprites()[-1])

        # Spawn power-ups
        if random.random() < 0.005:
            self.powerups.add(PowerUp())
            self.all_sprites.add(self.powerups.sprites()[-1])

        # Check collisions
        self.check_collisions()

    def draw(self):
        screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(screen)
        
        self.all_sprites.draw(screen)
        score_text = self.font.render(f"得分: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

    def shoot(self):
        spread = 1 + self.player.powerups["spread"] * 2
        damage = 1 + self.player.powerups["damage"]
        size = 4 + self.player.powerups["size"]
        
        for i in range(spread):
            angle = (i - (spread - 1) / 2) * (math.pi / 6)
            dx = math.sin(angle) * 2
            bullet = Bullet(self.player.rect.centerx, self.player.rect.top, dx, damage, size)
            self.bullets.add(bullet)
            self.all_sprites.add(bullet)

    def check_collisions(self):
        # Player bullets with enemies
        for enemy in self.enemies:
            hits = pygame.sprite.spritecollide(enemy, self.bullets, True)
            for hit in hits:
                enemy.kill()
                self.score += 1

        # Player bullets with elite enemies
        for enemy in self.elite_enemies:
            hits = pygame.sprite.spritecollide(enemy, self.bullets, True)
            for hit in hits:
                enemy.health -= hit.damage
                if enemy.health <= 0:
                    enemy.kill()
                    self.score += 5

        # Player with enemies
        if pygame.sprite.spritecollide(self.player, self.enemies, True) or \
           pygame.sprite.spritecollide(self.player, self.elite_enemies, True):
            self.game_over()

        # Player with power-ups
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in hits:
            self.player.powerups[hit.type] = min(self.player.powerups[hit.type] + 1, 3)

    def game_over(self):
        game_over_text = self.font.render("游戏结束", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        self.__init__()  # Reset the game

if __name__ == "__main__":
    game = Game()
    game.run()
# ================= MAIN_GAME.PY (Platform Collision + Spike Damage) =================
import pygame
import random
pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer Stick Fight")
SPIKE_DAMAGE = 50
WHITE = (255, 255, 255)
players = {}




def get_random_spawn(platforms):
    safe_platforms = [p for p in platforms if not p.is_spike]
    if not safe_platforms:
        return 100, 100  # fallback
    chosen = random.choice(safe_platforms)
    x = random.randint(chosen.rect.x + 10, chosen.rect.x + chosen.rect.width - 60)
    y = chosen.rect.y - 50
    return x, y

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_spike = False

    def draw(self, screen):
        # Create a transparent surface
        temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))   # 0 for fully invisible

        # Blit it to the screen at the rect's position
        screen.blit(temp_surface, self.rect.topleft)


class Player:
    def __init__(self, addr, x, y):
        self.addr = addr
        self.rect = pygame.Rect(x, y, 50, 50)
        self.vel_y = 0
        self.gravity = 1
        self.speed = 5
        self.jump_power = -15
        self.on_ground = False

        self.state = "idle"
        self.health = 100
        self.last_spike_time = 0

    def move(self, platforms):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        self.on_ground = False
        now = pygame.time.get_ticks()

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if platform.is_spike:
                    if now - self.last_spike_time > 1000:
                        self.health = max(0, self.health - SPIKE_DAMAGE)
                        self.last_spike_time = now
                elif self.vel_y >= 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

def create_platforms():
    platforms = []
    platforms.append(Platform(25, 422, 310, 1))        # Left
    platforms.append(Platform(870, 422, 195, 1))       # Right
    platforms.append(Platform(315, 540, 565, 1))       # Bottom
    platforms.append(Platform(452, 320, 292, 1))
    spike = Platform(470, 400, 260 ,15 )                 # Middle with spikes
    spike.is_spike = True
    platforms.append(spike)

    return platforms

def main_game():
    pygame.init()
    clock = pygame.time.Clock()
    platforms = create_platforms()

    running = True
    while running:
        screen.blit(background_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        for platform in platforms:
            platform.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

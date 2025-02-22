import pygame

pygame.init()

# Screen setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stick Fight")

# Colors
WHITE = (255, 255, 255)
BROWN = (150, 75, 0)
BLUE = (0, 0, 255)

# Platform class
class Platform:
    def __init__(self, x, y, width, height, image_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        if image_path:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            self.image = None  # Use a default rectangle if no image is given

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, (0, 0, 0), self.rect)  # Default color if no image

# Player class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.vel_y = 0
        self.on_ground = False
        self.punch_box = pygame.Rect(0, 0, 0, 0)  # Placeholder for punch hitbox
        self.is_punching = False

    def move(self, platforms, enemies):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 5
        if keys[pygame.K_d]:
            self.rect.x += 5
        if keys[pygame.K_SPACE] and self.on_ground:  # Jump only if on ground
            self.vel_y = -12
            self.on_ground = False
        # Punch action
        if keys[pygame.K_j] and not self.is_punching:  # Only punch if not already punching
            self.is_punching = True
            self.punch_box = pygame.Rect(self.rect.x + 40, self.rect.y + 20, 50, 20)  # Punch hitbox
        # Reset punch after some time
        if self.is_punching:
            pygame.time.set_timer(pygame.USEREVENT, 100)  # Timer to reset punch

        for enemy in enemies:
            if self.punch_box.colliderect(enemy.rect):
                print("Hit!")  # Placeholder for damage logic

        # Gravity
        self.vel_y += 0.5
        self.rect.y += self.vel_y

        # Collision detection
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)


def main_game():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Platformer Game")

    platforms = [
        Platform(200, 500, 300, 20),
        Platform(500, 400, 200, 20),
        Platform(100, 300, 250, 20)
    ]

    player = Player(300, 200)

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Pass an empty list for 'enemies' for now
        player.move(platforms, enemies=[])

        # Check if player falls off the map
        if player.rect.y > 600:
            player.rect.x = 300
            player.rect.y = 200
            player.vel_y = 12  # Reset velocity

        player.draw(screen)

        for platform in platforms:
            platform.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()



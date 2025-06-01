# ================= CLIENT1.PY (Final Cleaned Version without Sounds) =================
import socket
import threading
import pygame
import tkinter as tk
from pygame import KEYDOWN

import main_game
import main_file
import run_mp4 as rm4
import auth_setup as auth

WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stick Fight Client")

HOST = "127.0.0.1"
PORT = 5555
player_previous_x = {}
players = {}
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
    print(f"Connected to server at {HOST}:{PORT}")
except Exception as e:
    print(f"Failed to connect: {e}")
    exit(1)

# Load assets
def load_colored_sprites(color):
    run_path = f"assets/{color}/run_combined_strip.png"
    idle_path = f"assets/{color}/idle_frame.png"
    jump_path = f"assets/{color}/jump_frame.png"
    punch_path = f"assets/{color}/full_punch_strip.png"

    run_sheet = pygame.image.load(run_path).convert_alpha()
    run_frame_width = run_sheet.get_width() // 5
    run_frame_height = run_sheet.get_height()
    run_frames = [run_sheet.subsurface(pygame.Rect(i * run_frame_width, 0, run_frame_width, run_frame_height)).copy() for i in range(5)]

    idle_image = pygame.image.load(idle_path).convert_alpha()
    jump_image = pygame.image.load(jump_path).convert_alpha()
    punch_strip = pygame.image.load(punch_path).convert_alpha()
    punch_frame_width = punch_strip.get_width() // 12
    punch_frame_height = punch_strip.get_height()
    punch_frames = [punch_strip.subsurface(pygame.Rect(i * punch_frame_width, 0, punch_frame_width, punch_frame_height)).copy() for i in range(12)]

    return {
        "run": run_frames,
        "idle": [pygame.transform.scale(idle_image, (50, 50))],
        "jump": [pygame.transform.scale(jump_image, (50, 50))],
        "punch": punch_frames
    }

menu_background = pygame.image.load("assets/main_menu_bg.png")
menu_background = pygame.transform.smoothscale(menu_background, (WIDTH, HEIGHT))
background_image = pygame.image.load("assets/red_tree_bg.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
instructions_background = pygame.image.load("assets/how_to_play.png")
instructions_background = pygame.transform.smoothscale(instructions_background, (WIDTH, HEIGHT))
you_win_image = pygame.image.load("assets/you_win.png").convert_alpha()
you_win_image = pygame.transform.scale(you_win_image, (600, 200))  # Optional: resize

player_animations = {}
player_last_direction = {}

def fade_to_black(screen, speed=10):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, speed):
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)

def draw_instructions_screen(screen):
    running = True
    font = pygame.font.Font(None, 36)
    back_button = pygame.Rect(30, 30, 100, 40)

    while running:
        screen.blit(instructions_background, (0, 0))
        back_text = font.render("Back", True, (108, 99, 255))
        screen.blit(back_text, (back_button.x + 20, back_button.y + 8))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                running = False
            elif event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

def draw_health_bar(surface, x, y, health, max_health=100):
    bar_width, bar_height = 50, 6
    health_ratio = max(0, min(1, health / max_health))
    red = int((1 - health_ratio) * 255)
    green = int(health_ratio * 255)
    color = (red, green, 0)
    pygame.draw.rect(surface, (30, 30, 30), (x, y, bar_width, bar_height), border_radius=3)
    pygame.draw.rect(surface, color, (x, y, int(bar_width * health_ratio), bar_height), border_radius=3)
    pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), width=1, border_radius=3)

def extract_details(message):
    global players, player_animations
    message = message.replace("UPDATE ", "")
    updated_players = {}

    for entry in message.split():
        try:
            ip, port, coords = entry.split(":")
            addr = str((ip, int(port)))
            x, y, state, health, direction = coords.split(",")
            x, y, health = int(x), int(y), int(health)
            updated_players[addr] = (x, y, state, health, direction)
            if addr not in player_animations:
                player_index = len(player_animations)
                color = "BLUE" if player_index == 0 else "RED"
                player_animations[addr] = {
                    "frame_index": 0,
                    "timer": 0,
                    "color": color,
                    "sprites": load_colored_sprites(color)
                }

        except Exception as e:
            print(f"Error parsing entry: {entry} | {e}")

    players = updated_players

def receive_data():
    while True:
        try:
            message = client.recv(1024).decode()
            if not message:
                break
            if message.startswith("UPDATE"):
                extract_details(message)
        except:
            break
    print("Connection to server lost.")

def game_loop(screen=None):
    global SCREEN
    damage_flash_timer = 0
    pygame.init()
    SCREEN = screen
    clock = pygame.time.Clock()
    platforms = main_game.create_platforms()

    # Show waiting screen until at least 2 players are present
    waiting_font = pygame.font.Font(None, 72)
    small_font = pygame.font.Font(None, 36)
    while len(players) < 2:
        SCREEN.blit(background_image, (0, 0))
        text = waiting_font.render("Waiting for players...", True, (255, 255, 255))
        info = small_font.render("Need at least 2 players to begin", True, (200, 200, 200))
        SCREEN.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        SCREEN.blit(info, info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()

        clock.tick(60)

    running = True
    button_rect = pygame.Rect(475, 200, 250, 70)

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()
        message = "GAME"
        if keys[pygame.K_a]: message += "LEFT"
        if keys[pygame.K_d]: message += "RIGHT"
        if keys[pygame.K_SPACE]: message += "UP"
        if keys[pygame.K_j]: message += "PUNCH"

        try:
            client.sendall(message.encode())
        except:
            running = False

        SCREEN.blit(background_image, (0, 0))
        for platform in platforms:
            platform.draw(SCREEN)

        snapshot = list(players.items())

        # Damage flash
        my_addr = str(client.getsockname())
        if my_addr in players:
            old_health = player_animations.get(my_addr, {}).get("last_health", 100)
            _, _, _, new_health, _ = players[my_addr]

            if new_health < old_health:
                damage_flash_timer = 5
            player_animations.setdefault(my_addr, {})["last_health"] = new_health

        if damage_flash_timer > 0:
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.set_alpha(80)
            flash.fill((255, 0, 0))
            SCREEN.blit(flash, (0, 0))
            damage_flash_timer -= 1

        for i, item in enumerate(snapshot):
            try:
                addr, (x, y, state, health, direction) = item
            except ValueError:
                continue
            anim = player_animations.get(addr, {"frame_index": 0, "timer": 0})
            sprites = anim.get("sprites", load_colored_sprites("BLUE"))
            frame_list = sprites[state] if state in sprites else sprites["idle"]

            if anim["frame_index"] >= len(frame_list):
                anim["frame_index"] = 0

            anim["timer"] += 1
            speed = 3 if state == "punch" else 6
            if anim["timer"] >= speed:
                anim["timer"] = 0
                anim["frame_index"] = (anim["frame_index"] + 1) % len(frame_list)

            frame = pygame.transform.scale(frame_list[anim["frame_index"]], (50, 50))
            if direction == "left":
                frame = pygame.transform.flip(frame, True, False)

            SCREEN.blit(frame, (x, y))
            draw_health_bar(SCREEN, x, y - 10, health)
            font = pygame.font.Font(None, 24)
            label = font.render(f"Player {i + 1}", True, (255, 255, 255))
            SCREEN.blit(label, (x, y - 25))
            player_animations[addr] = anim

        if len(players) == 1:
            font = pygame.font.Font(None, 140)
            text_surface = font.render("YOU  WIN!", True, (255, 255, 0))
            screen.blit(text_surface, (365, 60))

            pygame.draw.rect(screen, (50, 50, 50), button_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, border_radius=10)

            button_font = pygame.font.Font(None, 48)
            button_text = button_font.render("Exit", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        return "quit"

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()



def draw_polished_menu(screen, username):
    font = pygame.font.Font(None, 72)
    menu_font = pygame.font.Font(None, 48)
    welcome = pygame.font.Font(None, 28).render(f"Welcome, {username}", True, (240, 240, 240))

    options = ["Start Game", "Instructions", "Quit"]
    option_rects = []
    clock = pygame.time.Clock()

    running = True
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(menu_background, (0, 0))
        screen.blit(welcome, (20, 20))

        option_rects.clear()
        for i, option in enumerate(options):
            base_color = (255, 255, 255)
            hover_color = (255, 215, 0)
            rect = pygame.Rect(20, 430 + i * 60, 200, 50)
            is_hovered = rect.collidepoint(mouse_x, mouse_y)
            color = hover_color if is_hovered else base_color
            label = menu_font.render(option, True, color)
            label_rect = label.get_rect(center=rect.center)
            screen.blit(label, label_rect)
            option_rects.append((option, rect))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for option, rect in option_rects:
                    if rect.collidepoint(mouse_x, mouse_y):
                        return option

        clock.tick(60)

def first_second_screen_send_message():
    current_state = "video"
    username = ""

    while True:
        if current_state == "video":
            current_state = rm4.main()

        elif current_state == "login":
            root = tk.Tk()
            app = auth.App(root, client)
            root.mainloop()

            if not app.login_success:
                print("Login not completed. Exiting...")
                return

            username = app.get_login_user_n_password()[0]

            pygame.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            current_state = "menu"

        elif current_state == "menu":
            pygame.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Stick Fight")

            choice = draw_polished_menu(screen, username)
            if choice == "Start Game":
                fade_to_black(screen)
                current_state = "game"
            elif choice == "Instructions":
                fade_to_black(screen)
                draw_instructions_screen(screen)
                fade_to_black(screen)
            elif choice.lower() == "quit":
                current_state = "quit"


        elif current_state == "game":
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            current_state = game_loop(screen)



        elif current_state == "quit":
            pygame.quit()
            break

receive_thread = threading.Thread(target=receive_data, daemon=True)
receive_thread.start()
first_second_screen_send_message()
client.close()

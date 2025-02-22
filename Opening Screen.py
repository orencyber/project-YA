import pygame
import cv2
import numpy as np
import PIL
import time
from PIL import Image, ImageDraw, ImageFont
import run_mp4
import main_game  # Make sure this is imported


def draw_menu(screen, menu_font, bigger_font, options):
    # Your existing draw_menu function remains the same
    white = (255, 255, 255)
    yellow = (255, 255, 0)
    black = (0, 0, 0)
    image = pygame.image.load("main_menu.png")
    screen.blit(image, (0, 0))
    pygame.display.flip()

    title_text = menu_font.render("Stick Fight", True, white)
    screen.blit(title_text, (550, 100))

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for i, option in enumerate(options):
        option_rect = pygame.Rect(550, 200 + i * 50, 200, 50)
        if option_rect.collidepoint(mouse_x, mouse_y):
            option_text = bigger_font.render(option, True, yellow)
        else:
            option_text = menu_font.render(option, True, white)
        screen.blit(option_text, (550, 200 + i * 50))


def main():
    pygame.init()
    current_state = "welcome"

    while True:
        if current_state == "welcome":
            current_state = run_mp4.main()

        elif current_state == "main_menu":
            pygame.init()
            screen = pygame.display.set_mode((1280, 720))
            pygame.display.set_caption("Stick Fight")

            font = pygame.font.Font(None, 50)
            menu_font = pygame.font.Font(None, 36)
            options = ["Start Game", "Instructions", "Settings", "Quit"]

            running = True
            while running:
                screen.fill((0, 0, 0))
                draw_menu(screen, menu_font, font, options)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "quit"

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        for i, option in enumerate(options):
                            option_rect = pygame.Rect(550, 200 + i * 50, 200, 50)
                            if option_rect.collidepoint(mouse_x, mouse_y):
                                if option == "Quit":
                                    return "quit"
                                elif option == "Start Game":
                                    current_state = "game"
                                    running = False
                                elif option in ["Instructions", "Settings"]:
                                    # Handle these states if needed
                                    pass

                pygame.time.delay(10)

        elif current_state == "game":
            return main_game.main_game()

        elif current_state == "quit":
            break

    pygame.quit()


if __name__ == "__main__":
    main()
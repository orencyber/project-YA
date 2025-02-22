import cv2
import pygame
from pygame.locals import *

def main():
    pygame.init()

    # Load video using OpenCV
    cap = cv2.VideoCapture("captioned.mp4")

    # Get video dimensions (width and height)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(height, width)
    # Set up the Pygame window
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("MP4 Video Background")

    # Set up font for caption
    font = pygame.font.SysFont('Arial', 36)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:  # Handle key press
                running = False  # Exit the loop on key press

        # Read a frame from the video
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create a Pygame surface from the frame
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

            # Draw the video frame
            screen.blit(frame_surface, (0, 0))

            # Add caption on top of the video
            caption = font.render("PRESS ANY KEY", True, (0, 155, 255))
            screen.blit(caption, (width // 3 + 120, height - 70))  # Adjust text position

            pygame.display.flip()
        else:
            # If video ends, loop it
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        pygame.time.Clock().tick(120)  # FPS for smooth video playback

    cap.release()  # Release the video capture object
    pygame.quit()
    return "main_menu"


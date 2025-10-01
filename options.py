import pygame

def draw_options(screen):
    image1 = pygame.transform.scale(pygame.image.load("assets/image.png"), (1000, 700))
    screen.blit(image1, (0, 0))
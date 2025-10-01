import pygame
import sys
from options import draw_options

pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.font.init()
pygame.mixer.init()

pygame.mixer.init()

pygame.mixer.music.load("music/musicafondo.mp3")
volumen = 0.5
# Primero ajusta el volumen
pygame.mixer.music.set_volume(volumen)
# Después reproduce la música
pygame.mixer.music.play(-1)

pygame.display.set_caption("Scrat Happy")

image1 = pygame.transform.scale(pygame.image.load("assets/image.png"), (1000, 700))

def menu_principal(button_pressed):
    font = pygame.font.Font(None, 74)
    text = font.render("Scrat Happy", True, (255, 255, 255))
    text_rect = text.get_rect(centerx=screen.get_width() // 2, y=80)  # Centrado horizontal, y=80
    screen.blit(text, text_rect)

    button_rect = pygame.Rect(400, 300, 200, 60)
    if button_pressed:
        color = (0, 90, 180)
        offset = 4
    else:
        color = (0, 128, 255)
        offset = 0

    shadow_rect = button_rect.move(0, 6)
    pygame.draw.rect(screen, (30, 30, 60), shadow_rect, border_radius=30)
    button_rect = button_rect.move(0, offset)
    pygame.draw.rect(screen, color, button_rect, border_radius=30)

    button_font = pygame.font.Font(None, 50)
    button_text = button_font.render("Jugar", True, (255, 255, 255))
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)
    return button_rect

button_pressed = False
estado = "menu"

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if estado == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    button_pressed = True
            if event.type == pygame.MOUSEBUTTONUP:
                if button_pressed and button_rect.collidepoint(event.pos):
                    estado = "options"
                button_pressed = False
        elif estado == "options":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado = "menu"

    if estado == "menu":
        screen.blit(image1, (0, 0))
        button_rect = menu_principal(button_pressed)
    elif estado == "options":
        draw_options(screen)

    pygame.display.flip()
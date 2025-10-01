import pygame
import math
import sys
import random

# --- Configuración ---
WIDTH, HEIGHT = 800, 600
OBJ_COLOR = (240, 180, 90)
JOYSTICK_BASE_COLOR = (100, 100, 100)
JOYSTICK_HANDLE_COLOR = (200, 200, 200)
OBSTACLE_COLOR = (200, 50, 50)  # rojo
TARGET_COLOR = (50, 200, 50)    # verde
FPS = 60
SPEED = 5

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("music/musicafondo.mp3")
volumen = 0.5
# Primero ajusta el volumen
pygame.mixer.music.set_volume(volumen)
# Después reproduce la música
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrat Happy")
clock = pygame.time.Clock()

# --- Cargar imagen de fondo ---
try:
    background = pygame.image.load("assets/fondo.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    background = None

# --- Clases ---
class MovableShape:
    def __init__(self, x, y, size=50, shape_type="circle"):
        self.x = x
        self.y = y
        self.size = size
        self.shape_type = shape_type

    def draw(self, surface):
        if self.shape_type == "circle":
            pygame.draw.circle(surface, OBJ_COLOR, (int(self.x), int(self.y)), self.size // 2)
        else:
            rect = pygame.Rect(0, 0, self.size, self.size)
            rect.center = (int(self.x), int(self.y))
            pygame.draw.rect(surface, OBJ_COLOR, rect, border_radius=8)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        half = self.size // 2
        self.x = max(half, min(WIDTH - half, self.x))
        self.y = max(half, min(HEIGHT - half, self.y))

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

class Joystick:
    def __init__(self, x, y, radius=50):
        self.center_x = x
        self.center_y = y
        self.radius = radius
        self.handle_radius = 15
        self.active = True
        self.handle_x = x
        self.handle_y = y

    def draw(self, surface):
        if not self.active:
            return
        pygame.draw.circle(surface, JOYSTICK_BASE_COLOR, (self.center_x, self.center_y), self.radius, 3)
        pygame.draw.circle(surface, JOYSTICK_HANDLE_COLOR, (int(self.handle_x), int(self.handle_y)), self.handle_radius)

    def move_handle(self, x, y):
        dx = x - self.center_x
        dy = y - self.center_y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > self.radius:
            scale = self.radius / dist
            dx *= scale
            dy *= scale
        self.handle_x = self.center_x + dx
        self.handle_y = self.center_y + dy
        return dx / self.radius, dy / self.radius

    def reset(self):
        self.handle_x = self.center_x
        self.handle_y = self.center_y
        return 0, 0

class Obstacle:
    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, surface):
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = (int(self.x), int(self.y))
        pygame.draw.rect(surface, OBSTACLE_COLOR, rect)

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

class Target:
    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, surface):
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = (int(self.x), int(self.y))
        pygame.draw.rect(surface, TARGET_COLOR, rect)

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

# --- Inicialización ---
shape = MovableShape(WIDTH // 2, HEIGHT // 2, size=60, shape_type="circle")
joystick = Joystick(WIDTH // 2, HEIGHT - 100, radius=60)
move_vector = (0, 0)

obstacles = []
targets = []

# --- Generar objetos aleatorios ---
def generate_objects():
    global obstacles, targets
    obstacles = []
    targets = []

    def is_overlapping(new_rect):
        for obj in obstacles + targets:
            if new_rect.colliderect(obj.get_rect()):
                return True
        return False

    num_obstacles = random.randint(2, 3)
    for _ in range(num_obstacles):
        while True:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 150)
            size = random.randint(40, 90)
            new_obstacle = Obstacle(x, y, size)
            if not is_overlapping(new_obstacle.get_rect()):
                obstacles.append(new_obstacle)
                break

    while True:
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 150)
        size = random.randint(50, 70)
        new_target = Target(x, y, size)
        if not is_overlapping(new_target.get_rect()):
            targets.append(new_target)
            break

generate_objects()

# --- Funciones ---
def game_over():
    print("💥 ¡Has chocado! Reiniciando...")
    shape.x = WIDTH // 2
    shape.y = HEIGHT // 2
    joystick.reset()
    generate_objects()

def win():
    print("🎉 ¡Ganaste! 🎉")
    shape.x = WIDTH // 2
    shape.y = HEIGHT // 2
    joystick.reset()
    generate_objects()

# --- Bucle principal ---
running = True
while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEMOTION:
            if joystick and joystick.active and pygame.mouse.get_pressed()[0]:
                move_vector = joystick.move_handle(*event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and joystick:
                move_vector = joystick.reset()

    dx = move_vector[0] * SPEED
    dy = move_vector[1] * SPEED
    shape.move(dx, dy)

    shape_rect = shape.get_rect()

    for obs in obstacles:
        if shape_rect.colliderect(obs.get_rect()):
            game_over()

    for target in targets:
        if shape_rect.colliderect(target.get_rect()):
            win()

    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill((30, 30, 40))

    for obs in obstacles:
        obs.draw(screen)

    for target in targets:
        target.draw(screen)

    shape.draw(screen)
    if joystick:
        joystick.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()

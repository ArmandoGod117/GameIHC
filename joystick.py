import pygame
import sys
import math
import random

# --- Inicialización Global ---
pygame.init()
pygame.font.init()
pygame.mixer.init()

# --- Constantes Globales de Pantalla ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# Configura la pantalla (UNA SOLA VEZ)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Scrat Happy")

# Configura la música (una sola vez)
try:
    pygame.mixer.music.load("music/musicafondo.mp3")
    volumen = 0.5
    pygame.mixer.music.set_volume(volumen)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"No se pudo cargar la música: {e}")

# Carga la imagen de fondo del menú
try:
    image1 = pygame.transform.scale(pygame.image.load("assets/image.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error as e:
    print(f"No se pudo cargar la imagen del menú: {e}")
    image1 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    image1.fill((30, 30, 30))


# --- Función de Ayuda: Dibujar Botón ---
def draw_styled_button(screen, text, rect, pressed):
    font = pygame.font.Font(None, 50)
    
    if pressed:
        color = (0, 90, 180)
        offset = 4
    else:
        color = (0, 128, 255)
        offset = 0

    shadow_rect = rect.move(0, 6)
    pygame.draw.rect(screen, (30, 30, 60), shadow_rect, border_radius=30)
    
    button_rect_moved = rect.move(0, offset)
    pygame.draw.rect(screen, color, button_rect_moved, border_radius=30)

    button_text = font.render(text, True, (255, 255, 255))
    button_text_rect = button_text.get_rect(center=button_rect_moved.center)
    screen.blit(button_text, button_text_rect)
    
    return rect


# --- Función del Menú ---
def menu_principal(screen, button_pressed):
    font = pygame.font.Font(None, 74)
    text = font.render("Scrat Happy", True, (255, 255, 255))
    text_rect = text.get_rect(centerx=screen.get_width() // 2, y=80)
    screen.blit(text, text_rect)

    button_rect_jugar = pygame.Rect(400, 350, 200, 60)
    draw_styled_button(screen, "Jugar", button_rect_jugar, button_pressed)

    return button_rect_jugar


# --- Función del Juego ---
def run_game(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Scrat Happy - En Juego")

    JOYSTICK_BASE_COLOR = (100, 100, 100) 
    JOYSTICK_HANDLE_COLOR = (200, 200, 200)
    
    FPS = 60
    SPEED = 5

    clock = pygame.time.Clock()

    try:
        background = pygame.image.load("assets/fondo.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except pygame.error as e:
        print(f"No se pudo cargar el fondo del juego: {e}")
        background = None

    # --- Clases del Juego ---
    class MovableShape:
        def __init__(self, x, y, size=60):
            self.x = x
            self.y = y
            self.size = size
            self.original_image = None
            self.image = None
            self.facing_right = False

            try:
                self.original_image = pygame.image.load("assets/Scrat.png").convert_alpha()
                self.original_image = pygame.transform.scale(self.original_image, (self.size, self.size))
                self.image = self.original_image
            except pygame.error as e:
                print(f"No se pudo cargar la imagen de Scrat: {e}")
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (240, 180, 90), self.image.get_rect())

        def update_image_orientation(self, dx):
            if dx > 0 and not self.facing_right:
                self.image = pygame.transform.flip(self.original_image, True, False)
                self.facing_right = True
            elif dx < 0 and self.facing_right:
                self.image = self.original_image
                self.facing_right = False

        def draw(self, surface):
            image_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.image, image_rect)

        def move(self, dx, dy):
            self.update_image_orientation(dx)
            self.x += dx
            self.y += dy
            half_width = self.image.get_width() // 2
            half_height = self.image.get_height() // 2
            self.x = max(half_width, min(WIDTH - half_width, self.x))
            self.y = max(half_height, min(HEIGHT - half_height, self.y))

        def get_rect(self):
            return self.image.get_rect(center=(int(self.x), int(self.y)))


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
            try:
                self.image = pygame.image.load("assets/Tigre.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.size, self.size))
            except pygame.error as e:
                print(f"No se pudo cargar la imagen de Tigre.png: {e}")
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (200, 50, 50), self.image.get_rect())

        def draw(self, surface):
            image_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.image, image_rect)

        def get_rect(self):
            return self.image.get_rect(center=(int(self.x), int(self.y)))

    class Target:
        def __init__(self, x, y, size=50):
            self.x = x
            self.y = y
            self.size = size
            try:
                self.image = pygame.image.load("assets/Nue.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.size, self.size))
            except pygame.error as e:
                print(f"No se pudo cargar la imagen de Nue.png: {e}")
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (50, 200, 50), self.image.get_rect())

        def draw(self, surface):
            image_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.image, image_rect)

        def get_rect(self):
            return self.image.get_rect(center=(int(self.x), int(self.y)))

    # --- Inicialización ---
    shape = MovableShape(WIDTH // 2, HEIGHT // 2, size=60)
    joystick = Joystick(WIDTH // 2, HEIGHT - 100, radius=60)
    move_vector = (0, 0)
    obstacles = []
    targets = []
    score = 0  # Contador de nueces/bellotas

    def generate_objects():
        nonlocal obstacles, targets
        obstacles = []
        targets = []

        def is_overlapping(new_rect):
            for obj in obstacles:
                if new_rect.colliderect(obj.get_rect()):
                    return True
            for obj in targets:
                if new_rect.colliderect(obj.get_rect()):
                    return True
            if new_rect.colliderect(shape.get_rect()):
                return True
            return False

        num_obstacles = 4  # Siempre 4 tigres
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

    def reset_game():
        nonlocal score
        shape.x = WIDTH // 2
        shape.y = HEIGHT // 2
        joystick.reset()
        score = 0
        generate_objects()

    def game_over():
        print("💥 ¡Has chocado!")
        return "game_over"

    def collect_nut():
        nonlocal score, obstacles
        print("🎉 ¡Agarraste una nuez!")
        score += 1
        if score >= 10:
            return "victory"
        
        # Reposicionar todos los tigres en lugares aleatorios
        obstacles.clear()
        for _ in range(4):
            while True:
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 150)
                size = random.randint(40, 90)
                new_obstacle = Obstacle(x, y, size)
                valid = True
                # Verificar que no se sobreponga con otros tigres
                for obj in obstacles:
                    if new_obstacle.get_rect().colliderect(obj.get_rect()):
                        valid = False
                        break
                # Verificar que no esté sobre el personaje
                if new_obstacle.get_rect().colliderect(shape.get_rect()):
                    valid = False
                if valid:
                    obstacles.append(new_obstacle)
                    break
        
        # Generar nueva nuez
        while True:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 150)
            size = random.randint(50, 70)
            new_target = Target(x, y, size)
            valid = True
            for obj in obstacles:
                if new_target.get_rect().colliderect(obj.get_rect()):
                    valid = False
                    break
            if new_target.get_rect().colliderect(shape.get_rect()):
                valid = False
            if valid:
                targets.append(new_target)
                break
        return "playing"

    game_state = "playing"
    running = True
    button_pause_yes = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 + 20, 200, 60)
    button_pause_no = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 20, 200, 60)
    button_gameover_replay = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 + 20, 200, 60)
    button_gameover_menu = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 20, 200, 60)
    button_victory_menu = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 60)
    button_pressed_pause = None
    button_pressed_gameover = None
    button_pressed_victory = None

    while running:
        dt = clock.tick(FPS)
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = "paused"
                elif event.type == pygame.MOUSEMOTION:
                    if joystick and joystick.active and pygame.mouse.get_pressed()[0]:
                        move_vector = joystick.move_handle(*event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and joystick:
                        move_vector = joystick.reset()
            elif game_state == "paused":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = "playing"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_pause_yes.collidepoint(event.pos):
                        button_pressed_pause = "yes"
                    elif button_pause_no.collidepoint(event.pos):
                        button_pressed_pause = "no"
                if event.type == pygame.MOUSEBUTTONUP:
                    if button_pressed_pause == "yes" and button_pause_yes.collidepoint(event.pos):
                        running = False
                    elif button_pressed_pause == "no" and button_pause_no.collidepoint(event.pos):
                        game_state = "playing"
                    button_pressed_pause = None
            elif game_state == "game_over":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_gameover_replay.collidepoint(event.pos):
                        button_pressed_gameover = "replay"
                    elif button_gameover_menu.collidepoint(event.pos):
                        button_pressed_gameover = "menu"
                if event.type == pygame.MOUSEBUTTONUP:
                    if button_pressed_gameover == "replay" and button_gameover_replay.collidepoint(event.pos):
                        reset_game()
                        game_state = "playing"
                    elif button_pressed_gameover == "menu" and button_gameover_menu.collidepoint(event.pos):
                        running = False
                    button_pressed_gameover = None
            elif game_state == "victory":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_victory_menu.collidepoint(event.pos):
                        button_pressed_victory = "menu"
                if event.type == pygame.MOUSEBUTTONUP:
                    if button_pressed_victory == "menu" and button_victory_menu.collidepoint(event.pos):
                        running = False
                    button_pressed_victory = None

        if game_state == "playing":
            keys = pygame.key.get_pressed()
            dx = move_vector[0] * SPEED
            dy = move_vector[1] * SPEED
            if keys[pygame.K_LEFT]:
                dx -= SPEED
            if keys[pygame.K_RIGHT]:
                dx += SPEED
            if keys[pygame.K_UP]:
                dy -= SPEED
            if keys[pygame.K_DOWN]:
                dy += SPEED

            mag = math.sqrt(dx**2 + dy**2)
            if mag > SPEED:
                dx = (dx / mag) * SPEED
                dy = (dy / mag) * SPEED

            shape.move(dx, dy)
            shape_rect = shape.get_rect()

            for obs in obstacles:
                if shape_rect.colliderect(obs.get_rect()):
                    game_state = game_over()
            
            for target in targets[:]:
                if shape_rect.colliderect(target.get_rect()):
                    targets.remove(target)
                    result = collect_nut()
                    if result == "victory":
                        game_state = "victory"
                    break

        # Dibujar fondo
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((30, 30, 40))

        # Dibujar objetos del juego
        for obs in obstacles:
            obs.draw(screen)
        for target in targets:
            target.draw(screen)
        shape.draw(screen)
        if joystick:
            joystick.draw(screen)

        # Dibujar contador de nueces
        if game_state == "playing":
            font_score = pygame.font.Font(None, 60)
            score_text = font_score.render(f"Nueces: {score}/10", True, (255, 255, 255))
            score_bg = pygame.Surface((score_text.get_width() + 30, score_text.get_height() + 20), pygame.SRCALPHA)
            pygame.draw.rect(score_bg, (0, 0, 0, 150), score_bg.get_rect(), border_radius=15)
            screen.blit(score_bg, (WIDTH//2 - score_text.get_width()//2 - 15, 20))
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 30))

        # Pantalla de pausa
        if game_state == "paused":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            popup_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 100, 500, 220)
            pygame.draw.rect(screen, (30, 30, 60), popup_rect, border_radius=20)
            font_pausa = pygame.font.Font(None, 60)
            text_pausa = font_pausa.render("¿Salir al menú?", True, (255, 255, 255))
            text_rect = text_pausa.get_rect(centerx=WIDTH//2, y=HEIGHT//2 - 70)
            screen.blit(text_pausa, text_rect)
            draw_styled_button(screen, "Sí, Salir", button_pause_yes, button_pressed_pause == "yes")
            draw_styled_button(screen, "No, Seguir", button_pause_no, button_pressed_pause == "no")

        # Pantalla de Game Over
        if game_state == "game_over":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            popup_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 120, 500, 260)
            pygame.draw.rect(screen, (60, 30, 30), popup_rect, border_radius=20)
            font_gameover = pygame.font.Font(None, 70)
            text_gameover = font_gameover.render("¡Perdiste!", True, (255, 100, 100))
            text_rect = text_gameover.get_rect(centerx=WIDTH//2, y=HEIGHT//2 - 90)
            screen.blit(text_gameover, text_rect)
            font_info = pygame.font.Font(None, 40)
            text_info = font_info.render(f"Te atrapó el tigre", True, (255, 255, 255))
            text_info_rect = text_info.get_rect(centerx=WIDTH//2, y=HEIGHT//2 - 30)
            screen.blit(text_info, text_info_rect)
            draw_styled_button(screen, "Reintentar", button_gameover_replay, button_pressed_gameover == "replay")
            draw_styled_button(screen, "Menú", button_gameover_menu, button_pressed_gameover == "menu")

        # Pantalla de Victoria
        if game_state == "victory":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            popup_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 120, 500, 240)
            pygame.draw.rect(screen, (30, 60, 30), popup_rect, border_radius=20)
            font_victory = pygame.font.Font(None, 70)
            text_victory = font_victory.render("¡Ganaste!", True, (100, 255, 100))
            text_rect = text_victory.get_rect(centerx=WIDTH//2, y=HEIGHT//2 - 90)
            screen.blit(text_victory, text_rect)
            font_info = pygame.font.Font(None, 40)
            text_info = font_info.render("🎉 Recolectaste 10 nueces 🎉", True, (255, 255, 255))
            text_info_rect = text_info.get_rect(centerx=WIDTH//2, y=HEIGHT//2 - 30)
            screen.blit(text_info, text_info_rect)
            draw_styled_button(screen, "Menú", button_victory_menu, button_pressed_victory == "menu")

        pygame.display.flip()


# --- Bucle Principal (Manejador de Estados) ---
button_pressed = False
estado = "menu"
button_rect_jugar = pygame.Rect(0, 0, 0, 0)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if estado == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_jugar.collidepoint(event.pos):
                    button_pressed = True
            if event.type == pygame.MOUSEBUTTONUP:
                if button_pressed and button_rect_jugar.collidepoint(event.pos):
                    estado = "juego"
                button_pressed = False
        elif estado == "juego":
            pass

    if estado == "menu":
        screen.blit(image1, (0, 0))
        button_rect_jugar = menu_principal(screen, button_pressed)
    elif estado == "juego":
        run_game(screen)
        estado = "menu"
        pygame.display.set_caption("Scrat Happy")

    pygame.display.flip()
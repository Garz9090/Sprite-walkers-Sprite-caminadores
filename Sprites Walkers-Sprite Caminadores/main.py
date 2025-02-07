import pygame
import pygame_gui
import os
import cv2
import random

# Configuración inicial de Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Spritesheet Animation")

# Reloj para controlar los FPS
clock = pygame.time.Clock()

def load_sprites(folder):
    sprites = {}
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in dirs:
            path = os.path.join(root, name)
            animations = {'return': 'return/SPRITESHEET', 'paused': 'paused/SPRITESHEET'}
            sprites[name] = {'return': [], 'paused': []}
            for animation, file in animations.items():
                full_path = os.path.join(path, file)
                if os.path.exists(full_path):
                    spritesheets = os.listdir(full_path)
                    if spritesheets:
                        spritesheet_path = os.path.join(full_path, random.choice(spritesheets))
                        img_cv = cv2.imread(spritesheet_path)
                        for i in range(img_cv.shape[1] // 64):  # Assume sprite width = 100px
                            #el spritesheet mide 576x120 entre 9 fotogramas el ancho debe ser de 64
                            sub_img = img_cv[:, i * 64:(i + 1) * 64] # 64 harcodeado
                            h, w, _ = sub_img.shape #para saber las dimensiones
                            img_pygame = pygame.image.frombuffer(sub_img.tobytes(), (w, h), "BGR")
                            sprites[name][animation].append(img_pygame)
                    else:
                        print(f"No spritesheets found for {animation} in {path}")
                else:
                    print(f"No folder found for {animation} in {path}")
    return sprites

class Avatar(pygame.sprite.Sprite):
    def __init__(self, animations, name):
        super().__init__()
        self.animations = animations
        self.current_animation = 'return'
        self.current_frame = 0
        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.speed = 5
        self.moving_left = False
        self.name = name

    def update(self):
        self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])
        self.image = self.animations[self.current_animation][self.current_frame]
        if self.moving_left:
            self.image = pygame.transform.flip(self.image, True, False)

        # Movement
        if self.current_animation == 'return':
            self.rect.x += -self.speed if self.moving_left else self.speed
            if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
                self.moving_left = not self.moving_left

# Load all sprites
sprites = load_sprites('sprites')

# Initialize UI manager
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# UI Components
text_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 50), (200, 50)),
    manager=manager
)
add_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((260, 50), (100, 50)),
    text='Add',
    manager=manager
)
remove_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((370, 50), (100, 50)),
    text='Remove',
    manager=manager
)
close_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((480, 50), (100, 50)),
    text='Close',
    manager=manager
)

# Sprite group
avatar_group = pygame.sprite.Group()

# Game loop
running = True
while running:
    time_delta = clock.tick(30) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.process_events(event)

        # Add avatar when Add button is pressed
        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == add_button:
                avatar_name = text_entry.get_text()
                if avatar_name:
                    if avatar_name in sprites:
                        new_avatar = Avatar(sprites[avatar_name], avatar_name)
                        avatar_group.add(new_avatar)
                    else:
                        print(f"No sprites found for avatar {avatar_name}")
                text_entry.set_text('')

        # Remove selected avatar when Remove button is pressed
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for avatar in avatar_group:
                    if avatar.rect.collidepoint(event.pos):
                        avatar_group.remove(avatar)
                        break

        # Close the program when Close button is pressed
        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == close_button:
                running = False

    manager.update(time_delta)

    screen.fill((0, 0, 0))  # Clear screen with black
    avatar_group.update()
    avatar_group.draw(screen)

    manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()

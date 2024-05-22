"""
Mortadella Hop - A platformer game using Pygame
"""

import time
import random
import sys
from threading import Thread, Lock
import pygame

# Create a lock object to manage thread synchronization (mutex)
LOCK = Lock()

# Initialize Pygame modules
pygame.init()
pygame.mixer.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Mortadella Hop')

# Game settings
CLOCK = pygame.time.Clock()
FPS = 60

# Load images
BACKGROUND_IMG = pygame.image.load('background.png').convert()
PLAYER_IMG = pygame.transform.scale(
    pygame.image.load('player.png').convert_alpha(), (50, 50)
)
COIN_IMG = pygame.transform.scale(
    pygame.image.load('coin.png').convert_alpha(), (20, 20)
)
PLATFORM_IMG = pygame.transform.scale(
    pygame.image.load('platform.png').convert_alpha(), (100, 20)
)
GROUND_IMG = pygame.transform.scale(
    pygame.image.load('ground.png').convert_alpha(), (SCREEN_WIDTH, 20)
)

# Character variables
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100]
player_size = PLAYER_IMG.get_size()
PLAYER_SPEED = 7.6
VELOCITY = 0
GRAVITY = 0.5
IS_JUMPING = True

# Coins and score variables
coins = []
COIN_SIZE = (20, 20)
SCORE = 0
FONT = pygame.font.Font(None, 36)

# Starting platform
terrain = [
    [0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20],
]

# List to hold moving platforms
moving_platforms = []

# Game state
GAME_OVER = False


def create_new_platform():
    """
    Create a new moving platform and add it to the list.
    """
    reference_height = moving_platforms[-1][1] if moving_platforms else SCREEN_HEIGHT
    new_platform_height = reference_height - random.randint(50, 80)
    new_platform_height = max(new_platform_height, 50)

    new_platform_x = random.randint(0, SCREEN_WIDTH - 100)
    new_platform = [new_platform_x, new_platform_height, 100, 20, random.choice([-1, 1])]
    moving_platforms.append(new_platform)


def create_initial_moving_platforms():
    """
    Create the initial set of moving platforms.
    """
    initial_platform_count = 8
    for _ in range(initial_platform_count):
        create_new_platform()


def move_moving_platforms():
    """
    Continuously move the moving platforms.
    """
    while True:
        time.sleep(0.05)
        with LOCK:
            for platform in moving_platforms:
                platform[0] += platform[4] * 11
                if platform[0] <= 0 or platform[0] + platform[2] >= SCREEN_WIDTH:
                    platform[4] *= -1

            if len(moving_platforms) < 8:
                create_new_platform()

            # Remove platforms that have moved off the screen
            if moving_platforms and moving_platforms[0][1] >= SCREEN_HEIGHT:
                moving_platforms.pop(0)
                create_new_platform()


def generate_coins():
    """
    Generate coins at random positions.
    """
    max_jump_height = 150
    margin_above_platform = 30
    while True:
        if len(coins) < 5 and moving_platforms:
            for _ in range(5 - len(coins)):
                placed = False
                while not placed:
                    platform = random.choice(moving_platforms)
                    coin_x = random.randint(
                        platform[0], platform[0] + platform[2] - COIN_SIZE[0]
                    )
                    coin_y = platform[1] - COIN_SIZE[1] - margin_above_platform
                    coin_pos = [coin_x, coin_y]

                    # Ensure the coin is within a reasonable height range
                    if any(
                        rect[1] - max_jump_height < coin_pos[1] < rect[1] + max_jump_height
                        for rect in moving_platforms
                    ):
                        coins.append(coin_pos)
                        placed = True
        time.sleep(2)


def play_background_music():
    """
    Play background music.
    """
    pygame.mixer.music.load('background_music.mp3')
    pygame.mixer.music.play(-1)


def player_physics():
    """
    Handle the physics of the player character.
    """
    global IS_JUMPING, VELOCITY, player_pos, SCORE, coins, GAME_OVER

    while not GAME_OVER:
        time.sleep(0.02)
        with LOCK:
            player_rect = pygame.Rect(*player_pos, *player_size)
            terrain_rects = [pygame.Rect(*rect[:4]) for rect in terrain + moving_platforms]

            standing_on_platform = False

            for tr in terrain_rects:
                if player_rect.colliderect(tr) and VELOCITY >= 0:
                    if player_pos[1] + player_size[1] <= tr.top + (VELOCITY + GRAVITY):
                        IS_JUMPING = False
                        VELOCITY = 0
                        player_pos[1] = tr.top - player_size[1]
                        standing_on_platform = True
                        break

            if not standing_on_platform:
                IS_JUMPING = True
                VELOCITY += GRAVITY
                player_pos[1] += VELOCITY

            # Check if player has fallen off the screen
            if player_pos[1] > SCREEN_HEIGHT:
                GAME_OVER = True
                return

            coins_copy = coins[:]
            for coin in coins_copy:
                coin_rect = pygame.Rect(*coin, *COIN_SIZE)
                if player_rect.colliderect(coin_rect):
                    coins.remove(coin)
                    SCORE += 1


def scroll_screen():
    """
    Scroll the screen and platforms smoothly.
    """
    global player_pos, terrain, moving_platforms, coins
    scroll_speed = 1
    time.sleep(4.5)  # Initial delay before scrolling starts
    while not GAME_OVER:
        time.sleep(0.02)
        with LOCK:
            player_pos[1] += scroll_speed

            for platform in terrain:
                platform[1] += scroll_speed
            for platform in moving_platforms:
                platform[1] += scroll_speed
            for coin in coins:
                coin[1] += scroll_speed

            # Remove off-screen elements
            terrain = [platform for platform in terrain if platform[1] < SCREEN_HEIGHT]
            moving_platforms = [platform for platform in moving_platforms if platform[1] < SCREEN_HEIGHT]
            coins = [coin for coin in coins if coin[1] < SCREEN_HEIGHT]


def draw_coins():
    """
    Draw coins on the screen.
    """
    for coin in coins:
        SCREEN.blit(COIN_IMG, coin)


def draw_terrain():
    """
    Draw platforms on the screen.
    """
    for rect in terrain:
        SCREEN.blit(GROUND_IMG, (rect[0], rect[1]))
    for rect in moving_platforms:
        SCREEN.blit(PLATFORM_IMG, (rect[0], rect[1]))


def draw_score():
    """
    Draw the score on the screen.
    """
    score_text = FONT.render(f'Score: {SCORE}', True, (255, 255, 255))
    SCREEN.blit(score_text, (10, 10))


def display_final_score():
    """
    Display the final score when the game is over.
    """
    SCREEN.fill((0, 0, 0))
    final_score_text = FONT.render(
        f'You fell and collected {SCORE} mortadellas', True, (255, 255, 255)
    )
    SCREEN.blit(
        final_score_text,
        (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2),
    )
    pygame.display.flip()
    time.sleep(1.5)
    pygame.quit()
    sys.exit()


def game_loop():
    """
    The main game loop.
    """
    global VELOCITY, IS_JUMPING, SCORE, GAME_OVER
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if GAME_OVER:
            display_final_score()
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_pos[0] -= PLAYER_SPEED
        if keys[pygame.K_d]:
            player_pos[0] += PLAYER_SPEED
        if keys[pygame.K_w] and not IS_JUMPING:
            IS_JUMPING = True
            VELOCITY = -10

        # Ensure player stays within screen bounds
        if player_pos[0] < 0:
            player_pos[0] = 0
        if player_pos[0] + player_size[0] > SCREEN_WIDTH:
            player_pos[0] = SCREEN_WIDTH - player_size[0]

        # Draw everything on the screen
        SCREEN.blit(BACKGROUND_IMG, (0, 0))
        draw_terrain()
        draw_coins()
        SCREEN.blit(PLAYER_IMG, player_pos)
        draw_score()
        pygame.display.flip()
        CLOCK.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    create_initial_moving_platforms()

    moving_platforms_movement_thread = Thread(target=move_moving_platforms)
    moving_platforms_movement_thread.daemon = True
    moving_platforms_movement_thread.start()

    coin_thread = Thread(target=generate_coins)
    coin_thread.daemon = True
    coin_thread.start()

    music_thread = Thread(target=play_background_music)
    music_thread.daemon = True
    music_thread.start()

    physics_thread = Thread(target=player_physics)
    physics_thread.daemon = True
    physics_thread.start()

    scroll_thread = Thread(target=scroll_screen)
    scroll_thread.daemon = True
    scroll_thread.start()

    game_loop()

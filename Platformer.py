import pygame
import sys
import time
import random
from threading import Thread
from threading import Lock
lock = Lock()  # Create a lock object to manage threads

pygame.init()
pygame.mixer.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Mortadella Hop: The Gold collection game')

# Game settings
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 223, 0)

# Character variables
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100]
player_size = [50, 50]
player_color = WHITE
player_speed = 5
velocity = 0
gravity = 0.5
is_jumping = True

# Coins, score, and countdown variables
coins = []
coin_size = [20, 20]
coin_color = GOLD
score = 0
countdown = 33
font = pygame.font.Font(None, 36)

# Terrain and platforms
terrain = [
    # Definition of platforms using rectangles [x, y, width, height]
    [0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20],
    [150, SCREEN_HEIGHT - 100, 100, 20],
    [350, SCREEN_HEIGHT - 180, 120, 20],
    [550, SCREEN_HEIGHT - 250, 80, 20],
    [150, SCREEN_HEIGHT - 250, 100, 20],
]

# Countdown timer function
def countdown_timer():
    global countdown
    while countdown > 0:
        time.sleep(1)
        countdown -= 1

# Function to generate coins in random positions
def generate_coins():
    max_jump_height = 150
    while True:
        if not coins:
            for _ in range(5):
                placed = False
                while not placed:
                    # Generate random position for coin
                    coin_pos = [random.randint(0, SCREEN_WIDTH - 20), random.randint(0, SCREEN_HEIGHT - 120)]
                    coin_rect = pygame.Rect(*coin_pos, *coin_size)  # Create coin rectangle
                    # Check collision with platforms and place within jump height
                    if not any(coin_rect.colliderect(pygame.Rect(*rect)) for rect in terrain) and \
                            any(coin_pos[1] < rect[1] + max_jump_height and coin_pos[1] > rect[1] - max_jump_height for rect in terrain):
                        coins.append(coin_pos)  # Add coin position to list
                        placed = True
        time.sleep(2)

# Function to play background music
def play_background_music():
    pygame.mixer.music.load('background_music.mp3')
    pygame.mixer.music.play(-1)  # Play music on loop

# Function to handle gravity and jumping logic
def gravity_and_jump():
    global is_jumping, velocity, player_pos, score, coins
    while True:
        time.sleep(0.02)  # Small delay to reduce CPU usage
        with lock:  # Lock thread to update player and coins positions safely
            player_rect = pygame.Rect(*player_pos, *player_size)  # Player rectangle
            terrain_rects = [pygame.Rect(*rect) for rect in terrain]  # Terrain rectangles
            standing_on_platform = False  # Flag to check if the player is standing on a platform

            # Check collision with the terrain
            for tr in terrain_rects:
                if player_rect.colliderect(tr) and velocity >= 0:  # Ensure the player is falling or on a platform
                    # Condition to "snap" the player onto the platform from below
                    if player_pos[1] + player_size[1] <= tr.top + (velocity + gravity):
                        is_jumping = False
                        velocity = 0
                        player_pos[1] = tr.top - player_size[1]
                        standing_on_platform = True
                        break

            # If the player is not on a platform, they start falling
            if not standing_on_platform:
                is_jumping = True
                velocity += gravity
                player_pos[1] += velocity

            # Reset the player position if they hit the "ground"
            if player_pos[1] >= SCREEN_HEIGHT - player_size[1]:
                player_pos[1] = SCREEN_HEIGHT - player_size[1]
                is_jumping = False
                velocity = 0

            # Check for and collect coins
            coins_copy = coins[:]
            for coin in coins_copy:
                coin_rect = pygame.Rect(*coin, *coin_size)
                if player_rect.colliderect(coin_rect):
                    coins.remove(coin)
                    score += 10

# Drawing functions
def draw_coins():
    for coin in coins:
        pygame.draw.rect(screen, coin_color, (*coin, *coin_size))  # Draw each coin

def draw_terrain():
    for rect in terrain:
        pygame.draw.rect(screen, WHITE, rect)  # Draw each platform

def draw_score_and_time():
    score_text = font.render(f'Score: {score}', True, WHITE)  # Render the score text
    time_text = font.render(f'Time: {countdown}', True, WHITE)  # Render the countdown timer
    screen.blit(score_text, (10, 10))  # Display the score
    screen.blit(time_text, (SCREEN_WIDTH - 150, 10))  # Display the timer

def display_final_score():
    screen.fill(BLACK)  # Clear the screen
    final_score_text = font.render(f'Final Score: {score}', True, WHITE)  # Render the final score text
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))  # Center the final score text
    pygame.display.flip()  # Update the display
    time.sleep(5)  # Give the player time to see their final score

# Main game loop
def game_loop():
    global velocity, is_jumping, score, running
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check for window close button
                running = False

        keys = pygame.key.get_pressed()  # Get the state of all keyboard buttons
        if keys[pygame.K_LEFT]:  # Move left if the left arrow key is pressed
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]:  # Move right if the right arrow key is pressed
            player_pos[0] += player_speed

        if keys[pygame.K_UP] and not is_jumping:  # Jump if the up arrow key is pressed and not already jumping
            is_jumping = True
            velocity = -10  # Set the initial jump velocity

        screen.fill(BLACK)
        draw_terrain()
        draw_coins()
        pygame.draw.rect(screen, player_color, (*player_pos, *player_size))
        draw_score_and_time()

        if countdown <= 0:
            display_final_score()  # Display the final score when the timer runs out
            break  # Exit the game loop

        pygame.display.flip()  # Update the full display Surface to the screen
        clock.tick(FPS)  # Limit the speed of the game loop

# Run the game and threads
if __name__ == "__main__":
    countdown_thread = Thread(target=countdown_timer)  # Create a thread for the countdown timer
    countdown_thread.daemon = True  # Set the thread as a daemon
    countdown_thread.start()  # Start the countdown timer thread

    coin_thread = Thread(target=generate_coins)
    coin_thread.daemon = True
    coin_thread.start()

    music_thread = Thread(target=play_background_music)
    music_thread.daemon = True
    music_thread.start()

    gravity_thread = Thread(target=gravity_and_jump)
    gravity_thread.daemon = True
    gravity_thread.start()

    game_loop()

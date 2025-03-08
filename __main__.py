from ursina import *
import random

app = Ursina(title="Subway Surfeuille", borderless=False, fullscreen=True)

# Assurer que la police est bien chargée
Text.default_font = 'VeraMono.ttf'  # Facultatif mais peut aider sur certaines configurations

# Load assets
player = Entity(model='cube', color=color.orange, scale=(1, 1, 1), position=(0, 1, -5))
road_segments = [
    Entity(model='cube', color=color.gray, scale=(6, 0.1, 20), position=(0, 0, i))
    for i in range(-20, 40, 20)
]

# Game variables
lanes = [-2, 0, 2]
current_lane = 1
speed = 5
obstacles = []
time_elapsed = 0
lives = 3
score = 0

# UI Elements
lives_text = Text(text=f'Lives: {lives}',
                  origin=(-1, 1),  # Alignement en haut à gauche
                  position=(-0.70, 0.45),  # Position en haut à gauche
                  scale=1.5,
                  color=color.white,
                  background=True)

score_text = Text(text=f'Score: {score}',
                  origin=(-1, 1),  # Alignement en haut à gauche
                  position=(-0.70, 0.30),  # Juste en dessous
                  scale=1.5,
                  color=color.white,
                  background=True)

# Input handling
def input(key):
    global current_lane
    if key in ['a', 'left'] and current_lane > 0:
        current_lane -= 1
        player.x = lanes[current_lane]
    elif key in ['d', 'right'] and current_lane < 2:
        current_lane += 1
        player.x = lanes[current_lane]

# Update function
def update():
    global speed, time_elapsed, lives, score
    time_elapsed += time.dt
    speed = 5 + (time_elapsed // 10)  # Increase speed over time
    score += 1  # Increment score
    score_text.text = f'Score: {score}'  # Update text
    score_text.visible = True  # Assurer l'affichage

    # Jumping
    if held_keys['space'] and player.y <= 1:
        player.animate_y(6, duration=0.3, curve=curve.out_quad)
        invoke(setattr, player, 'y', 1, delay=0.6)

    # Spawn obstacles
    if random.random() < 0.02:
        lane = random.choice(lanes)
        obstacles.append(Entity(model='rock', texture='rock', scale=(0.1, 0.1, 0.1), position=(lane, 1, 20)))

    if random.random() < 0.02:
        lane = random.choice(lanes)
        obstacles.append(Entity(model='cube', color=color.yellow, scale=(1, 2, 1), position=(lane, 4, 20)))

    # Move obstacles & check collisions
    for obs in obstacles[:]:
        obs.z -= time.dt * speed

        if abs(obs.z - player.z) < 0.2 and abs(obs.x - player.x) < 0.2 and abs(obs.y - player.y) < 0.2:
            lives -= 1
            lives_text.text = f'Lives: {lives}'  # Update text
            lives_text.visible = True  # Assurer l'affichage
            obstacles.remove(obs)
            destroy(obs)
            if lives <= 0:
                print("Game Over")
                application.quit()

        if abs(obs.z - player.z) < 1 and abs(obs.x - player.x) < 1 and abs(obs.y - player.y) < 1:
            lives -= 1
            lives_text.text = f'Lives: {lives}'  # Update text
            lives_text.visible = True  # Assurer l'affichage
            obstacles.remove(obs)
            destroy(obs)
            if lives <= 0:
                print("Game Over")
                application.quit()

        elif obs.z < -10:  # Remove off-screen obstacles
            obstacles.remove(obs)
            destroy(obs)

    # Move road segments
    for road in road_segments:
        road.z -= time.dt * speed
        if road.z < -30:
            road.z += 60  # Loop road segment

# Camera setup
camera.position = (0, 15, -30)
camera.rotation_x = 25

app.run()

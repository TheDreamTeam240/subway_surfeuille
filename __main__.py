from ursina import *
import random

app = Ursina()

# Load assets
player = Entity(model='cube', color=color.orange, scale=(1, 2, 1), position=(0, 1, -5))
road = Entity(model='cube', color=color.gray, scale=(6, 0.1, 50), position=(0, 0, -10))

# Game variables
lanes = [-2, 0, 2]
current_lane = 1
speed = 5
obstacles = []
time_elapsed = 0
lives = 3
lives_text = Text(text=f'Lives: {lives}', position=(-0.85, 0.45), scale=2, color=color.white)

def input(key):
    global current_lane
    if key == 'a' or key == 'left':
        if current_lane > 0:
            current_lane -= 1
            player.x = lanes[current_lane]
    elif key == 'd' or key == 'right':
        if current_lane < 2:
            current_lane += 1
            player.x = lanes[current_lane]

def update():
    global speed, time_elapsed, lives
    time_elapsed += time.dt
    speed = 5 + (time_elapsed // 10)  # Increase speed over time
    
    # Jumping
    if held_keys['space'] and player.y <= 1:
        player.animate_y(2.5, duration=0.3, curve=curve.out_quad)
        invoke(setattr, player, 'y', 1, delay=0.6)
    
    # Spawn obstacles
    if random.random() < 0.02:
        lane = random.choice(lanes)
        obstacle = Entity(model='cube', color=color.red, scale=(1, 2, 1), position=(lane, 1, 20))
        obstacles.append(obstacle)
    
    # Move obstacles and road backward
    for obs in obstacles:
        obs.z -= time.dt * speed
        
        # Check collision
        if abs(obs.z - player.z) < 1 and abs(obs.x - player.x) < 1:
            lives -= 1
            lives_text.text = f'Lives: {lives}'
            obstacles.remove(obs)
            destroy(obs)
            if lives <= 0:
                print("Game Over")
                application.quit()
                
        if obs.z < -10:
            obstacles.remove(obs)
            destroy(obs)
    
    road.z -= time.dt * speed  # Move road backward
    if road.z < -20:
        road.z += 20  # Reset road position to create an infinite effect

camera.position = (0, 5, -15)
camera.rotation_x = 20

app.run()

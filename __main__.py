from ursina import *
import random

app = Ursina(title="Subway Surfeuille", borderless=False, fullscreen=True)

# Assurer que la police est bien chargée
Text.default_font = 'VeraMono.ttf'  # Facultatif mais peut aider sur certaines configurations

# Load assets
player = Entity(model='cube', color=color.orange, scale=(1, 1, 1), position=(0, 1, -5))

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

class WaterParticle(Entity):
    def __init__(self, position, direction, speed, lifetime=5):
        super().__init__(
            model='sphere',  
            scale=random.uniform(0.1, 0.3),  # Random size for variation
            color=random.choice([color.blue, color.azure, color.cyan, color.turquoise]),  # Using only the available blue shades
            position=position,
            texture='white_cube',
            alpha=random.uniform(0.5, 0.8)  # Random transparency for better effect
        )
        self.direction = direction
        self.speed = speed
        self.lifetime = lifetime

    def update(self):
        self.position += self.direction * self.speed * time.dt
        self.lifetime -= time.dt
        if self.lifetime <= 0:
            destroy(self)

class River(Entity):
    def __init__(self, start_pos, width=10, particle_count=50):
        super().__init__()
        self.start_pos = start_pos
        self.width = width
        self.particle_count = particle_count
        self.spawn_particles()

    def spawn_particles(self):
        for _ in range(self.particle_count):
            direction = Vec3(0, 0, random.uniform(0.5, 1.5))  # Mouvement vers l'arrière
            position = self.start_pos + Vec3(random.uniform(-self.width/2, self.width/2), 0, random.uniform(-0.5, 0.5))
            speed = random.uniform(1, 3)
            WaterParticle(position, direction, speed)

    def update(self):
        self.spawn_particles()

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
        player.animate_y(6, duration=0.3, curve=curve.out_sine)
        invoke(setattr, player, 'y', 1, delay=0.6)



    # Spawn obstacles
    if random.random() < 0.02:
        lane = random.choice(lanes)
        obstacles.append(Entity(model=random.choice(['rock-sl-1', 'rock-sl-2', 'rock']), texture=random.choice(['rock_diffuse.png', 'rock_roughness.png', 'rock_specular.png']), scale=(0.1, 0.1, 0.1), position=(lane, 1, 20),
                         rotation=(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360))))

    if random.random() < 0.02:
        lane = random.choice(lanes)
        obstacles.append(Entity(model='Tree_Spooky2_Low', texture=random.choice(['tree1.jpg', 'tree2.jpg', 'tree3.jpg']), scale=(0.02, 0.02, 0.02), position=(lane, 4, 20)));

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

river = River(start_pos=Vec3(0, 0.1, -5), width=15, particle_count=10)

# Camera setup
camera.position = (0, 10, -20)
camera.rotation_x = 25

app.run()

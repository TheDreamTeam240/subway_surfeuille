from ursina import *
import random

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
    def __init__(self, start_pos, end_pos, particle_count=15):
        super().__init__()
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.particle_count = particle_count
        self.spawn_particles()

    def spawn_particles(self):
        for _ in range(self.particle_count):
            direction = Vec3(0, 0, random.uniform(0.5, 1))  # Moving forward in Z direction
            position = self.start_pos + Vec3(random.uniform(-2, 2), 0, random.uniform(-0.5, 0.5))
            speed = random.uniform(1, 2)
            WaterParticle(position, direction, speed)

    def update(self):
        self.spawn_particles()

# Ursina App
app = Ursina()

# Set up top-down camera
camera.position = (0, 10, -20)
camera.rotation_x = 25

# Ground
ground = Entity(model='plane', scale=(15, 1, 15), color=color.green, texture='grass')

# River
river = River(start_pos=Vec3(0, 0.1, -5), end_pos=Vec3(0, 0.1, 5), particle_count=10)

app.run()

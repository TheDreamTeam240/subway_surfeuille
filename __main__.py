from ursina import *
import random
import math

app = Ursina(title="Subway Surfeuille", borderless=False, fullscreen=True)

Text.default_font = 'VeraMono.ttf'

player = Entity(model='leaf', color=color.green, scale=(0.01, 0.01, 0.01), position=(0, 0.2, -5))

lanes = [-2, 0, 2]
current_lane = 1
speed = 5
obstacles = []
time_elapsed = 0
lives = 10
score = 0

lives_text = Text(text=f'Lives: {lives}',
                  origin=(-1, 1),
                  position=(-0.70, 0.45),
                  scale=1.5,
                  color=color.white,
                  background=True)

score_text = Text(text=f'Score: {score}',
                  origin=(-1, 1),
                  position=(-0.70, 0.30),
                  scale=1.5,
                  color=color.white,
                  background=True)

water_shader = Shader(
    language=Shader.GLSL,
    vertex='''
#version 110
attribute vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float time;
varying vec3 world_pos;

void main() {
    vec4 pos = p3d_Vertex;
    float wave_height = 0.1 * sin(pos.x * 0.5 + time) * cos(pos.z * 0.3 + time * 0.7);
    pos.y += wave_height;
    gl_Position = p3d_ModelViewProjectionMatrix * pos;
    world_pos = pos.xyz;
}
    ''',
    fragment='''
#version 110
varying vec3 world_pos;
uniform vec3 light_pos;
uniform float time;

void main() {
    vec3 base_color = vec3(0.0, 0.5, 0.8);
    float wave = 0.5 + 0.5 * sin(world_pos.x * 0.5 + world_pos.z * 0.3 + time);
    vec3 water_color = base_color * wave;

    vec3 light_dir = normalize(light_pos - world_pos);
    float diffuse = max(0.0, dot(vec3(0.0, 1.0, 0.0), light_dir));
    water_color += vec3(diffuse) * 0.3;

    gl_FragColor = vec4(water_color, 0.85);
}
    '''
)

particle_shader = Shader(
    language=Shader.GLSL,
    vertex='''
#version 110
attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;
varying vec2 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
}
    ''',
    fragment='''
#version 110
varying vec2 texcoord;
uniform sampler2D p3d_Texture0;
uniform float time;

void main() {
    vec4 color = texture2D(p3d_Texture0, texcoord);
    float brightness = 0.5 + 0.5 * sin(time * 5.0 + texcoord.x * texcoord.y);
    vec3 water_color = vec3(0.2, 0.6, 0.9);
    float alpha = 0.8 * (1.0 - texcoord.y) * brightness;
    gl_FragColor = vec4(water_color * brightness, alpha);
}
    '''
)

class WaterParticle(Entity):
    def __init__(self, position, direction, speed, lifetime=1, is_splash=False, is_foam=False):
        if is_foam:
            scale = 0.02
        elif is_splash:
            scale = random.uniform(0.02, 0.08)
        else:
            scale = random.uniform(0.03, 0.15)

        super().__init__(
            model='quad',
            scale=scale,
            color=color.rgb(26, 17, 122),
            position=position,
            texture='white_cube',
            billboard=True,
            alpha=0.6 if is_foam else 0.8,
            shader=particle_shader
        )
        self.direction = direction
        self.base_speed = speed
        self.speed_factor = max(0.1, 1 - (abs(self.x) / 7.5)**2)
        self.speed = self.base_speed * self.speed_factor
        self.lifetime = lifetime
        self.time_alive = 0
        self.is_splash = is_splash
        self.is_foam = is_foam
        self.velocity_y = random.uniform(0.5, 1.5) if is_splash else 0
        self.set_shader_input("time", 0.0)

    def update(self):
        turbulence = Vec3(random.uniform(-0.02, 0.02), 0, random.uniform(-0.02, 0.02))
        self.position += (self.direction * self.speed * time.dt) + (turbulence * time.dt)

        if self.is_splash:
            self.velocity_y -= 9.8 * time.dt
            self.y += self.velocity_y * time.dt
        elif self.is_foam:
            self.y = 0.1
            self.position += Vec3(random.uniform(-0.01, 0.01), 0, random.uniform(-0.01, 0.01)) * time.dt
        else:
            self.time_alive += time.dt
            z = self.z
            t = self.time_alive
            wave1 = 0.03 * math.sin(math.pi * z - math.pi * t)
            wave2 = 0.02 * math.sin(2 * math.pi * z - 2 * math.pi * t)
            self.y = 0.1 + wave1 + wave2

        self.set_shader_input("time", time.time())
        self.lifetime -= time.dt
        if self.lifetime <= 0:
            destroy(self)
            del self

class River(Entity):
    def __init__(self, start_pos, width=5, particle_count=50, spawn_rate=1):
        super().__init__()
        self.start_pos = start_pos
        self.width = width
        self.particle_count = particle_count
        self.spawn_rate = spawn_rate
        self.last_spawn_time = time.time()

        self.water_surface = Entity(
            model='plane',
            scale=(self.width, 0, 60),
            position=(self.start_pos.x, 0.1, self.start_pos.z),
            color=color.rgb(26, 17, 122),
            texture='white_cube',
            shader=water_shader
        )
        self.water_surface.set_shader_input("light_pos", Vec3(10, 10, 10))
        self.water_surface.set_shader_input("time", 0.0)
        self.spawn_initial_particles()

    def spawn_initial_particles(self):
        for _ in range(self.particle_count):
            self.create_particle()
        for _ in range(self.particle_count // 2):
            self.create_particle(is_foam=True, position=Vec3(random.choice([-7, 7]), 0.1, random.uniform(-30, 30)))

    def create_particle(self, is_splash=False, is_foam=False, position=None):
        direction = Vec3(0, 0, random.uniform(0.5, 1.5))
        if position is None:
            position = self.start_pos + Vec3(random.uniform(-self.width/2, self.width/2), 0, random.uniform(-30, 30))
        speed = random.uniform(1, 3)
        # Augmentation de la durée de vie
        lifetime = random.uniform(20, 40) if not is_splash else random.uniform(1, 3)
        lifetime = random.uniform(15, 25) if is_foam else lifetime
        WaterParticle(position, direction, speed, lifetime, is_splash, is_foam)

    def update(self):
        current_time = time.time()
        time_since_last_spawn = current_time - self.last_spawn_time
        if time_since_last_spawn >= 1 / self.spawn_rate:
            self.create_particle()
            self.last_spawn_time = current_time

        self.water_surface.set_shader_input("time", time.time())
        self.water_surface.set_shader_input("light_pos", Vec3(10, 10, 10))

        if player.y < 0.5 and abs(player.z) < 30:
            if random.random() < 0.02:
                splash_pos = Vec3(player.x + random.uniform(-0.5, 0.5), 0.1, player.z + random.uniform(-0.5, 0.5))
                self.create_particle(is_splash=True, position=splash_pos)
                for _ in range(8):
                    ripple_pos = Vec3(player.x + random.uniform(-1, 1), 0.1, player.z + random.uniform(-1, 1))
                    self.create_particle(position=ripple_pos)


def input(key):
    global current_lane
    if key in ['a', 'left'] and current_lane > 0:
        current_lane -= 1
        player.x = lanes[current_lane]
    elif key in ['d', 'right'] and current_lane < 2:
        current_lane += 1
        player.x = lanes[current_lane]


def update():
    global speed, time_elapsed, lives, score
    time_elapsed += time.dt
    speed = 5 + (time_elapsed // 10)
    score += 1
    score_text.text = f'Score: {score}'
    score_text.visible = True

    if held_keys['space'] and player.y <= 1:
        player.animate_y(2, duration=0.3, curve=curve.out_sine)
        invoke(setattr, player, 'y', 0.3, delay=0.6)

    if random.random() < 0.02:
        lane = random.choice(lanes)
        obstacles.append(Entity(model=random.choice(['rock-sl-1', 'rock-sl-2', 'rock']), texture=random.choice(['rock_diffuse.png', 'rock_roughness.png', 'rock_specular.png']), scale=(0.07, 0.07, 0.07), position=(lane, 0, 20),
                         rotation=(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360))))

    if random.random() < 0.02:
        lane = random.choice(lanes)
        obstacles.append(Entity(model='Tree_Spooky2_Low', texture=random.choice(['tree1.jpg', 'tree2.jpg', 'tree3.jpg']), scale=(0.02, 0.02, 0.02), position=(lane, 0, 20)))

    for obs in obstacles[:]:
        obs.z -= time.dt * speed

        if abs(obs.z - player.z) < 0.2 and abs(obs.x - player.x) < 0.2 and abs(obs.y - player.y) < 0.2:
            lives -= 1
            lives_text.text = f'Lives: {lives}'
            lives_text.visible = True
            obstacles.remove(obs)
            destroy(obs)
            if lives <= 0:
                print("Game Over")
                application.quit()

        if abs(obs.z - player.z) < 1 and abs(obs.x - player.x) < 1 and abs(obs.y - player.y) < 1:
            lives -= 1
            lives_text.text = f'Lives: {lives}'
            lives_text.visible = True
            obstacles.remove(obs)
            destroy(obs)
            if lives <= 0:
                print("Game Over")
                application.quit()

        elif obs.z < -10:
            obstacles.remove(obs)
            destroy(obs)

class WindParticle(Entity):
    def __init__(self, position, direction, lifetime=2):
        super().__init__(
            model='plane',
            scale=random.uniform(0.3, 0.7),
            color=color.white,
            position=position,
            texture='white_cube',
            alpha=0.7
        )
        self.direction = direction
        self.lifetime = lifetime

    def update(self):
        self.position += self.direction * time.dt
        self.lifetime -= time.dt
        if self.lifetime <= 0:
            destroy(self)

def spawn_wind_particle():
    global current_lane
    wind_direction = random.choice([-1, 1])
    new_lane = current_lane + wind_direction
    if new_lane < 0:
        new_lane = 0
    elif new_lane > 2:
        new_lane = 2

    current_lane = new_lane
    player.x = lanes[current_lane]

    wind_direction = random.choice([Vec3(-1, 0, 0), Vec3(1, 0, 0)])
    num_particles = random.randint(5, 10)
    for _ in range(num_particles):
        offset = Vec3(random.uniform(-1, 1), random.uniform(1, 2), random.uniform(0, 1))
        WindParticle(position=player.position + offset, direction=wind_direction, lifetime=2)

    invoke(spawn_wind_particle, delay=3)

spawn_wind_particle()

river = River(start_pos=Vec3(0, 0, 0), width=15, particle_count=300, spawn_rate=10)

sky = Sky()
sun = DirectionalLight(shadows=True)
sun.look_at(Vec3(-0.5, -1, -0.5))

camera.position = (0, 5, -20)
camera.rotation_x = 10

app.run()

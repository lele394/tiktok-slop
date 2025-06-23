import pygame
import math
import random
import sys

import config as cfg

pygame.init()
WIDTH, HEIGHT = 1080, 1920

# Scaling shit
WIDTH = WIDTH//2
HEIGHT = HEIGHT//2

CENTER = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

GRAVITY = pygame.Vector2(0, 0.2)


sound_logs = open("sound_logs.txt", "a")


# Shitty bloom effect
def apply_bloom(screen, threshold=180, blur_radius=8):
    # 1. Extract bright areas
    bright = pygame.Surface(screen.get_size()).convert()
    bright.fill((0, 0, 0))
    
    arr = pygame.surfarray.pixels3d(screen)
    bright_arr = pygame.surfarray.pixels3d(bright)

    # Apply threshold
    bright_arr[:] = [[px if px[0] > threshold or px[1] > threshold or px[2] > threshold else (0,0,0)
                      for px in row] for row in arr]

    del arr
    del bright_arr

    # 2. Blur
    for _ in range(blur_radius):
        bright = pygame.transform.smoothscale(bright, (screen.get_width() // 2, screen.get_height() // 2))
        bright = pygame.transform.smoothscale(bright, screen.get_size())

    # 3. Add to original
    screen.blit(bright, (0, 0), special_flags=pygame.BLEND_ADD)


class Ball:
    def __init__(self, radius, position, name="ball", color=None, image_path=None):
        self.radius = radius
        self.color = color
        self.name = name
        self.image_path = image_path
        self.image = pygame.image.load(image_path).convert_alpha() if image_path else None
        if self.image:
            self.image = pygame.transform.smoothscale(self.image, (radius * 2, radius * 2))
        self.pos = position
        self.vel = pygame.Vector2(0, 4.0)
        self.starting_pos = position

        # Score stuff?
        self.broken_walls = 0.0
        self.bounce = 0.0
        self.score = 0.0


    def get_expected_speed_from_height(self):
        g = GRAVITY.y  # assumes downward gravity
        h0 = self.starting_pos.y
        h = self.pos.y
        if h < h0:
            return 0.0  # can't gain energy going up in this simple model
        return math.sqrt(2 * g * (h - h0))

    def update(self):
        self.vel += GRAVITY
        self.pos += self.vel
        self.score += self.vel.magnitude()

    def draw(self, surface):
        if self.image:
            rect = self.image.get_rect(center=self.pos)
            surface.blit(self.image, rect)
        else:
            pygame.draw.circle(surface, self.color, self.pos, self.radius)

class CircleWall:
    def __init__(self, radius, thickness, hole_angle_deg, hole_size_deg, color, rotation_speed_deg):
        self.radius = radius
        self.thickness = thickness
        self.hole_angle = math.radians(hole_angle_deg)
        self.hole_size = math.radians(hole_size_deg)
        self.color = color
        self.rotation_speed = math.radians(rotation_speed_deg)
        self.rotation = 0  # in radians
        self.to_delete = False

    def update(self):
        self.rotation += self.rotation_speed
        self.rotation %= 2 * math.pi

    def draw(self, surface):
        n_segments = 100
        step = 2 * math.pi / n_segments
        for i in range(n_segments):
            angle1 = i * step
            angle2 = (i + 1) * step
            # Skip the hole
            a = (angle1 - self.rotation) % (2 * math.pi)
            if self.hole_angle <= a <= self.hole_angle + self.hole_size:
                continue
            inner1 = CENTER + pygame.Vector2(math.cos(angle1), math.sin(angle1)) * (self.radius - self.thickness / 2)
            outer1 = CENTER + pygame.Vector2(math.cos(angle1), math.sin(angle1)) * (self.radius + self.thickness / 2)
            inner2 = CENTER + pygame.Vector2(math.cos(angle2), math.sin(angle2)) * (self.radius - self.thickness / 2)
            outer2 = CENTER + pygame.Vector2(math.cos(angle2), math.sin(angle2)) * (self.radius + self.thickness / 2)
            pygame.draw.polygon(surface, self.color, [inner1, outer1, outer2, inner2])

    def handle_collision(self, ball):
        offset = ball.pos - CENTER
        dist = offset.length()

        # Check if within collision shell (including ball's radius)
        if not (self.radius - self.thickness / 2 - ball.radius <= dist <= self.radius + self.thickness / 2 + ball.radius):
            return  # no collision

        # Check if within hole
        angle = math.atan2(offset.y, offset.x)
        rel_angle = (angle - self.rotation) % (2 * math.pi)
        start = self.hole_angle % (2 * math.pi)
        end = (self.hole_angle + self.hole_size) % (2 * math.pi)

        in_hole = (start <= rel_angle <= end) if start < end else (rel_angle >= start or rel_angle <= end)
        if in_hole:
            self.to_delete = True
            ball.broken_walls += 1
            sound_logs.write(f"wall_break\t{frame_number}\n")
            
            ball.radius += 4 # Increase ball radius when breaking wall?
            if ball.image: # adapt image to size increase
                ball.image = pygame.image.load(ball.image_path).convert_alpha() if ball.image_path else None
                ball.image = pygame.transform.smoothscale(ball.image, (ball.radius * 2, ball.radius * 2))

            return

        # Reflect the ball with a bit of randomness
        normal = (ball.pos - CENTER).normalize()
        vel_normal = ball.vel.dot(normal)
        reflected = ball.vel - 2 * vel_normal * normal  # perfect reflection

        # Add random angle to the reflected vector
        angle_variation = math.radians(random.uniform(-30, 30))  # up to ±10 degrees
        reflected = reflected.rotate_rad(angle_variation)

        ball.vel = reflected


        # Push back inside the circle
        target_dist = self.radius + self.thickness / 2 + ball.radius if vel_normal < 0 else self.radius - self.thickness / 2 - ball.radius
        ball.pos = CENTER + normal * target_dist

        desired_speed = ball.get_expected_speed_from_height() + (random.random()*4+4)
        ball.vel = ball.vel.normalize() * desired_speed
        ball.bounce += 1
        sound_logs.write(f"bounce\t{frame_number}\n")



# Initialize balls
# Initialize balls
# balls = [
#     Ball(
#         name="you",
#         radius=8,
#         color=(255, 100, 100),
#         position=pygame.Vector2(
#             WIDTH//2 + random.uniform(0, 95),
#             HEIGHT//2# OFFSET TO GET SOME MOMENTUM + random.uniform(-30, 30)
#         )
#     ),
#     Ball(
#         name="opponent",
#         radius=8,
#         color=(100, 200, 255),
#         position=pygame.Vector2(
#             WIDTH//2 + random.uniform(-95, 0),
#             HEIGHT//2# OFFSET TO GET SOME MOMENTUM + random.uniform(-100, 100)
#         )
#     )
# ]



balls = []

for item in cfg.BALLS:

    ball = Ball(
        name=item["name"],
        radius=item["radius"],
        color=item["color"],
        image_path=item["image_path"],
        position=pygame.Vector2(
            WIDTH//2 + random.uniform(-95, 95),
            HEIGHT//2# OFFSET TO GET SOME MOMENTUM + random.uniform(-30, 30)
        )
    )

    balls.append(ball)



# Initialize walls
walls = []

def spawn_random_wall():
    pass_gap = 10  # minimum radius gap between consecutive walls
    if not walls:
        # First wall radius
        radius = 100
    else:
        radius = int(walls[-1].radius + pass_gap)

    wall = CircleWall(
        radius=radius,
        thickness=5,
        hole_angle_deg=random.randint(0, 330),
        hole_size_deg=30, # random.randint(60, 100),
        color=[random.randint(100, 255) for _ in range(3)],
        rotation_speed_deg=random.choice([-2, -1, 1, 2])
    )
    walls.append(wall)


def spawn_wall_1():
    pass_gap = 10  # minimum radius gap between consecutive walls
    if not walls:
        # First wall radius
        radius = 100
    else:
        radius = int(walls[-1].radius + pass_gap)

    wall = CircleWall(
        radius=radius,
        thickness=5,
        hole_angle_deg=0,
        hole_size_deg=30, # random.randint(60, 100),
        color=[random.randint(100, 255) for _ in range(3)],
        rotation_speed_deg = (radius**0.8)/50
    )
    walls.append(wall)

def spawn_wall_2():
    pass_gap = 10  # minimum radius gap between consecutive walls
    if not walls:
        # First wall radius
        radius = 100
        flip = 1 # don't fleep speed on first
    else:
        radius = int(walls[-1].radius + pass_gap)
        flip = 1 if walls[-1].rotation_speed < 0 else -1

    wall = CircleWall(
        radius=radius,
        thickness=5,
        hole_angle_deg=0,
        hole_size_deg=30, # random.randint(60, 100),
        color=[random.randint(100, 255) for _ in range(3)],
        rotation_speed_deg = (radius**0.8)/50 * flip
    )
    walls.append(wall)


def spawn_wall_2_cst():
    pass_gap = 10  # minimum radius gap between consecutive walls
    if not walls:
        # First wall radius
        radius = 100
        flip = 1 # don't fleep speed on first
    else:
        radius = int(walls[-1].radius + pass_gap)
        flip = 1 if walls[-1].rotation_speed < 0 else -1

    wall = CircleWall(
        radius=radius,
        thickness=5,
        hole_angle_deg=0,
        hole_size_deg=30, # random.randint(60, 100),
        color=[random.randint(100, 255) for _ in range(3)],
        rotation_speed_deg = 2 * flip
    )
    walls.append(wall)


# Spawn initial walls
for _ in range(cfg.N_WALLS):
    # spawn_random_wall()
    # spawn_wall_1()
    # spawn_wall_2()
    spawn_wall_2_cst()






frame_number = 0
Is_Done = False
# Game loop
running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update balls
    for ball in balls:
        ball.update()

    # Update walls
    for wall in walls:
        wall.update()
        for ball in balls:
            wall.handle_collision(ball)

    # Remove walls that have been passed
    walls = [w for w in walls if not w.to_delete]

    if len(walls) == 0 and not(Is_Done):
        Is_Done = True
        counter = 120 # 120 more frames then kill it.

        sound_logs.write(f"win\t{frame_number}\n")

        
        winner = None
        win_score = 0
        for ball in balls:
            score = score = int(ball.bounce * 100 + 10000 * ball.broken_walls + ball.score/20)
            if score >= win_score:
                winner = ball
                win_score = score



    # Draw walls
    for wall in walls:
        wall.draw(screen)

    # Draw balls
    for ball in balls:
        ball.draw(screen)


    font = pygame.font.SysFont("comicneue", 50, bold=True)  # Initialize once


    text_surface = font.render(cfg.TITLE, True, ball.color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, 60))
    screen.blit(text_surface, text_rect)


    if Is_Done:
        text_surface = font.render(f"Winner : {winner.name}", True, winner.color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT//2))
        screen.blit(text_surface, text_rect)

        text_surface = font.render(f"{win_score}", True, winner.color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT//2+40))
        screen.blit(text_surface, text_rect)

        # last frame counter decrease and togle :
        counter -= 1
        if counter<0:
            running = False




    else:
        y_offset = 110
        for ball in balls:
            score = int(ball.bounce * 100 + 10000 * ball.broken_walls + ball.score/20)
            status_text = f'{ball.name} : {score}'
            
            # Render text using the ball's color
            text_surface = font.render(status_text, True, ball.color)
            
            # Center the text horizontally
            text_rect = text_surface.get_rect(center=(WIDTH // 2, y_offset))
            
            screen.blit(text_surface, text_rect)
            y_offset += 60  # line spacing


    text_surface = font.render("Subscribe to choose", True, ball.color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT-180))
    screen.blit(text_surface, text_rect)

    text_surface = font.render("the next fight", True, ball.color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT-120))
    screen.blit(text_surface, text_rect)



    # Laggy as SHIT
    # apply_bloom(screen)
    pygame.display.flip()
    pygame.image.save(screen, f"frames/frame_{frame_number:05d}.png")
    frame_number += 1
    # clock.tick(60)

pygame.quit()
sys.exit()


# f'{ball.name} : {ball.bounce} bounce & {ball.broken_walls} points'
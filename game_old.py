import pygame
import neat
import numpy as np

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_w,
    K_a,
    K_s,
    K_d,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    MOUSEBUTTONUP
)

COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (0, 0, 0)]
SCREEN_SIZE = 400
NUM_H = 0
GAME_LENGTH = 5_000
# HIT_BONUS = 0.1
FRAMERATE = 60

N_LIVES = 5
RELOAD_RATE = 30
BULLET_SPEED = 5
TANK_SPEED = 1


def closest(this, sprites):
    min_dist = float("inf")
    closest_pt = (0, 0)
    vector = (0, 0)
    this_pt = this.rect.center
    for sprite in sprites:
        point = sprite.rect.center
        dist = np.sqrt((this_pt[0]-point[0])**2 + (this_pt[1]-point[1])**2)
        if dist < min_dist and this.id != sprite.id:
            closest_pt = point
            min_dist = dist
            vector = sprite.vector
    return list(closest_pt) + list(vector)

def magnitude(vector):
    return np.sqrt(vector[0] ** 2 + vector[1] ** 2)

def make_tanks(models, genomes):
    # n_h_tanks = int(input("Enter # of human tanks (0 - 2):"))
    # n_bots = int(input("Enter # of bot tanks:"))

    # assert len(models) == NUM_B
    all, h, b = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    i = 0
    while i < NUM_H:
        tank = Tank(COLORS[i % len(COLORS)], i)
        all.add(tank)
        h.add(tank)
        i += 1

    while i < NUM_H + len(genomes):
        tank = AI_Tank(COLORS[i % len(COLORS)], i, models[i-NUM_H], genomes[i-NUM_H][1])
        all.add(tank)
        b.add(tank)
        i += 1

    return {tank.id: tank for tank in all}, h, b, all

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, vector, id):
        super(Bullet, self).__init__()

        self.surf = pygame.Surface((3, 3))
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect()
        self.rect.x, self.rect.y = pos
        self.owner = id
        self.id = id

        mag = magnitude(vector)
        if mag == 0:
            self.vector = vector
        else:
            self.vector = np.multiply(vector, BULLET_SPEED / mag)
    def move(self):
        self.rect.move_ip(*self.vector)
    def collides_with_wall(self):
        return self.rect.left < 0 or self.rect.right > SCREEN_SIZE or self.rect.top < 0 or self.rect.bottom > SCREEN_SIZE

class Tank(pygame.sprite.Sprite):
    def __init__(self, color, index):
        super(Tank, self).__init__()

        self.surf = pygame.Surface((25, 25))
        self.surf.fill(color)
        self.rect = self.surf.get_rect()
        self.rect.x, self.rect.y = rand_pos()

        self.vector = (0, 0)

        self.reloaded = 0
        self.lives = N_LIVES
        self.id = index
    def move(self, *vector):
        mag = magnitude(vector)
        if mag == 0:
            norm_vector = vector
        else:
            norm_vector = np.multiply(vector, TANK_SPEED / mag)

        self.vector = norm_vector



        self.rect.move_ip(*np.round(self.vector))
        # assert a[0] != self.rect[0] or a[1] != self.rect[1]
    def keyboard_move(self, presses):

        if presses[K_w]:
            self.move(0, -1)
        if presses[K_s]:
            self.move(0, 1)
        if presses[K_a]:
            self.move(-1, 0)
        if presses[K_d]:
            self.move(1, 0)

    def reload(self):
        if self.reloaded > 0:
            self.reloaded -= 1
    def fire_bullet(self, mouse_pos):
        if self.reloaded > 0:
            return
        self.reloaded = RELOAD_RATE
        return Bullet(self.rect.center, np.subtract(mouse_pos, self.rect.center), self.id)

    def hurt(self, tanks_all):
        if self.lives == 1:
            self.kill()
        self.lives -= 1

class AI_Tank(Tank):
    def __init__(self, color, index, model, genome):
        super(AI_Tank, self).__init__(color, index)
        self.model = model
        self.genome = genome

    def eval(self, tanks_all, bullets):
        closest_tank, closest_bullet = closest(self, tanks_all), closest(self, bullets)
        inputs = np.concatenate((self.rect.center, np.subtract(closest_tank[:2], self.rect.center), closest_tank[2:], np.subtract(closest_bullet[:2], self.rect.center), closest_bullet[2:]))

        guess = self.model.activate(inputs)
        # guess = [1, 1, 1, 1]
        tank_vector, bullet_vector = guess[:2], guess[2:] # both should have magnitude 1

        return tank_vector, bullet_vector

    def act(self, tanks_all, bullets):
        tank_vector, bullet_vector = self.eval(tanks_all, bullets)

        self.move(*tank_vector)
        return self.fire_bullet(bullet_vector)

    def fire_bullet(self, bullet_vector):
        if self.reloaded > 0:
            return

        self.reloaded = RELOAD_RATE

        return Bullet(self.rect.center, bullet_vector, self.id)

    def hurt(self, tanks_all):
        if self.lives == 1:
            self.genome.fitness = -len(tanks_all)
        super(AI_Tank, self).hurt(tanks_all)


def rand_pos():
    return np.random.randint(SCREEN_SIZE, size=2)
def border_pass(sprite):
    out = False
    if sprite.rect.x < 0:
        out = True
        sprite.rect.move_ip(SCREEN_SIZE, 0)
    elif sprite.rect.x > SCREEN_SIZE:
        out = True
        sprite.rect.move_ip(-SCREEN_SIZE, 0)
    if sprite.rect.y < 0:
        out = True
        sprite.rect.move_ip(0, SCREEN_SIZE)
    elif sprite.rect.y > SCREEN_SIZE:
        out = True
        sprite.rect.move_ip(0, -SCREEN_SIZE)
    if out and type(sprite) == Bullet:
        sprite.kill()

def play(genomes, config):
    models = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        models.append(neat.nn.FeedForwardNetwork.create(genome, config))

    tank_id_map, tanks_h, tanks_b, tanks_all = make_tanks(models, genomes)

    bullets = pygame.sprite.Group()

    pygame.init()

    screen = pygame.display.set_mode([SCREEN_SIZE, SCREEN_SIZE])
    screen.fill((255, 255, 255))

    for tank in tanks_all:
        screen.blit(tank.surf, tank.rect)

    pygame.display.flip()

    clock = pygame.time.Clock()
    running = True
    game_length = 0 # 1300 = shortest game
    while len(tanks_all) > 1 and game_length < GAME_LENGTH:

        for event in pygame.event.get():
            screen.fill((255, 255, 255))
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

            elif event.type == QUIT:
                running = False

            # fire bullet from human tank 1
            elif event.type == MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                if len(tanks_h) > 0:
                    bullet = list(tanks_h)[0].fire_bullet(mouse_pos)
                    if bullet:
                        bullets.add(bullet)


        screen.fill((255, 255, 255))

        presses = pygame.key.get_pressed()
        # draw + move tanks
        for tank in tanks_all:
            border_pass(tank)
            if type(tank) == Tank:
                tank.keyboard_move(presses)
                tank.reload()
            elif type(tank) == AI_Tank:
                bullet = tank.act(tanks_all, bullets)
                if bullet:
                    bullets.add(bullet)
                tank.reload()
            for bullet in bullets:
                if pygame.sprite.collide_rect(tank, bullet) and tank.id != bullet.owner:
                    bullet.kill()
                    tank.hurt(tanks_all)
                    tank_id_map[bullet.owner].lives += 1
                    # tank_id_map[bullet.owner].genome.fitness += HIT_BONUS
            screen.blit(tank.surf, tank.rect)

        for bullet in bullets:
            bullet.move()
            # border_pass(bullet)

            screen.blit(bullet.surf, bullet.rect)
        pygame.display.flip()



        screen.fill((255,255,255))
        # clock.tick(FRAMERATE)
        game_length += 1
        if game_length % 1000 == 0:
            print(game_length)

    if len(tanks_all) > 1: # if took too long
        max_lives = 0
        id = -1
        for tank in tanks_all:
            if tank.lives > max_lives:
                id = tank.id
                max_lives = tank.lives
        winner = tank_id_map[id]
    else:
        winner = tank_id_map[0]
    return winner.id, winner.lives, game_length

def run_neat(config_file):
    """
    runs the NEAT algorithm to train a neural network to play the tank game
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 20 generations.
    winner = p.run(play, 20)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))
# inputs:
#   current position (x, y)
#   relative pos of closest tank (x, y), (dx, dy)
#   relative pos of closest bullet (x, y), (dx, dy)
# outputs:
#   desired tank vector (dx, dy)
#   desired bullet vector (dx, dy)

# print(play([], None))

run_neat('config-feedforward.txt')











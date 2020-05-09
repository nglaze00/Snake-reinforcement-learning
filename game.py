"""
Code for running Snake using PyGame
"""
import pygame
import numpy as np
from pygame.locals import (
    K_w,
    K_a,
    K_s,
    K_d,
    KEYDOWN,
    QUIT,
    K_ESCAPE
)
# screen
SCREEN_SIZE = 500
BLOCK_SIZE = 25
GRID_SIZE = SCREEN_SIZE // BLOCK_SIZE


# attempt settings
START_GEN = 190
WATCH = True

# framerate
FRAMERATE = 20
USE_FRAMERATE = WATCH



VISION_BOX = 9

class Food():
    def __init__(self, pos):
        self.pos = tuple(pos)
    def draw(self, screen):
        border = 5
        real_pos = np.multiply(self.pos, BLOCK_SIZE)
        pygame.draw.rect(screen, (150, 0, 0), (*real_pos, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(screen, (255, 0, 0),
                         (real_pos[0] + border, real_pos[1] + border, BLOCK_SIZE - 2 * border, BLOCK_SIZE - 2 * border))
    def respawn(self):
        self.pos = tuple(rand_pos())


class Snake():
    def __init__(self, pos):
        self.dir = self.right
        self.blocks = [tuple(pos)]
        self.pos_history = [tuple(pos)] + [None] * 20

    def draw(self, screen):
        border = 5
        for pos in self.blocks:
            real_pos = np.multiply(pos, BLOCK_SIZE)
            pygame.draw.rect(screen, (0, 150, 0), (*real_pos, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, (0, 255, 0), (real_pos[0] + border, real_pos[1] + border, BLOCK_SIZE - 2 * border, BLOCK_SIZE - 2 * border))

    def move(self):

        new = self.dir(self.blocks[0])

        # validate move
        if not 0 <= new[0] < GRID_SIZE or not 0 <= new[1] < GRID_SIZE:
            if WATCH:
                print('out map')
            return False
        if new in self.blocks:
            if WATCH:
                print('hit snake')
            return False

        self.blocks.insert(0, new)
        self.blocks.pop()

        # kill if single block moves back and forth
        if new in self.pos_history[10:] and new in self.pos_history[:10]:
            if WATCH:
                print('cycle')
            return False
        self.pos_history.pop()
        self.pos_history.insert(0, new)

        return True

    def left(self, head):
        return (head[0] - 1, head[1])
    def right(self, head):
        return (head[0] + 1, head[1])
    def up(self, head):
        return (head[0], head[1] - 1)
    def down(self, head):
        return (head[0], head[1] + 1)

# def Food(pygame.sprite.Sprite):

def rand_pos():
    return np.random.randint(0, GRID_SIZE, size=2)

def human_mover(state, snake):
    presses = pygame.key.get_pressed()
    if presses[K_w]:
        snake.dir = snake.up
    elif presses[K_s]:
        snake.dir = snake.down
    elif presses[K_a]:
        snake.dir = snake.left
    elif presses[K_d]:
        snake.dir = snake.right

def complete_state(snake, food):
    state = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    # snake head = 2
    state[snake.blocks[0]] = 2
    # other snake blocks = 1
    for block in snake.blocks[1:]:
        state[block] = 1
    state[food.pos] = 3

    return state.flatten()

def eval_point(pos, snake, food):
    if pos in snake.blocks: # snake tail
        return 1
    if not 0 <= pos[0] < GRID_SIZE or not 0 <= pos[1] < GRID_SIZE: # border
        return 1
    if pos == food.pos: # food
        return 3
    else:                # blank
        return 0

def local_state(snake, food):
    state = []
    head = snake.blocks[0]

    # local state (5x5 grid around snake)
    for i in range(-VISION_BOX // 2 + 1, VISION_BOX // 2 + 1):
        for j in range(-VISION_BOX // 2 + 1, VISION_BOX // 2 + 1):
            if i != 0 or j != 0:

                state.append(eval_point((head[0] + j, head[1] + i), snake, food))

    # relative location of food
    food_relative = (food.pos[0] - head[0], food.pos[1] - head[1])
    state += [*food_relative]
    # print(np.reshape(state[:-2] + [-1], (VISION_BOX, VISION_BOX)))
    return state

def play(mover):
    """
    :param mover: function that, given current state, returns the direction to move the snake
    :return: score (# of foods eaten)
    """
    global USE_FRAMERATE
    global SHOW
    use_framerate = USE_FRAMERATE
    show = WATCH
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_SIZE, SCREEN_SIZE])
    clock = pygame.time.Clock()

    snake = Snake(rand_pos())
    food = Food(rand_pos())
    score = 0

    search_length = 0


    done = False
    while not done:
        # if search_length > 100:
        #     show = True
        #     use_framerate = True
        if search_length > 200:
            if WATCH:
                print('timeout')
            return score
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = True
            elif event.type == QUIT:
                done = True
        if show:
            screen.fill((0, 0, 0))
            snake.draw(screen)
            food.draw(screen)
            pygame.display.flip()


        # build game state
        # state = complete_state(snake, food)
        state = local_state(snake, food)

        # move snake
        mover(state, snake)

        if not snake.move():
            return score

        # check if ate food

        if snake.blocks[0] == food.pos:

            search_length = 0
            score += 1
            food.respawn()
            snake.blocks.append(snake.blocks[0])

        if use_framerate:
            clock.tick(FRAMERATE)
        search_length += 1
    return score
if __name__ == '__main__':
    play(human_mover)
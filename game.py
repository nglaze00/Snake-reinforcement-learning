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
START_GEN = 0
WATCH = False


# framerate
FRAMERATE = 20
USE_FRAMERATE = False

SHOW_DEATH_CAUSE = False



VISION_BOX = 5

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

        self.turn_directions = {
            self.left: [self.down, self.left, self.up],
            self.down: [self.right, self.down, self.left],
            self.right: [self.up, self.right, self.down],
            self.up: [self.left, self.up, self.right]
        }

    def draw(self, screen):
        border = 5
        for pos in self.blocks:
            real_pos = np.multiply(pos, BLOCK_SIZE)
            pygame.draw.rect(screen, (0, 150, 0), (*real_pos, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, (0, 255, 0), (real_pos[0] + border, real_pos[1] + border, BLOCK_SIZE - 2 * border, BLOCK_SIZE - 2 * border))

    def move(self):
        new = self.dir(self.blocks[0])
        self.blocks.insert(0, new)
        self.blocks.pop()

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

    # four booleans: is food up, down, left, or right?
    food_direction = (
            1 if food.pos[1] < head[1] else 0,
            1 if food.pos[1] > head[1] else 0,
            1 if food.pos[0] < head[0] else 0,
            1 if food.pos[0] > head[0] else 0
    )
    state += [*food_direction]
    # print(np.reshape(state[:-2] + [-1], (VISION_BOX, VISION_BOX)))
    return state

def local_plus_directional_state(snake, food):
    return np.concatenate((local_state(snake, food), directional_state(snake, food)))

def dir_to_point(source, other):
    """
    Determine whether the other point is in one of the 8 cardinal / intercardinal directions from the source
    directions numbered 1-8, clockwise from north

    return relative direction and distance along the direction, or (0, None) if not in cardinal direction
    """
    # diagonal

    s, o = np.asarray(source), np.asarray(other)

    rel_pos = o - s
    if rel_pos[0] == rel_pos[1]:
        if rel_pos[0] > 0:
            return (4, rel_pos[0])
        else:
            return (8, -rel_pos[0])

    elif rel_pos[0] == -rel_pos[1]:
        if rel_pos[0] > 0:
            return (3, rel_pos[0])
        else:
            return (6, rel_pos[1])

    elif rel_pos[0] == 0:
        if rel_pos[1] > 0:
            return (5, rel_pos[1])
        else:
            return (1, -rel_pos[1])
    elif rel_pos[1] == 0:
        if rel_pos[0] > 0:
            return (3, rel_pos[0])
        else:
            return (7, -rel_pos[0])

    return (0, None)



def directional_state(snake, food):
    """
    18 inputs; return distance to border and snake body in each of the 8 directions, along with relative position of food
    """

    head = snake.blocks[0]
    rel_food_pos = (np.asarray(food.pos, dtype=float) - np.asarray(head, dtype=float))

    for i in range(2):
        if rel_food_pos[i] == 0:
            rel_food_pos[i] = 1
        elif rel_food_pos[i] > 0:
            rel_food_pos[i] = 1.0 / (rel_food_pos[i] + 1)
        else:
            rel_food_pos[i] = 1.0 / (rel_food_pos[i] - 1)


    state = {
             'food':   rel_food_pos,
             'border': [0, 0, 0, 0, 0, 0, 0, 0],
             'body':   [0, 0, 0, 0, 0, 0, 0, 0]
             }


    # look for snake blocks
    for block in snake.blocks[1:]:
        dir, dist = dir_to_point(head, block)
        if dir != 0:
            state['body'][dir - 1] = np.divide(1, dist)

    # border distances
    state['border'][0] = head[1]
    state['border'][1] = min((GRID_SIZE - head[0], head[1]))
    state['border'][2] = GRID_SIZE - head[0]
    state['border'][3] = min((GRID_SIZE - head[0], GRID_SIZE - head[1]))
    state['border'][4] = GRID_SIZE - head[1]
    state['border'][5] = min((head[0], GRID_SIZE - head[1]))
    state['border'][6] = head[0]
    state['border'][7] = min(head)







    return np.concatenate((state['food'], [1 / (b + 1) for b in state['border']], state['body']))


def play(choose_dir):
    """
    :param mover: function that, given current state, returns the direction to move the snake
    :return: score (# of foods eaten)
    """


    pygame.init()
    screen = pygame.display.set_mode([SCREEN_SIZE, SCREEN_SIZE])
    clock = pygame.time.Clock()

    snake = Snake(rand_pos())
    food = Food(rand_pos())
    score = 0

    search_length = 0


    done = False
    while not done:

        if search_length > 100:
            if SHOW_DEATH_CAUSE:
                print('timeout')
            return score
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = True
            elif event.type == QUIT:
                done = True
        if WATCH:
            screen.fill((0, 0, 0))
            snake.draw(screen)
            food.draw(screen)
            pygame.display.flip()

        # check if snake in map
        if not 0 <= snake.blocks[0][0] < GRID_SIZE or not 0 <= snake.blocks[0][1] < GRID_SIZE:
            if SHOW_DEATH_CAUSE:
                print('out map')
            return score

        # build game state
        # state = complete_state(snake, food)
        state = local_state(snake, food)
        # state = local_state(snake, food)

        # move snake
        choose_dir(state, snake)

        # check if snake hit itself
        if snake.blocks[0] in snake.blocks[1:]:
            if SHOW_DEATH_CAUSE:
                print('hit snake')
            return score

        # check if ate food
        if snake.blocks[0] == food.pos:
            search_length = 0
            score += 1
            food.respawn()
            snake.blocks.append(snake.blocks[0])

        snake.move()





        if USE_FRAMERATE:
            clock.tick(FRAMERATE)
        search_length += 1
    return score

if __name__ == '__main__':
    play(human_mover)
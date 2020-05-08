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
GRID_SIZE = SCREEN_SIZE / BLOCK_SIZE



# framerate
FRAMERATE = 10
USE_FRAMERATE = True

class Food():
    def __init__(self, pos):
        self.pos = tuple(np.multiply(pos, BLOCK_SIZE))
    def draw(self, screen):
        border = 5
        pygame.draw.rect(screen, (150, 0, 0), (*self.pos, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(screen, (255, 0, 0),
                         (self.pos[0] + border, self.pos[1] + border, BLOCK_SIZE - 2 * border, BLOCK_SIZE - 2 * border))
    def respawn(self):
        self.pos = tuple(np.multiply(rand_pos(), BLOCK_SIZE))


class Snake():
    def __init__(self, pos):
        self.dir = self.right
        self.blocks = [tuple(np.multiply(pos, BLOCK_SIZE))]

    def draw(self, screen):
        border = 5
        for pos in self.blocks:
            pygame.draw.rect(screen, (0, 150, 0), (*pos, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, (0, 255, 0), (pos[0] + border, pos[1] + border, BLOCK_SIZE - 2 * border, BLOCK_SIZE - 2 * border))

    def move(self):

        new = self.dir(self.blocks[0])
        # validate move
        if not 0 <= new[0] < SCREEN_SIZE or not 0 <= new[1] < SCREEN_SIZE:
            return False
        if new in self.blocks:
            return False

        self.blocks.insert(0, new)
        self.blocks.pop()
        return True

    def left(self, head):
        return (head[0] - BLOCK_SIZE, head[1])
    def right(self, head):
        return (head[0] + BLOCK_SIZE, head[1])
    def up(self, head):
        return (head[0], head[1] - BLOCK_SIZE)
    def down(self, head):
        return (head[0], head[1] + BLOCK_SIZE)

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


def play(mover):
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


    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == QUIT:
                running = False

        screen.fill((0, 0, 0))
        snake.draw(screen)
        food.draw(screen)
        pygame.display.flip()


        # build game state
        state = np.zeros((SCREEN_SIZE, SCREEN_SIZE), dtype=int)
        # snake head = 2
        state[snake.blocks[0]] = 2
        # other snake blocks = 1
        for block in snake.blocks[1:]:
            state[block] = 1
        # todo food position = 3

        # move snake
        mover(state, snake)
        if not snake.move():
            return score

        # check if ate food

        if snake.blocks[0] == food.pos:
            score += 1
            food.respawn()
            snake.blocks.append(snake.blocks[0])

        clock.tick(FRAMERATE)

    return score

play(human_mover)
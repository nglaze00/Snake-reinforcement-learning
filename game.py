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

# board
BLOCK_SIZE = 25
GRID_SIZE = 16
SCREEN_SIZE = BLOCK_SIZE * GRID_SIZE

# observation settings
FRAMERATE = 10
USE_FRAMERATE = True
WATCH = True
SHOW_DEATH_CAUSE = False

class Food():
    def __init__(self, pos):
        self.pos = tuple(pos)

    def draw(self, screen):
        """
        Draws the food with a border
        """
        border = 5
        real_pos = np.multiply(self.pos, BLOCK_SIZE)
        pygame.draw.rect(screen, (150, 0, 0), (*real_pos, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(screen, (255, 0, 0),
                         (real_pos[0] + border, real_pos[1] + border, BLOCK_SIZE - 2 * border, BLOCK_SIZE - 2 * border))

    def respawn(self, func):
        """
        Respawn the food in a new place
        """
        new_pos = tuple(func())
        self.pos = new_pos


class Snake():
    def __init__(self, pos):
        self.dir = self.right
        self.blocks = [tuple(pos)]


    def draw(self, screen):
        """
        Draws each block of the snake with a border
        """
        border = 5
        for pos in self.blocks:
            real_pos = np.multiply(pos, BLOCK_SIZE)
            pygame.draw.rect(screen, (0, 150, 0), (*real_pos, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, (0, 255, 0), (real_pos[0] + border, real_pos[1] + border, BLOCK_SIZE - 2 * border, BLOCK_SIZE - 2 * border))

    def move(self):
        """
        Move the snake in direction indicated by self.dir
        """
        new = self.dir(self.blocks[0])
        self.blocks.insert(0, new)
        self.blocks.pop()


    ## Direction functions; move head of snake left, right, up, or down
    def left(self, head):
        return (head[0] - 1, head[1])
    def right(self, head):
        return (head[0] + 1, head[1])
    def up(self, head):
        return (head[0], head[1] - 1)
    def down(self, head):
        return (head[0], head[1] + 1)


def rand_pos():
    """
    Return a random tuple with values between 0 and GRID_SIZE
    """
    return np.random.randint(0, GRID_SIZE, size=2)

def human_mover(snake, food):
    presses = pygame.key.get_pressed()
    if presses[K_w]:
        snake.dir = snake.up
    elif presses[K_s]:
        snake.dir = snake.down
    elif presses[K_a]:
        snake.dir = snake.left
    elif presses[K_d]:
        snake.dir = snake.right

def play(snake_controller, food_controller):
    """
    Plays Snake using given
    :param snake_controller: function that, given current state, returns the direction to move the snake
    :param food controller: function that returns the next food position when called.
    :return: score (# of foods eaten)
    """
    # PyGame setup
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_SIZE, SCREEN_SIZE])
    clock = pygame.time.Clock()

    # Game objects setup
    snake = Snake(rand_pos())
    food = Food(rand_pos())


    score = 0
    search_length = 0

    done = False
    while not done:
        # Quit if escape / X pressed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    done = True
            elif event.type == QUIT:
                done = True

        # Draw board if user wants to watch
        if WATCH:
            screen.fill((0, 0, 0))
            snake.draw(screen)
            food.draw(screen)
            pygame.display.flip()

        # Quit if snake takes too long to find the food
        if search_length > 100:
            if SHOW_DEATH_CAUSE:
                print('timeout')
            break

        # quit if snake hits border
        if not 0 <= snake.blocks[0][0] < GRID_SIZE or not 0 <= snake.blocks[0][1] < GRID_SIZE:
            if SHOW_DEATH_CAUSE:
                print('out map')
            break

        # move snake
        snake_controller(snake, food)

        # check if snake hit itself
        if snake.blocks[0] in snake.blocks[1:]:
            if SHOW_DEATH_CAUSE:
                print('hit snake')
            break

        # check if snake ate food
        if snake.blocks[0] == food.pos:
            search_length = 0
            score += 1
            food.respawn(food_controller)
            while food.pos in snake.blocks:
                food.respawn(food_controller)
            snake.blocks.append(snake.blocks[0])

        # Move snake
        snake.move()

        if USE_FRAMERATE:
            clock.tick(FRAMERATE)

        search_length += 1

    return score

if __name__ == '__main__':
    FRAMERATE = 10
    while True:
        print("Score: {}".format(play(human_mover, rand_pos)))
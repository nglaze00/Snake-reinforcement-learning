"""
Code for training a Snake bot using NEAT



"""
import pickle
import neat
import numpy as np
from game import play
import game

# how many plays to average together in each fitness calculation
PLAYS_PER_BOT = 3
# how far to allow the bot to see
VISION_BOX = 5



def bot_mover_maker(model):
    """
    Returns a function that, when called, uses the given model to suggest a direction for the snake to move, given
    the current state
    :param model: neat.nn.FeedForwardNetwork object
    :return: function with args (state, snake)
    """
    def bot_mover(snake, food):
        state = local_state(snake, food)
        guesses = model.activate(state)

        new_dir = np.argmax(guesses)
        if new_dir == 0:
            snake.dir = snake.up
        elif new_dir == 1:
            snake.dir = snake.right
        elif new_dir == 2:
            snake.dir = snake.down
        elif new_dir == 3:
            snake.dir = snake.left

    return bot_mover


def is_occupied(pos, snake):
    """
    Return whether a grid point :pos: is blank (0) or not (1)
    """
    if pos in snake.blocks: # snake tail
        return 1
    if not 0 <= pos[0] < game.GRID_SIZE or not 0 <= pos[1] < game.GRID_SIZE: # border
        return 1
    else:                # blank
        return 0

def local_state(snake, food):
    """
    Returns whether the points in a grid around the snake's head are occupied,
        plus booleans identifying direction to food

    :return: flattened VISION_BOX x VISION_BOX binary matrix
    """
    state = []
    head = snake.blocks[0]

    # local state (5x5 grid around snake)
    for i in range(-VISION_BOX // 2 + 1, VISION_BOX // 2 + 1):
        for j in range(-VISION_BOX // 2 + 1, VISION_BOX // 2 + 1):
            if i != 0 or j != 0:

                state.append(is_occupied((head[0] + j, head[1] + i), snake))

    # four booleans: is food up, down, left, or right?
    food_direction = (
            1 if food.pos[1] < head[1] else 0,
            1 if food.pos[1] > head[1] else 0,
            1 if food.pos[0] < head[0] else 0,
            1 if food.pos[0] > head[0] else 0
    )
    state += [*food_direction]
    return state


def train_generation(genomes, config):
    """
    Computes fitnesses of given genomes
    """
    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        model = neat.nn.FeedForwardNetwork.create(genome, config)
        bot_mover = bot_mover_maker(model)
        for _ in range(PLAYS_PER_BOT):
            genome.fitness += play(bot_mover, game.rand_pos()) / PLAYS_PER_BOT

def run_neat(config_file):
    """
    runs the NEAT algorithm to train a neural network to play Snake
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
    p.add_reporter(neat.Checkpointer(50))

    # Run for up to 1000 generations.
    winner = p.run(train_generation, 1000)

    # save best genome to file
    pickle.dump(winner, open('best_genome', 'wb'))

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    run_neat('config-feedforward.txt')
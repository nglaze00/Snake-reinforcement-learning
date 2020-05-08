"""
Code for training a Snake bot using NEAT

inputs: board state
    0: blank
    1: snake
    2: snake head
    3: food

outputs: direction to move:
    0: up
    1: right
    2: down
    3: left
"""
import neat
import numpy as np
from game import play, GRID_SIZE


def bot_mover_maker(model):
    def bot_mover(state, snake):
        inputs = state.flatten()
        guesses = model.activate(inputs)
        dir = np.argmax(guesses)
        if dir == 0:
            snake.dir = snake.up
        elif dir == 1:
            snake.dir = snake.right
        elif dir == 2:
            snake.dir = snake.down
        elif dir == 3:
            snake.dir = snake.left

    return bot_mover


def train_generation(genomes, config):

    for genome_id, genome in genomes:
        genome.fitness = 0
        model = neat.nn.FeedForwardNetwork.create(genome, config)
        bot_mover = bot_mover_maker(model)

        genome.fitness = play(bot_mover)

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
    winner = p.run(train_generation, 20)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


run_neat('config-feedforward.txt')
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
from game import play, START_GEN


PLAYS_PER_BOT = 5

def bot_mover_maker(model):
    def bot_mover(state, snake):

        guesses = model.activate(state)

        dir = np.argmax(guesses)

        if dir == 0 and not snake.dir == snake.down:
            snake.dir = snake.up
        elif dir == 1 and not snake.dir == snake.left:
            snake.dir = snake.right
        elif dir == 2 and not snake.dir == snake.up:
            snake.dir = snake.down
        elif dir == 3 and not snake.dir == snake.right:
            snake.dir = snake.left

    return bot_mover


def train_generation(genomes, config):
    fitnesses = 0


    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        model = neat.nn.FeedForwardNetwork.create(genome, config)
        bot_mover = bot_mover_maker(model)
        for _ in range(PLAYS_PER_BOT):
            genome.fitness += play(bot_mover) / PLAYS_PER_BOT
            fitnesses += genome.fitness

    print('#  ' * 30, fitnesses / len(genomes))

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
    if START_GEN == 0:
        p = neat.Population(config)
    else:
        p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-' + str(START_GEN))
    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(50))

    # Run for up to 20 generations.
    winner = p.run(train_generation, 1000)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


run_neat('config-feedforward.txt')
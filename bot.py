"""
Code for training a Snake bot using NEAT



"""
import neat
import numpy as np
from game import play, START_GEN
import game


PLAYS_PER_BOT = 3



def bot_mover_maker(model):
    def bot_mover(state, snake):

        guesses = model.activate(state)

        # turn = np.argmax(guesses) # left, straight, or right
        #
        # snake.dir = snake.turn_directions[snake.dir][turn]

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


def train_generation(genomes, config):

    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        model = neat.nn.FeedForwardNetwork.create(genome, config)
        bot_mover = bot_mover_maker(model)
        for _ in range(PLAYS_PER_BOT):
            genome.fitness += play(bot_mover) / PLAYS_PER_BOT

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
    p = neat.Checkpointer.restore_checkpoint('gamers_box=5_hidden=18')
    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(50))

    print(p.config.genome_config.num_hidden, p.config.genome_config.num_inputs, p.config.pop_size)

    # Run for up to ?? generations.
    winner = p.run(train_generation, 1000)






    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

    game.WATCH = True
    game.USE_FRAMERATE = True
    winner_model = neat.nn.FeedForwardNetwork.create(winner, config)
    score = np.average([play(bot_mover_maker(winner_model)) for _ in range(10)])

    print(score)


run_neat('config-feedforward.txt')
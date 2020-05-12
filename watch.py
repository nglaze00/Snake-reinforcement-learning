"""
Code to watch the best bot play Snake
"""
import pickle
import game, bot
import neat
import numpy as np

def preset_food_pos_maker(positions):
    """
    Returns a function that returns the next position in :positions: each time it's called
    :param positions: list of tuples
    :return: function with no args
    """
    pos = positions
    def preset_food_pos():
        try:
            return pos.pop(0)
        except Exception:
            print('out of given positions; using random ones')
            return game.rand_pos()
    return preset_food_pos

def watch_best(genome_file, config_file, food_pos_file):
    """
    Watch a particularly good game of Snake
    """
    # Import best game data
    genome = pickle.load(open(genome_file, 'rb'))
    config = pickle.load(open(config_file, 'rb'))
    food_positions = pickle.load(open(food_pos_file, 'rb'))

    # Generate model from best genome
    model = neat.nn.FeedForwardNetwork.create(genome, config)

    ## Play game
    # Must be true to observe game being played
    game.WATCH = True
    game.USE_FRAMERATE = True

    # Functions that control movement of snake and positioning of food
    snake_controller = bot.bot_mover_maker(model)
    food_controller = preset_food_pos_maker(food_positions)

    print('Score:', game.play(snake_controller, food_controller))




def watch_games(genome_file, config_file):
    """
    Loads the given genome from file and plays Snake repeatedly, using that genome to control the bot
    :param genome_file: name of genome file
    """
    # Import best genome data
    genome = pickle.load(open(genome_file, 'rb'))
    config = pickle.load(open(config_file, 'rb'))

    # Generate model from best genome
    model = neat.nn.FeedForwardNetwork.create(genome, config)

    # Must be true to observe game being played
    # game.WATCH = True
    # game.USE_FRAMERATE = True


    # Functions that control movement of snake and positioning of food
    snake_controller = bot.bot_mover_maker(model)
    food_controller = game.rand_pos

    while True:
        print('Score:', game.play(snake_controller, food_controller))



game.FRAMERATE = 30
watch_best('best_genome.pkl', 'best_config.pkl', 'best_food_pos.pkl')
watch_games('best_genome.pkl', 'best_config.pkl')
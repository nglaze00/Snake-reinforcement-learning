"""
Code for training a Snake bot using NEAT
"""
import neat

def bot_mover_maker


def train_generation(genomes, config):
    models = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        models.append(neat.nn.FeedForwardNetwork.create(genome, config))


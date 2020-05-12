# Snake-reinforcement-learning
AI trained to play Snake using NEAT reinforcement learning and PyGame.

![Snake bot](snake_bot.gif)

This bot scored 67 points.

## Training using NEAT-Python
[NEAT-Python](https://neat-python.readthedocs.io/en/latest/) is a library that trains neural networks using genetic algorithms. 

The NN is architected as follows:
* **Inputs:** binary matrix representing the N x N grid of spaces around the snake's head, plus 4 boolean values representing whether the food is above, below, left, or right of the head.
* **Hidden nodes:** The initial population has a preset number of hidden nodes, but evolved models will have different numbers.
* **Outputs:** 4 nodes, each representing whether the snake should move up, down, left, or right. The direction with the maximum value is the one that's chosen.

Genetic algorithms train neural networks by first generating a population of models with random weights in the given architecture. After computing the *fitness* of each model (here, the number of foods eaten), a new population is evolved from the best-performing members of the previous one. These new models will have slightly different weights than their predecessors, and occasionally slightly different architectures, as hidden nodes can be added or deleted.

## Tuning
Model settings can be found in [config-feedforward.txt](config-feedforward.txt). Especially effective settings include `pop_size`, `num_hidden`, `num_inputs`, `num_outputs`, and `max_stagnation`. 

A description of all settings can be found in the [NEAT documentation](https://neat-python.readthedocs.io/en/latest/config_file.html).

## Usage
* Run `watch.py` to watch the best trained bot play Snake.
* Run `bot.py` to watch new bots be trained
  ** Change `game.USE_FRAMERATE` and `game.WATCH` to `False` to train faster (without watching)
* Run `game.py` to play Snake. Control with WASD.

# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import numpy as np
from hanabi_learning_environment import pyhanabi
from utils import double_dummy_action, all_worlds
import sys

def print_state(state):
  """Print some basic information about the state."""
  print("")
  print("Current player: {}".format(state.cur_player()))
  print(state)

  # Example of more queries to provide more about this state. For
  # example, bots could use these methods to to get information
  # about the state in order to act accordingly.
  print("### Information about the state retrieved separately ###")
  print("### Information tokens: {}".format(state.information_tokens()))
  print("### Life tokens: {}".format(state.life_tokens()))
  print("### Fireworks: {}".format(state.fireworks()))
  print("### Deck size: {}".format(state.deck_size()))
  print("### Discard pile: {}".format(str(state.discard_pile())))
  print("### Player hands: {}".format(str(state.player_hands())))
  print("")

def print_observation(observation):
  """Print some basic information about an agent observation."""
  print("--- Observation ---")
  print(observation)

def run_game(game_parameters,iterations):
  """Play a game, selecting random actions."""
  
  game = pyhanabi.HanabiGame(game_parameters)
  cum_score = 0
  perfects = 0

  for i in range(iterations):
    state = game.new_initial_state()
    while not state.is_terminal():
      if state.cur_player() == pyhanabi.CHANCE_PLAYER_ID:
        state.deal_random_card()
        continue

      move = double_dummy_action(state)
      state.apply_move(move)
    # print(state)
    cum_score += state.score()
    if state.score() == game.num_colors()*game.num_ranks():
      perfects += 1
  # print(str(iterations) + " games completed.")
  # print("Average Score: " + str(cum_score/iterations))
  # print("Perfect Games: " + str(perfects/iterations*100) + "%")
  return cum_score/iterations

def run_all_games(game_parameters):
  game = pyhanabi.HanabiGame(game_parameters)
  cum_score = 0
  perfects = 0

  # initialize the state
  init_state = game.new_initial_state()
  while init_state.cur_player() == pyhanabi.CHANCE_PLAYER_ID:
    init_state.deal_random_card()
  print(init_state)
  print(init_state.fireworks())
  games = 0
  # enumerate all possible worlds
  for state in all_worlds(game,init_state):
    if len(state.fireworks()) != game_parameters['colors']:
      print(state)
    while not state.is_terminal():
      if state.cur_player() == pyhanabi.CHANCE_PLAYER_ID:
        state.deal_random_card()
        continue
      move = double_dummy_action(state)
      state.apply_move(move)
      print(state)
      print(state.fireworks())
    # print(state)
    cum_score += state.score()
    games += 1
    print("Average Score = " + str(cum_score/games))
    if state.score() == game.num_colors()*game.num_ranks():
      perfects += 1
  # print(str(iterations) + " games completed.")
  # print("Average Score: " + str(cum_score/iterations))
  # print("Perfect Games: " + str(perfects/iterations*100) + "%")
  return cum_score/games

if __name__ == "__main__":
  # Check that the cdef and library were loaded from the standard paths.
  assert pyhanabi.cdef_loaded(), "cdef failed to load"
  assert pyhanabi.lib_loaded(), "lib failed to load"
  # run_game({"players": 2, "random_start_player": False,"colors":int(sys.argv[2])},int(sys.argv[1]))
  r,c = int(sys.argv[1]),int(sys.argv[2])
  s = run_all_games({"players": 2, "random_start_player": False,"ranks":r,"colors":c})
  print("Final Score: " + str(s/(r*c)))
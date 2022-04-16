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

"""Example code demonstrating the Python Hanabi interface."""

from __future__ import print_function

import numpy as np
from hanabi_learning_environment import pyhanabi
from utils import double_dummy_action, possible_cards


def run_game(game_parameters):
  """Play a game, selecting random actions."""

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
    
  game = pyhanabi.HanabiGame(game_parameters)
  print(game.parameter_string(), end="")

  state = game.new_initial_state()
  # state2 = game.new_initial_state()
  while not state.is_terminal():
    if state.cur_player() == pyhanabi.CHANCE_PLAYER_ID:
      state.deal_random_card()
      # state2.deal_random_card()
      continue

    """
    print_state(state)
    print_state(state2)

    # print(state.observation(1).observed_hands()[1])
    print((card.to_dict() for card in state.observation(0).observed_hands()[1]))

    # hands = state.player_hands()
    # for pid,hand in enumerate(hands):
    #   print(hand)
    #   state2.set_hand(pid,hand)

    state2.set_hand(1,(card.to_dict() for card in state.observation(0).observed_hands()[1]))
    # state2.set_hand(1,state.observation(1).observed_hands()[1])

    print(state)
    print(state2)

    # other_state = state.copy()
    # print(other_state)
    # print(other_state._state.Deck())
    """

    if state.cur_player() < -1:
      move = double_dummy_action(state)
    else:
      observation = state.observation(state.cur_player())
      print_observation(observation)

      legal_moves = state.legal_moves()
      print("")
      print("Number of legal moves: {}".format(len(legal_moves)))
      print("Legal moves:")
      print('\n'.join(str(i) + ": " + str(m) for i,m in enumerate(legal_moves)))
      move_idx = int(input('Whats is your move?'))
      move = legal_moves[move_idx]
      # move = np.random.choice(legal_moves)
      # print("Chose random legal move: {}".format(move))

    print(move)

    state.apply_move(move)

    print(possible_cards(game,state.observation()))

  print("")
  print("Game done. Terminal state:")
  print("")
  print(state)
  print("")
  print("score: {}".format(state.score()))


if __name__ == "__main__":
  # Check that the cdef and library were loaded from the standard paths.
  assert pyhanabi.cdef_loaded(), "cdef failed to load"
  assert pyhanabi.lib_loaded(), "lib failed to load"
  run_game({"players": 2, "random_start_player": False, "colors":2})

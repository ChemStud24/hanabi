from hanabi_learning_environment import pyhanabi
from hanabi_learning_environment.pyhanabi import color_char_to_idx, color_idx_to_char, HanabiMove, HanabiMoveType
# from pyhanabi import color_char_to_idx, HanabiMove
import random
from itertools import permutations

def is_discardable(color,rank,state):
	return rank <= state.fireworks()[color_char_to_idx(color)]

def discard_legal(state):
	for move in state.legal_moves():
		if move.type() == HanabiMoveType.DISCARD:
			return True
	return False

def double_dummy_action(state,max_rank=None):
	cur_hand = [card.to_dict() for card in state.player_hands()[state.cur_player()]]

	# if I have a playable card, play it
	for idx,card in enumerate(cur_hand):
		if state.card_playable_on_fireworks(color_char_to_idx(card['color']),card['rank']):
			# print('playable')
			return HanabiMove.get_play_move(idx)

	# if you have a playable card, I will give a random clue if allowed
	if state.information_tokens() > 0:
		all_hands = state.player_hands()
		for pid,hand in enumerate(all_hands):
			if pid != state.cur_player():
				hand = (card.to_dict() for card in hand)
				for idx,card in enumerate(hand):
					if state.card_playable_on_fireworks(color_char_to_idx(card['color']),card['rank']):
						# give the first clue
						for move in state.legal_moves():
							if move.type() == HanabiMoveType.REVEAL_COLOR or move.type() == HanabiMoveType.REVEAL_RANK:
								# print('clue playable')
								return move

	if discard_legal(state):

		# if I have a discardable card, I will discard it
		for idx,card in enumerate(cur_hand):
			if is_discardable(card['color'],card['rank'],state):
				# print('discard')
				return HanabiMove.get_discard_move(idx)

		# if I have duplicates, I will discard one
		# else, I will discard the highest card in my hand
		dups = []
		highest = -1
		high_idx = -1
		for idx,card in enumerate(cur_hand):
			if card in dups:
				# print('duplicate')
				return HanabiMove.get_discard_move(idx)
			else:
				dups.append(card)
				# if given, don't discard the max rank because there is only 1 of each
				if card['rank'] > highest and card['rank'] != max_rank:
					highest = card['rank']
					high_idx = idx
		if high_idx != -1:
			# print('high')
			return HanabiMove.get_discard_move(high_idx)

	# if discarding is illegal (max info tokens) then give a clue
	for move in state.legal_moves():
		if move.type() == HanabiMoveType.REVEAL_COLOR or move.type() == HanabiMoveType.REVEAL_RANK:
			# print('clue random')
			return move

	# if we declined to discard a 5 (max rank) but there are no info tokens left
	for move in state.legal_moves():
		if move.type() == HanabiMoveType.DISCARD:
			# print('discard random')
			return move

	# an edge case where none of the above is true
	# this should never happen
	print("THIS IS REALLY BAD")
	return random.choice(state.legal_moves())

def double_dummy_playout(state):
	while not state.is_terminal():
		if state.cur_player() == pyhanabi.CHANCE_PLAYER_ID:
			state.deal_random_card()
			continue

		move = double_dummy_action(state)
		state.apply_move(move)
	return state.score()

def all_cards(game):
	for c in range(game.num_colors()):
		for r in range(game.num_ranks()):
			yield {'color':color_idx_to_char(c),'rank':r}
			if r != game.num_ranks()-1:
				yield {'color':color_idx_to_char(c),'rank':r}
			if r == 0:
				yield {'color':color_idx_to_char(c),'rank':r}

def possible_cards(game,observation):
	unseen_cards = list(all_cards(game))
	[unseen_cards.remove(card.to_dict()) for hand in observation.observed_hands() for card in hand if card.rank() >= 0]
	[unseen_cards.remove(card.to_dict()) for card in observation.discard_pile()]
	return unseen_cards

def possible(cards,observation):
	# check if a set of cards in my hand is congruent with the information I have
	my_knowledge = observation.card_knowledge()[0]
	for c in range(len(cards)):
		if my_knowledge[c].rank_plausible(cards[c]['rank']) and my_knowledge[c].color_plausible(color_char_to_idx(cards[c]['color'])):
			continue
		else:
			return False
	return True

def all_worlds(game,state):
	obs = state.observation(state.cur_player())
	cards = possible_cards(game,obs)
	my_hand_size = len(obs.observed_hands()[0])
	possible_hands = permutations(cards,my_hand_size)
	worlds = []
	for hand in possible_hands:
		if possible(hand,obs):
			worlds.append(state.copy())
			worlds[-1].set_hand(state.cur_player(),hand)
	return worlds

def PIMC(game,state):
	moves = state.legal_moves()
	score = [0]*len(moves)
	for m,move in enumerate(moves):
		for w in all_worlds(game,state):
			print(w)
			w.apply_move(move)
			print(move)
			score[m] += double_dummy_playout(w)
			print(score[m])
	# return the move with the max score
	return max(zip(score,moves))[1]
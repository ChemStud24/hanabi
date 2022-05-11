from hanabi_learning_environment import pyhanabi
from hanabi_learning_environment.pyhanabi import color_char_to_idx, color_idx_to_char, HanabiMove, HanabiMoveType
# from pyhanabi import color_char_to_idx, HanabiMove
import random
from itertools import permutations

NUM_PLAYERS = 2

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
		# print('DD')
		# print(move)
		state.apply_move(move)
	return state.score()

def fireworks_2_cards(fireworks):
	cards = []
	for c,r in enumerate(fireworks):
		cards.extend({'color':color_idx_to_char(c),'rank':rank} for rank in range(r))
	return cards

def all_cards(game):
	for c in range(game.num_colors()):
		for r in range(game.num_ranks()):
			yield {'color':color_idx_to_char(c),'rank':r}
			if r != game.num_ranks()-1:
				yield {'color':color_idx_to_char(c),'rank':r}
			if r == 0:
				yield {'color':color_idx_to_char(c),'rank':r}
			if game.num_ranks() == 1:
				yield {'color':color_idx_to_char(c),'rank':r}

def possible_cards(game,observation):
	unseen_cards = list(all_cards(game))
	[unseen_cards.remove(card.to_dict()) for hand in observation.observed_hands() for card in hand if card.rank() >= 0]
	[unseen_cards.remove(card.to_dict()) for card in observation.discard_pile()]
	[unseen_cards.remove(card) for card in fireworks_2_cards(observation.fireworks())]
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

def k_worlds(game,state,k):
	obs = state.observation(state.cur_player())
	cards = possible_cards(game,obs)
	my_hand_size = len(obs.observed_hands()[0])
	possible_hands = permutations(cards,my_hand_size)
	worlds = []
	for hand in possible_hands:
		if possible(hand,obs):
			worlds.append(state.copy())
			worlds[-1].set_hand(state.cur_player(),hand)
		if len(worlds) >= k:
			break
	return worlds

def PIMC(game,state,k=None):
	moves = state.legal_moves()
	score = [0]*len(moves)

	if k == None:
		worlds = all_worlds(game,state)
	else:
		worlds = k_worlds(game,state,k)

	for m,move in enumerate(moves):
		these_worlds = [w.copy() for w in worlds]
		for w in these_worlds:#all_worlds(game,state):
			w.apply_move(move)
			score[m] += double_dummy_playout(w)
	# return the move with the max score
	i = max((x,i) for i,x in enumerate(score))[1]
	# print(score)
	# print(moves)
	# print(i)
	return moves[i]
	# return max(zip(score,moves))[1]

def get_random_action(state):
	return random.choice(state.legal_moves())

def last_action(state)
	return state.legal_moves()[-1]

def dominates(vec1,vec2):
	if vec1['valid'] != vec2['valid']:
		return False
	return all(v1 >= v2 for v1,v2 in zip(vec1['score'],vec2['score']) if v1 != None and v2 != None)

def max_front(front):
	for vec in front:
		if any(dominates(v,vec) for v in front if v != vec):
			front.remove(vec)
	return front

def front_score(front):
	return max(sum([s for s in vec['score'] if s != None])/len(vec['score']) for vec in front)

def stop(state,M,ply,all_players_worlds):
	player_id = ply % NUM_PLAYERS
	worlds = all_players_worlds[player_id]

	if state.is_terminal():
		return tuple(state.score() for w in worlds)
	if ply >= M:
		return tuple(double_dummy_playout(w) for w in worlds)

def alpha_mu(worlds,M):
	# get this player and this player's worlds
	# player_id = ply % NUM_PLAYERS
	# worlds = all_players_worlds[player_id]

	# # return score if we're in a terminal state
	# if state.is_terminal():
	# 	return tuple(state.score() for w in worlds)

	# return DD results if we're at the end of the search
	if M <= 0:
		for w,state in enumerate(worlds['states']):
			if worlds['valid'][w] and worlds['score'][w] == None:
				worlds['score'][w] = double_dummy_playout(state)
				return [worlds]

	all_moves = []

	for w,state in enumerate(worlds['states']):
		if worlds['valid'][w] and worlds['score'][w] == None:

			# record the score for any worlds in terminal states
			if state.is_terminal():
				worlds['score'][w] = state.score()

			# get all moves
			l = state.legal_moves()
			all_moves.extend(m for m in l if not m in all_moves)

	front = []
	for move in all_moves:
		these_worlds = deep_copy(worlds)
		for w,state in enumerate(these_worlds['states']):
			if these_worlds['valid'][w] and not state.is_terminal():
				if move in state.legal_moves():
					state.apply_move(move)
				else:
					these_worlds['valid'][w] == False
		f = alpha_mu(these_worlds,M-1)
		front = max_front(front + f)
	return front

def get_alpha_mu_action(game,state,M=2,k=100):
	moves = state.legal_moves()
	score = [0]*len(moves)

	worlds = {}
	if k == None:
		worlds['states'] = all_worlds(game,state)
	else:
		worlds['states'] = k_worlds(game,state,k)

	worlds['valid'] = [True]*len(worlds['states'])
	worlds['score'] = [None]*len(worlds['states'])

	# all_players_worlds = [{'states':worlds,'valid':[True]*len(worlds)},'score':[None]*len(worlds)] + [{'states':None,'valid':None,'score':None}]*(NUM_PLAYERS-1)

	for m,move in enumerate(moves):
		these_worlds = deep_copy(worlds)
		for w in these_worlds['states']:
			w.apply_move(move)
		score[m] = front_score(alpha_mu(worlds,M-1))

	# return the move that yielded the highest-scoring front
	i = max((x,i) for i,x in enumerate(score))[1]
	return moves[i]

def deep_copy(worlds):
	new_worlds = {}
	new_worlds['states'] = [w.copy() for w in worlds['states']]
	new_worlds['valid'] = [v for v in worlds['valid']]
	new_worlds['score'] = [s for s in worlds['score']]
	return new_worlds
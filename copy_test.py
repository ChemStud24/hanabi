from hanabi_learning_environment.pyhanabi import HanabiGame

# g = HanabiGame()
# s1 = g.new_initial_state()
# print(s1.fireworks())
# s2 = s1.copy()
# print(s2.fireworks())

for r in range(1,6):
	for c in range(1,6):
		ncards = 2*r*c
		if ncards < 10 or (r == 2 and c == 3) or (r == 3 and c == 2) or (r == 3 and c == 3) or (r == 4 and c == 2) or (r == 4 and c == 3) or (r == 5 and c == 1) or (r == 5 and c == 2):
			continue
		print("Colors: " + str(c))
		print("Ranks: " + str(r))
		g = HanabiGame({"colors":c,"ranks":r})
		s1 = g.new_initial_state()
		print(s1.fireworks())
		s2 = s1.copy()
		print(s2.fireworks())
		print("")
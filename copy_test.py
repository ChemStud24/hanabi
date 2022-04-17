from hanabi_learning_environment.pyhanabi import HanabiGame

# g = HanabiGame()
# s1 = g.new_initial_state()
# print(s1.fireworks())
# s2 = s1.copy()
# print(s2.fireworks())

for r in range(1,6):
	for c in range(1,6):
		ncards = 2*r*c
		if ncards < 10:
			continue
		print("Colors: " + str(c))
		print("Ranks: " + str(r))
		g = HanabiGame({"colors":c,"ranks":r})
		s1 = g.new_initial_state()
		print(s1.fireworks())
		s2 = s1.copy()
		try:
			print(s2.fireworks())
		except:
			print("Core Dumped :/")
		print("")
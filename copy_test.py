from hanabi_learning_environment.pyhanabi import HanabiGame

g = HanabiGame()
s1 = g.new_initial_state()
print(s1.fireworks())
s2 = s1.copy()
print(s2.fireworks())
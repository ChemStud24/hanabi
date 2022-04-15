from DD_test import run_game
from itertools import permutations
from time import time

if __name__ == "__main__":
  # # Check that the cdef and library were loaded from the standard paths.
  # assert pyhanabi.cdef_loaded(), "cdef failed to load"
  # assert pyhanabi.lib_loaded(), "lib failed to load"


  iterations = 10000
  for r in range(1,6):
  	for c in range(1,6):
  		ncards = 2*r*c
  		if ncards < 10:
  			continue
  		nworlds = len(list(permutations(range(ncards-5),5)))
  		t0 = time()
  		run_game({"players": 2, "random_start_player": False,"colors":c,"ranks":r},iterations)
  		t = time() - t0
  		print("Ranks: " + str(r) + " Colors: " + str(c) + " Worlds: " + str(nworlds) + " Time: " + str(nworlds/iterations*t))
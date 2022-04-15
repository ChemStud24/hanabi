from DD_test import run_game

if __name__ == "__main__":
  # Check that the cdef and library were loaded from the standard paths.
  assert pyhanabi.cdef_loaded(), "cdef failed to load"
  assert pyhanabi.lib_loaded(), "lib failed to load"


  iterations = 10000
  for r in range(1,6):
  	for c in range(1,6):
  		ncards = r*c
		run_game({"players": 2, "random_start_player": False,"colors":int(sys.argv[2])},int(sys.argv[1]))
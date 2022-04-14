from itertools import permutations
from time import time

t = time()
l = len(list(permutations(range(45),5)))
print(time()-t)
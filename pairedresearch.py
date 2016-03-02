from mwmatching import * 

import sys
if len(sys.argv) < 2: 
    sys.stderr.write('Usage: python pairedresearch.py weights.txt \n')
    sys.exit(1)

with open(sys.argv[1]) as x: f = x.readlines()

# weights
wm = eval(f[0]) 

matches = maxWeightMatching(wm)

print(matches)

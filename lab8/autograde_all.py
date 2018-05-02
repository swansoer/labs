
import os

params = ['1','2','3','4','5']
scores = []
for i in range(len(params)):
    score  = os.system("py .\\autograder.py %s" % params[i])
    scores.append(score)

for i in range(len(scores)):
    print("For Circle ",params[i]," Score was: ",scores[i])
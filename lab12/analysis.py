# analysis.py
# -----------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


######################
# ANALYSIS QUESTIONS #
######################

# Set the given parameters to obtain the specified policies through
# value iteration.

def question2():
    answerDiscount = 0.9
    answerNoise = 0.2
    return answerDiscount, answerNoise

# These were determined through trial and error while thinking about what parameters
# values would yield the asked for response
def question3a():
    # high discount means it wants to leave early, low noise means will take a risk with
    # the cliff and no living reward means staying alive is no benefit
    answerDiscount = .01
    answerNoise = 0
    answerLivingReward = 0
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'

def question3b():
    # moderate discount means it wants to leave early noise menas it wants to avoid the cliff
    # and a living bonus means it will want to stay alive a bit but not necessarily a long time
    # meaning going up and around is better
    answerDiscount = .1
    answerNoise = .1
    answerLivingReward = .6
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'

def question3c():
    # a small discount means its willing to travel farther for the bigger reward. low noise
    # means its willing to risk the cliff and no living reward means it has no reason to stick around
    answerDiscount = 0.9
    answerNoise = 0
    answerLivingReward = 0
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'

def question3d():
    # a small discount means its willing to travel farther for the bigger reward. moderate noise means
    # it doesn't want to go along the cliff and a smaller living reward means it wants to terminate eventually
    answerDiscount = .9
    answerNoise = .5
    answerLivingReward = .2
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'

def question3e():
    # large noise means it wants to avoid the cliff and generally try moving toward the boarder, a small discount and 
    # a large living reward means that it wants to stick around as long as possible
    answerDiscount = .9
    answerNoise = .9
    answerLivingReward = 10
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'

def question6():
    answerEpsilon = None
    answerLearningRate = None
    return answerEpsilon, answerLearningRate
    # If not possible, return 'NOT POSSIBLE'

if __name__ == '__main__':
    print('Answers to analysis questions:')
    import analysis
    for q in [q for q in dir(analysis) if q.startswith('question')]:
        response = getattr(analysis, q)()
        print('  Question %s:\t%s' % (q, str(response)))

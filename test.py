from simulator.environment import Environment
from learner.q import QLearning
import cProfile
import os
q = QLearning()
filename = os.listdir("files")[2]
filename = "files/" + filename
scenario = Environment(file=filename)

#q.learn(scenario)
cProfile.run('q.learn(scenario)', sort='cumtime')

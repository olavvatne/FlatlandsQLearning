from simulator.environment import Environment
from learner.q import QLearning
import cProfile
import os
q = QLearning()
filename = os.listdir("files")[3]
filename = "files/" + filename
print(filename)
scenario = Environment(file=filename)

#q.learn(scenario)
cProfile.run('q.learn(scenario)', sort='cumtime')

from simulator.environment import Environment
from learner.q import QLearning
import os
q = QLearning()
filename = os.listdir("files")[0]
filename = "files/" + filename
scenario = Environment(file=filename)

q.learn(scenario)
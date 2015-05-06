__author__ = 'Olav'
import itertools
import numpy as np

class QLearning:

    def __init__(self):
        self.discount_factor = 1
        self.learning_rate = 0.1
        self.random_rate = 0.01
        self.q = {}
    def learn(self, scenario, k=10):
        #TODO: can be really massive. Init, during trainnig?
        #TODO:Maybe create Q based on identity of food
        self._create_Q(scenario)
        print(self.q)
        for i in range(k):
            scenario.restart()
            print("ITERATION", i)

            #TODO: go back to start, so food left not enough. Also put in reward for going back at the end.
            while scenario.food_left > 0:
                s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food)
                a = self._select_action(s)
                r = scenario.move_agent(a)
                new_s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food)
                self._update_Q(s,new_s, a,r)


    def _update_Q(self, s,ns, a, r):
        self.q[s][a] = self.q[s][a] + self.learning_rate*(r + (self.discount_factor*(max(self.q[s])) - self.q[s][a]))

    def _select_action(self, s):
        actions = self.q[s]
        m = min(actions)
        probs = [a+m for a in actions]
        s = sum(probs)
        if s>0:
            probs = [a/s for a in probs]
        else:
            probs = [1/len(actions) for i in actions]
        return np.random.choice(list(range(4)), size=1, p=probs)

    def get_state(self, x,y,n):
        return str(x)+","+str(y)+ ","+ str(n)

    def _get_Q(self, s, a):
        return self.q[s][a]


    def _create_Q(self, scenario):
        self.q = {}
        w = [i for i in range(scenario.width)]
        h = [j for j in range(scenario.height)]
        n = [t for t in range(scenario.food_number + 1)]

        per = itertools.product(w, h, n)
        for p in per:
            self.q[str(p[0])+","+str(p[1])+ ","+ str(p[2])] = [0,0,0,0]



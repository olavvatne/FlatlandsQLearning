__author__ = 'Olav'
import itertools
import numpy as np
import random
class QLearning:

    def __init__(self):
        self.discount_factor = 0.5
        self.learning_rate = 0.1
        self.eligbility_trace = .8
        self.stopped = False
        self.q = {}
        self.e = {}

    def learn(self, scenario, k=100):
        self.stopped = False
        #TODO: can be really massive. Init, during trainnig?
        #TODO:Maybe create Q based on identity of food
        self._create_EQ(scenario)
        for i in range(k):
            scenario.restart()
            self.visited = {}
            self.t = 1  - (i/k)
            print("ITERATION", i)
            #TODO: go back to start, so food left not enough. Also put in reward for going back at the end.
            while not scenario.is_goal() and not self.stopped:
                s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food)
                a = self._select_action(s)
                r = scenario.update(a)
                new_s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food)
                self.visited[new_s] = True
                self._update_E(s, a)
                self._update_Q(s,new_s, a,r)

    def test(self, scenario):

        scenario.restart()
        recording = []
        max_steps = scenario.width*scenario.height
        for i in range(max_steps):
            snapshot = scenario.take_snapshot()
            snapshot.append(self._create_action_map(scenario.board, scenario.food))
            #TODO: Action for each state.
            recording.append(snapshot)
            s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food)
            a = self._get_best_action(s)
            r = scenario.update(a)
            if scenario.is_goal():
                break
        snapshot = scenario.take_snapshot()
        snapshot.append(self._create_action_map(scenario.board, scenario.food))
        recording.append(snapshot)

        return recording

    def _create_action_map(self, board, n):
        map = []
        for i in range(len(board)):
            row = []
            for j in range(len(board[0])):
                s = self.get_state(j, i, n)
                row.append(self._get_best_action(s))
            map.append(row)
        return map

    def _update_Q(self, s,ns, a, r):
        #d = r + (self.discount_factor*max(self.q[ns])) - self.q[s][a]
        #self.q[s][a] +=  (self.learning_rate*d)
        d = r + (self.discount_factor*max(self.q[ns])) - self.q[s][a]
        for k in self.visited.keys():
            for i in range(len(self.e[k])):
                self.q[k][i] += self.learning_rate*d*self.e[k][i]

    def _get_best_action(self,s ):
        return max(list(enumerate(self.q[s])), key=lambda k: k[1])[0]

    def _select_action(self, s):

        if random.random() < self.t:
            return random.choice(list(range(4)))
        else:
            actions = self.q[s]
            m = abs(min(actions))
            #TODO: make prob more even at first, since they are , simulated annealing combined
            #TODO: maybe?
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

    def _update_E(self, s, a):
        for k in self.visited.keys():
            for i in range(len(self.e[k])):
                self.e[k][i] = self.discount_factor*self.eligbility_trace*self.e[k][i]
        self.e[s][a] += 1
        #for k in self.visited.keys():
        #    for i in range(len(self.e[k])):
        #        if self.e[k][a] == 0:
        #            del self.visited[k]

    def _create_EQ(self, scenario):
        self.q = {}
        self.e = {}
        w = [i for i in range(scenario.width)]
        h = [j for j in range(scenario.height)]
        n = [t for t in range(scenario.food_number + 1)]

        per = itertools.product(w, h, n)
        for p in per:
            s = str(p[0])+","+str(p[1])+ ","+ str(p[2])
            self.q[s] = [0,0,0,0]
            self.e[s] = [0,0,0,0]



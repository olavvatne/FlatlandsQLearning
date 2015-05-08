__author__ = 'Olav'
import itertools
import numpy as np
import random
from collections import deque

class QLearning:
    LEARNING_RATE = 0.24
    DISCOUNT_FACTOR = 0.9
    ELIGIBILITY_TRACE = 0.34

    def __init__(self, listener=None,l=LEARNING_RATE, d=DISCOUNT_FACTOR, e= ELIGIBILITY_TRACE):
        self.listener = None
        if listener:
            self.listener = listener
        self.discount_factor = d
        self.learning_rate = l
        self.eligibility_trace = e
        self.max_tail = 6
        self.stopped = False
        self.q = {}
        self.e = {}

    def config(self, l=None, d=None, e=None):
        if l:
            self.learning_rate = l
        if d:
            self.discount_factor = d
        if e:
            self.eligibility_trace = e

    def learn(self, scenario, k=100):
        self.stopped = False
        sss = []
        self._create_EQ(scenario)
        for i in range(k):
            scenario.restart()
            self._create_tail()
            self.t = 1  - ((i+1)/k)
            if self.listener:
                self.listener.update(i)
            print("ITERATION", i)
            while not scenario.is_goal() and not self.stopped:
                s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food_state())
                a = self._select_action(s)
                if self.t == 0:
                    sss.append(a)
                r = scenario.update(a)
                new_s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food_state())
                self._add_tail(s,a)
                self._update_E(s, a)
                self._update_Q(s,new_s, a,r)
        print(sss)
    def _check(self, s):
        if s not in self.q:
            self.q[s] = [0,0,0,0]
            self.e[s] = [0,0,0,0]

    def test(self, scenario):
        scenario.restart()
        recording = []
        sss = []
        #Only best actions
        self.t = 0
        max_steps = scenario.width*scenario.height
        for i in range(max_steps):
            #TODO: Not show arrow for unvisited states
            recording.append(self._gui_snapshot(scenario))
            s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food_state())
            a = self._select_action(s)
            if self.t == 0:
                sss.append(a)
            r = scenario.update(a)
            if scenario.is_goal():
                break
        print(sss)
        recording.append(self._gui_snapshot(scenario))
        return recording

    def _gui_snapshot(self, scenario):
        snapshot = scenario.take_snapshot()
        snapshot.append(self._create_action_map(scenario.board, scenario.food_state()))
        return snapshot

    def _create_tail(self):
        self.visited = deque([])

    def _add_tail(self, s, a):
        self.visited.appendleft((s, a))
        if len(self.visited) > self.max_tail:
            ds, da = self.visited.pop()
            #TODO: When looping this will set propagation to zero!
            self.e[ds][da] = 0

    def _create_action_map(self, board, n):
        map = []
        for i in range(len(board)):
            row = []
            for j in range(len(board[0])):
                s = self.get_state(j, i, n)
                row.append(self._select_action(s))
            map.append(row)
        return map

    def _update_Q(self, s,ns, a, r):
        q = self.q
        e = self.e
        learn = self.learning_rate
        d = r + (self.discount_factor*max(q[ns])) - q[s][a]
        for k, i in self.visited:
            q[k][i] += learn*d*e[k][i]

    #def _get_best_action(self,s ):
    #    actions = self.q[s]
    #    return max(enumerate(actions), key=lambda k: k[1])[0]

    def _select_action(self, s):
        if random.random() < self.t:
            return random.choice(list(range(4)))
        else:
            actions = self.q[s]
            #TODO: FIX selection action. Above good enough

            if random.random() < (1-self.t):

                return max(enumerate(actions), key=lambda k: k[1])[0]
            else:
                m = abs(min(actions))
                #TODO: make prob more even at first, since they are , simulated annealing combined
                #TODO: maybe?
                probs = [a+m for a in actions]
                s = sum(probs)
                if s>0:
                    probs = [a/s for a in probs]
                else:
                    probs = [1/len(actions) for i in actions]
                return np.random.choice([0,1,2,3], size=1, p=probs)

    def get_state(self, x,y,n):
        s = str(x)+","+str(y)+ ","+ str(n)
        self._check(s)
        return s

    def _get_Q(self, s, a):
        return self.q[s][a]

    def _update_E(self, s, a):
        e = self.e
        dis = self.discount_factor
        eli = self.eligibility_trace
        for si, ai in self.visited:
            e[si][ai] = dis*eli*e[si][ai]
        e[s][a] += 1

    def set_listener(self, listner):
        self.listener = listner

    def _create_EQ(self, scenario):
        self.q = {}
        self.e = {}



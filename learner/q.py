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
        self.epsilon = 0.1
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
                r = scenario.update(a)
                new_s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food_state())
                self._add_tail(s,a)
                self._update_E(s, a)
                self._update_Q(s,new_s, a,r)
            print("steps",scenario.steps)

    def _check(self, s):
        if s not in self.q:
            self.q[s] = [0,0,0,0]
            self.e[s] = [0,0,0,0]

    def test(self, scenario):
        scenario.restart()
        recording = []
        #Only best actions
        max_steps = scenario.width*scenario.height*4
        for i in range(max_steps):
            recording.append(self._gui_snapshot(scenario))
            s = self.get_state(scenario.agent_x, scenario.agent_y, scenario.food_state())
            a = self._select_action(s, test=True)
            r = scenario.update(a)
            if scenario.is_goal():
                break
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


            #Should not reset self.e if other instance of state in visited
            loop = False
            for ts, ta in self.visited:
                if ts==ds and ta==da:
                    loop = True
                    break
            #TODO: When looping this will set propagation to zero!
            if not loop:
                self.e[ds][da] = 0

    def _create_action_map(self, board, n):
        map = []
        for i in range(len(board)):
            row = []
            for j in range(len(board[0])):
                s = self.get_state(j, i, n)
                row.append(self._select_action(s, test=True))
            map.append(row)
        return map

    def _update_Q(self, s,ns, a, r):
        q = self.q
        e = self.e
        learn = self.learning_rate
        d = r + (self.discount_factor*max(q[ns])) - q[s][a]
        for k, i in self.visited:
            q[k][i] += learn*d*e[k][i]

    def _select_action(self, s, test=False):
        q = self.q[s]
        nr_actions = len(q)
        if test:
            return max(enumerate(q), key=lambda k: k[1])[0]
        maxQ = max(q)

        #Exploration. Agent explore a lot in the start, over time t,
        #this exploration will be reduced
        if random.random() < self.t+self.epsilon:
            minQ = min(q)
            mag = max(abs(minQ), abs(maxQ))
            q = [q[i] + random.random() * mag -+.5*mag for i in range(nr_actions)]
            maxQ = max(q)

        count = q.count(maxQ)
        if count > 1:
            #Random action if Q values does not discriminate
            best = [i for i in range(nr_actions) if q[i] == maxQ]
            i = random.choice(best)
        else:
            #Return best action
            i = q.index(maxQ)
        return i


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



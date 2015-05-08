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
        '''
        The learn method takes an scenario as input. The scenario is what
        the q-learner will use to find q-values and therefore train an agent
        to move about in the scenario.
        '''
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
                s = self.get_state(scenario)
                a = self._select_action(s)
                r = scenario.update(a)
                new_s = self.get_state(scenario)
                self._add_tail(s,a)
                self._update_E(s, a)
                self._update_Q(s,new_s, a,r)
            print("steps",scenario.steps)

    def _check(self, s):
        '''
        The check method, is needed for lazy initing of q-value.
        If the state does not exist in the q map, a new entry is added
        for that particular state. Eligibility trace map is also updated.
        In the case of flatland, there is a huge state-space so initing
        all the possible states is prohibitive
        '''
        if s not in self.q:
            self.q[s] = [0,0,0,0]
            self.e[s] = [0,0,0,0]

    def test(self, scenario):
        '''
        Run after the train method. The train method has found suitable
        q values for state action pairs, and the test method will
        then test the agent. In this case, the agent will use the best
        action for each state, so no exploring.
        The steps taken by the agent is recorded and can be visualized by
        the gui.
        '''
        scenario.restart()
        recording = []
        #Only best actions
        max_steps = scenario.width*scenario.height*4
        for i in range(max_steps):
            recording.append(self._gui_snapshot(scenario))
            s = self.get_state(scenario)
            a = self._select_action(s, test=True)
            r = scenario.update(a)
            if scenario.is_goal():
                break
        recording.append(self._gui_snapshot(scenario))
        return recording

    def _gui_snapshot(self, scenario):
        '''
        The data returned from the scenario is combined with a action map of the board
        to display action for each state visible on the board.
        '''
        snapshot = scenario.take_snapshot()
        snapshot.append(self._create_action_map(scenario.board, scenario.food_state()))
        return snapshot

    def _create_tail(self):
        '''
        Eligibility trace for a big board, or for a big state space is prohibitive.
        A queue or tail of newly visited states are kept, to make tracing possible.
        '''
        self.visited = deque([])

    def _add_tail(self, s, a):
        '''
        The newly visited queue must be updated when an action has been
        done sending the agent into a new state. The visited array is updated,
        by either adding to the queue, or adding and popping the oldest state.
        The eligibility trace value must be reset if no other instances of the state
        is found in the visitied array (When agent goes in a loop). The max_tail
        decide how long this queue should be.
        '''
        self.visited.appendleft((s, a))
        if len(self.visited) > self.max_tail:
            ds, da = self.visited.pop()

            #Should not reset self.e if other instance of state in visited
            loop = False
            for ts, ta in self.visited:
                if ts==ds and ta==da:
                    loop = True
                    break
            if not loop:
                self.e[ds][da] = 0

    def _create_action_map(self, board, n):
        '''
        Using the board, and the current food left in the board, creates
        a action map, that can be visualized by the gui.
        '''
        map = []
        for i in range(len(board)):
            row = []
            for j in range(len(board[0])):
                s = str(j)+","+str(i)+ ","+ str(n)
                self._check(s)
                row.append(self._select_action(s, test=True))
            map.append(row)
        return map

    def _update_Q(self, s,ns, a, r):
        '''
        Update method for the Q-action pairs. Immediate rewards will
        for a new state ns, will be propagated with some loss to previous
        states. How much of the reward will be propagated is decided by
        learning rate, discount factor and the eligibility trace value of previously
        visited states.
        '''
        q = self.q
        e = self.e
        learn = self.learning_rate
        d = r + (self.discount_factor*max(q[ns])) - q[s][a]
        for k, i in self.visited:
            q[k][i] += learn*d*e[k][i]

    def _select_action(self, s, test=False):
        '''
        When selecting an action moving the agent from one state to another,
        exploitation vs exploration must be considered. In the start, when
        the temperature is high (simulated annealing), some randomness is often
        added to the q-action pair values, to promote exploration. Over time
        this temperature will lower, promoting exploitation.
        '''
        actionQ = self.q[s]
        nr_actions = len(actionQ)
        if test:
            return max(enumerate(actionQ), key=lambda k: k[1])[0]
        bestQ = max(actionQ)

        #Exploration. Agent explore a lot in the start, over time t,
        #this exploration will be reduced. #Adds randomness for each action
        if random.random() < self.t+self.epsilon:
            worstQ = min(actionQ)
            magnitude = max(abs(worstQ), abs(bestQ))
            actionQ = [self._randomize(actionQ[i], magnitude) for i in range(nr_actions)]
            bestQ = max(actionQ)

        count = actionQ.count(bestQ)
        if count > 1:
            #Random action if Q values does not discriminate
            best = [i for i in range(nr_actions) if actionQ[i] == bestQ]
            i = random.choice(best)
        else:
            #Return best action
            i = actionQ.index(bestQ)
        return i

    def _randomize(self, v, r):
        '''
        Adds random noise to a value. How much depends on the magnitude r
        '''
        return v + (random.random() * r) - (0.5*r)

    def get_state(self, scenario):
        '''
        Each state for the flatlands scenario consists of a x ,y and n value.
        Specifically for flatlands, means agent position and a ordered bit pattern of
        food eaten this far.
        '''
        s = scenario.get_environment_state()
        self._check(s)
        return s

    def _get_Q(self, s, a):
        return self.q[s][a]

    def _update_E(self, s, a):
        '''
        Backup scheme. The q-learner use eligibility tracing, to update previous
        states with immediate rewards recieved in the current state. For each
        movement of the agent, the eligibilty trace for previously seen states are
        decreased by the formula below. new eligibilty trace value = discount factor x eligibilty trace factor x eligibility trace value
        The current eligibilty trace value representing the state the agents in get's a boost of 1
        '''
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



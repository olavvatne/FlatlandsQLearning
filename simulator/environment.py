import numpy as np
import copy

class Environment:
    EMPTY = 0
    FOOD = 1
    POISON = -1
    PLAYER = -2
    GOAL = -3

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def __init__(self, file=None):
        self.board = []
        if file:
            self.create_environment(file)
        self.agent_x = 0
        self.agent_y = 0
        self.recording = []
        self.poison = 0
        self.food = 0
        self.steps = 0
        self.simple = False

    def create_environment(self, file):
        '''
        Creates an environment from a file.
        '''
        f = open(file, "r")
        board_description = [int(v) for v in f.readline().split()]
        w, h, x,y,n = board_description
        self.width = w
        self.height = h
        self.agent_x = x
        self.agent_y = y

        self.food_number = n
        self.board = []
        for i in range(h):
            self.board.append([int(c) for c in f.readline().split()])
        self.bc = copy.deepcopy(self.board)
        self.bc_x = x
        self.bc_y = y



    def restart(self):
        self.board = copy.deepcopy(self.bc)
        self.agent_x = self.bc_x
        self.agent_y = self.bc_y
        self.food_left = self.food_number
        self.food = 0
        self.poison = 0
        self.steps = 0
        self.eaten = [0 for i in range(self.food_number)]
        self.eaten_str = str(self.eaten)

    def take_snapshot(self):
        '''
        For visualization purposes. A snapshot of the current board
        state is taken, includes the board, food items left and number
        of steps taken by the agent.
        '''
        return [copy.deepcopy(self.board), self.food_left, self.steps]

    def update(self, action):
        '''
        The update method takes an action, implement it on the environment,
        collect reward or punishments and return the reward to the q-learner.
        '''
        content = self._move_agent(action)
        reward = self._reward(content)
        if self.food_left == 0:
            self._generate_reward()
        return reward

    def is_goal(self):
        '''
        If the agent has collected all the food and returned to its starting
        position it has reached it's goal.
        '''
        return self.food_left == 0 and self.agent_x == self.bc_x and self.agent_y == self.bc_y

    def _generate_reward(self):
        '''
        A reward is placed onto the board when the agent has consumed all food
        on the board.
        '''
        self.board[self.bc_y][self.bc_x] = Environment.GOAL

    def _reward(self, content):
        '''
        The environment gives out rewards or punishments using this method.
        Poison : -1.5, food: 1, step: -0.01.

        '''
        reward = -0.01
        if content >= Environment.FOOD:
            self.food += 1
            self.food_left -= 1
            self.eaten[content-1] = 1
            self.eaten_str = str(self.eaten)
            reward = 2
        elif content == Environment.POISON:
            self.poison += 1
            reward = -1.5
        elif content == Environment.GOAL:
            reward = 1
        return reward

    def _move_agent(self, action):
        '''
        Move agent method implement an action on the board. An agent can go
        left right up and down. The environment also has wrap around.
        The content of the cell the agent's currently in will be returned.
        This can be an empty cell, food cell or poison cell.
        '''
        x = self.agent_x
        y = self.agent_y

        self.board[y][x] = Environment.EMPTY
        if action == Environment.NORTH:
            y = (y-1)%self.height
        elif action == Environment.EAST:
             x = (x+1)%self.width
        elif action == Environment.SOUTH:
            y = (y+1)%self.height
        else:
            x = (x-1)%self.width

        self.agent_x = x
        self.agent_y = y
        content = self.board[y][x]
        self.board[y][x] = Environment.PLAYER
        self.steps += 1
        return content

    def food_state(self):
        '''
        For simple mode , the order of the food eaten does not matter
        for the state.
        '''
        if self.simple:
            return str(self.food)
        else:
            return self.eaten_str

    def __repr__(self):
        return str(self.board)


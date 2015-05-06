import numpy as np
import copy

class Environment:
    EMPTY = 0
    FOOD = 1
    POISON = -1
    PLAYER = -2

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    MOVE_FORWARD = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    #TODO: fix directionality
    MOVE_DOWN = 3

    def __init__(self, file=None):
        self.board = []
        if file:
            self.create_environment(file)
        self.agent_x = 0
        self.agent_y = 0
        self.recording = []
        self.poison = 0
        self.food = 0

    def create_environment(self, file):
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


    def init_scoring(self):
        b = np.empty_like (self.board)
        b[:] = self.board
        #TODO: Might consider using a structure to keep track of changes made
        #to board while sim
        self.food = 0
        self.poison = 0
        y = self.agent_y
        x = self.agent_x
        dir = self.agent_dir
        return b, y, x, dir

    def restart(self):
        self.board = copy.deepcopy(self.bc)
        self.agent_x = self.bc_x
        self.agent_y = self.bc_y
        self.food_left = self.food_number
        self.food = 0
        self.poison = 0

    '''def score_agent(self, agent):
        #TODO: No timesteps, apparently
        b, y, x, dir = self.init_scoring()
        #print("SCORE ------------------------------------")

        self.recording = []
        timesteps=60
        for i in range(timesteps):

            #Senor gathering
            food_sensors = self._get_sensor_data(y,x,dir, b, Environment.FOOD)
            poison_sensors = self._get_sensor_data(y,x,dir, b, Environment.POISON)
            #Motor output
            motor_output = agent.feedforward(np.array(food_sensors + poison_sensors, dtype=np.int32))
            #print("Motor", motor_output)
            winning_output = np.argmax(motor_output)
            #print("FOOD", food_sensors)
            #print("POISON", poison_sensors)
            #print(i ,motor_output)
            if motor_output[winning_output] > 0.5:
                m = 0
                if winning_output == Environment.MOVE_LEFT:
                    #print("MOVE LEFT")
                    m = -1
                elif winning_output == Environment.MOVE_RIGHT:
                    #print("MOVE RIGHT")
                    m = 1

                #Update scoring and environment
                self.recording.append((i, x,y,(dir+m)%4))
                y,x,dir = self._move_agent(y, x, (dir+m)%4, b)
        #print("Score: ", self.food, self.poison)
        return (self.food, self.poison)
    '''
    '''
    def get_recording(self):
        b = np.empty_like (self.board)
        b[:] = self.board
        rec = []
        for i,x,y, dir in self.recording:
            a = np.empty_like (b)
            a[:] = b
            rec.append((i,x,y, dir, a))
            self._move_agent(y,x, dir, b)
        return rec
    '''
    def move_agent(self, action):
        x = self.agent_x
        y = self.agent_y
        print(x, y)
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
        reward = 0
        if content >= Environment.FOOD:
            self.food += 1
            self.food_left -= 1
            reward = 1
        elif content == Environment.POISON:
            self.poison += 1
            reward = -1
        self.board[y][x] = Environment.PLAYER
        return reward


    def __repr__(self):
        return str(self.board)


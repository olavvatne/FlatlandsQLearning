import numpy as np


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
        self.agent_dir = Environment.NORTH
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

        print(self.board)


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

    def score_agent(self, agent, timesteps=60):
        b, y, x, dir = self.init_scoring()
        #print("SCORE ------------------------------------")
        #TODO: Create a record method? And not dilute score agent
        self.recording = []

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

    def _move_agent(self, y,x, dir, b):
        #print("dir", dir)
        if dir == Environment.NORTH:
            y = (y-1)%self.dim
        elif dir == Environment.EAST:
             x = (x+1)%self.dim
        elif dir == Environment.SOUTH:
            y = (y+1)%self.dim
        else:
            x = (x-1)%self.dim

        content = b[y][x]
        if content == Environment.FOOD:
            self.food += 1
        elif content == Environment.POISON:
            self.poison += 1
        b[y][x] = Environment.EMPTY
        return (y, x, dir)


    def _get_sensor_data(self, y,x, dir, b,type):
        dim = len(b)
        if dir == Environment.NORTH:
            data = [b[y][(x-1)%dim] == type,
                    b[(y-1)%dim][x] == type,
                    b[y][(x+1)%dim] == type]
        elif dir == Environment.EAST:
            data = [b[(y-1)%dim][x] == type,
                    b[y][(x+1)%dim] == type,
                    b[(y+1)%dim][x]== type]
        elif dir == Environment.SOUTH:
            data = [b[y][(x+1)%dim] == type,
                    b[(y+1)%dim][x] == type,
                    b[y][(x-1)%dim]== type]
        else:
            data = [b[(y+1)%dim][x] == type,
                    b[y][(x-1)%dim] == type,
                    b[(y-1)%dim][x]== type]
        return data


    def __repr__(self):
        return str(self.board)


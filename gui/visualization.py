from tkinter import Toplevel, Button
from simulator.environment import Environment
from tkinter import *
from tkinter import ttk
from enum import Enum
from math import fabs, floor
from gui.elements import LabelledSelect
from collections import deque

#Subclass of the tkinters Canvas object. Contains methods
#for setting a graph model and drawing a graph, and changing
#the vertices' colors.
class PixelDisplay(Canvas):
    cWi = 500
    cHi = 500

    def __init__(self, parent):
        self.pd = 0
        self.queue = deque([])
        self.model = None
        self.width = self.cWi
        self.height = self.cHi
        self.padding = int(self.width/64)
        self.parent = parent
        self.offset = 1
        self.event_rate = 400
        self._callback_id = None
        super().__init__(parent, bg='#1C3C4A', width=self.width, height=self.height, highlightthickness=0)

    def set_rate(self, n):
        self.event_rate = n

    def set_model(self, model):
        self.model = model

    def get_model(self):
        return self.model


    def draw(self):
        '''
        Draw will call itself and redraw (colorize nodes) as long
        as the display is in running mode or there are timeslices left
        in the queue. The queue of timeslices allow the algorithm to run at
        full speed while the display is delaying the rendering, so it is easy to
        watch it's progress

        Draw will pop a timeslice from the draw queue, and
        use it's data to draw the partial solution on screen.
        Each cell will be assigned a color, and a arrow/point to indicate
        direction the cell gives its output.
        '''
        if len(self.queue)>0:
            timeslice = self.queue.popleft()
            if timeslice:
                self.draw_model(timeslice)


        if not self.stopped or len(self.queue) > 0:
            self._callback_id =self.after(self.event_rate, self.draw)

    def colorize_item(self, item, color):
        self.itemconfig(item, fill=color)


    def draw_label(self, x_pos, y_pos, w, h, text,t="label", c="black"):
        x = self.translate_x(x_pos)
        y = self.translate_y(y_pos)
        w = self.translate_y(x_pos + w)
        h = self.translate_y(y_pos + h)
        penalty = len(text)
        font_size = 35 -penalty*2
        font = ("Helvetica", font_size, "bold")
        self.create_text((x+w)/2, (y+h)/2, text=text, tags=t, fill=c, font=font)

    #Method for drawing a graph from a ProblemModel.
    #Draws the model and add tags so individual nodes can later
    #be changed.
    def draw_model(self, timeslice):
        pass

    def start(self):
        self.stop()
        self.stopped = False
        self.draw()

    def stop(self):
        self.stopped = True
        if self._callback_id:
            self.after_cancel(self._callback_id)

    #The actual x position of the graph element on screen
    def translate_x(self, x):


        if self.width/self.w < self.height/self.h:
            mpixels= self.width
            m = self.w
        else:
            mpixels= self.height
            m = self.h

        x_norm = fabs(self.min_x) + x
        x_screen =  self.pd + x_norm*(float((mpixels)/m))
        return x_screen

    #The actual y position of the graph element on screen
    def translate_y(self, y):
        if self.width/self.w < self.height/self.h:
            mpixels= self.width
            m = self.w
        else:
            mpixels= self.height
            m = self.h
        y_norm = fabs(self.min_y) + y
        y_screen =  y_norm*(float((mpixels)/m))
        return y_screen

    def reset(self):
        self.delete(ALL)

    def set_padding(self, padding):
        self.padding = padding

    #draws a cell.
    def draw_pixel(self, x,y, w, h, c, tag=""):
        self.create_rectangle(self.translate_x(x),
            self.translate_y(y),
            self.translate_x(x+w),
            self.translate_y(y+h),
            fill=c,
            tags=tag)

    def draw_rounded(self, x_pos, y_pos, width, height, color, rad=5, tags="", padding=0, line="black"):
        x = self.translate_x(x_pos)+padding
        y = self.translate_y(y_pos)+padding
        w = self.translate_x(x_pos+width)-padding
        h = self.translate_y(y_pos+height)-padding
        self.create_oval(x, y, x +rad, y + rad, fill=color, tag=tags, width=1, outline=line)
        self.create_oval(w -rad, y, w, y + rad, fill=color, tag=tags, width=1, outline=line)
        self.create_oval(x, h-rad, x +rad, h, fill=color, tag=tags, width=1, outline=line)
        self.create_oval(w-rad, h-rad, w , h, fill=color, tag=tags, width=1, outline=line)
        self.create_rectangle(x + (rad/2.0), y, w-(rad/2.0), h, fill=color, tag=tags, width=0)
        self.create_rectangle(x , y + (rad/2.0), w, h-(rad/2.0), fill=color, tag=tags, width=0)

    def set_dimension(self, max_x, max_y, min_x, min_y):
        self.w = fabs(min_x) + max_x
        self.h = fabs(min_y) + max_y
        #self.h = max(self.w, self.h)
        #self.w = self.h
        self.max_x = max_x
        self.max_y = max_y
        self.min_y = min_y
        self.min_x = min_x
        self.set_pd()

    def set_queue(self, data):
        self.queue.clear()
        self.queue.extend(data)

    def scale_draw(self):
        pass
    def event(self, data):
        self.queue.append(data)

    def set_pd(self):
        mw = self.translate_x(self.max_x) - self.translate_x(self.min_x)
        self.pd = (self.width -mw)/2
        print(self.pd)

    def on_resize(self,event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.padding = int(self.width/64)
        #if event.width/self.w > event.height/self.h:
        #    scale = hscale
        #else:
        #    scale = wscale
        self.config(width=self.width, height=self.height)
        #self.scale("all",0,0,scale,scale)
        self.set_pd()
        self.scale_draw()

class FlatlandsDisplay(PixelDisplay):

    def __init__(self, parent):
        super().__init__(parent)

        self.bg = "#bbada0"
        self.empty_cell = "#ccc0b3"

    def draw_board(self):
        if self.model:
            self.reset()
            self.draw_pixel(0, 0, self.model.width, self.model.height, self.bg, tag="bg")
            for i in range(self.model.height):
                for j in range(self.model.width):
                    self.draw_rounded(j,i, 1, 1,  self.empty_cell, padding=1, line=self.bg, tags="bg")
            self.draw_pieces(self.model.board)

    def set_scenario(self, scenario):
        self.set_model(scenario)
        self.set_dimension(scenario.width, scenario.height, 0, 0)
        self.draw_board()

    def draw_model(self, timeslice):
        #TODO: fix
        if timeslice:
            b, f, s, m = timeslice
            self.draw_pieces(b)
            self.draw_arrows(m)
            self.create_text(50, 20, font=("Arial",20), text="P: " +str(f), fill="white", tags="Piece")
            self.create_text(150, 20, font=("Arial",20), text="S: " +str(s), fill="white", tags="Piece")

    def scale_draw(self):
        self.draw_board()

    def draw_pieces(self, board):
        self.delete("Piece")
        for i in range(len(board)):
            for j in range(len(board[0])):
                tile = board[i][j]
                if tile != 0:
                    self.draw_piece("Piece", j, i, tile)
                    if tile>0:
                        self.create_text(self.translate_x(j + 0.5), self.translate_y(i + 0.5), font=("Arial",int(self.width/self.w*0.35)), text=str(tile), fill="#B8DC69", tags="Piece")

    def draw_arrows(self, map):
        self.delete("Arrows")
        for i in range(len(map)):
            for j in range(len(map[0])):
                tile = self._get_arrow(map[i][j])
                self.create_text(self.translate_x(j + 0.5), self.translate_y(i + 0.5), font=("Arial",int(self.width/self.w*0.2)), text=str(tile), fill="#FDEA93", tags="Piece")

    def draw_piece(self, piece_id, x, y, piece_type):
        self.draw_rounded(x,y, 1, 1,  self._get_color(piece_type), padding=2, line=self.bg, tags=piece_id)
        #self.draw_label( x,y, 1,1, str(piece_id), t=piece_id)

    def _get_color(self, type):
        c = {-2:"blue", -1:"#F33803", -3: "orange"}
        if type not in c:
            return "#55A045"
        return c.get(type)

    def _get_arrow(self, type):
        c = {0:"↑", 1:"→", 2:"↓", 3: "←"}
        return c.get(type)
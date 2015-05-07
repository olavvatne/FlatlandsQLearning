from tkinter import *
from tkinter import ttk
import threading

from gui.elements import LabelledSelect, LabelledEntry
from gui.visualization import FlatlandsDisplay
from simulator.environment import Environment
from learner.q import QLearning
import os
import cProfile

class AppUI(Frame):
    '''
    Main user interface of EA. Uses elements found in gui.elements. Layout of application.
    '''
    def __init__(self, master=None):
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        master.title("Flatlands agent using Q-learning")
        Frame.__init__(self, master, relief=SUNKEN, bd=2, highlightthickness=0)
        self.grid(sticky=N+S+E+W)

        #Menu
        self.menubar = Menu(self)
        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="Exit", command=on_exit)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Simulator", menu=menu)
        menu.add_command(label="Run", command=lambda: run_pressed(), accelerator="Ctrl+R")
        master.bind("<Control-r>", lambda event: run_pressed())
        menu.add_command(label="Stop", command=lambda: stop_pressed(), accelerator="Ctrl+S")
        master.bind("<Control-s>", lambda event: stop_pressed())


        def run_pressed():
            run()


        def stop_pressed():
            stop()

        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            self.master.tk.call(master, "config", "-menu", self.menubar)

        #Elements
        options = get_file_listing()
        self.file_selector = LabelledSelect(self, options, "Flatlands scenario", command=load_file)
        self.file_selector.grid(row=0, column=0, sticky=N+S+E+W, padx=4, pady=4)
        self.iteration_entry = LabelledEntry(self, "Iterations", 100)
        self.iteration_entry.grid(row=0, column=2, padx=4, pady=4)

        button = Button(self, text="Run", command=run_pressed)
        button.grid(row=0, column=3, columnspan=1, rowspan=2, padx = 4, pady=4, sticky=N+S+E+W)

        self.learning_rate = LabelledEntry(self, "Learning", 0.01)
        self.learning_rate.grid(row=1, column=0, padx=4, pady=4)

        self.discount = LabelledEntry(self, "Discount", 0.6)
        self.discount.grid(row=1, column=1, padx=4, pady=4)

        self.eligibility = LabelledEntry(self, "Eligibility", 0.9)
        self.eligibility.grid(row=1, column=2, padx=4, pady=4)

        self.canvas = FlatlandsDisplay(self)
        self.canvas.grid(row=2, column=0,columnspan=4, sticky=N+S+E+W ,padx=4, pady=4)

        #Layout behavior
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2,  weight=1)
        self.rowconfigure(2, weight=1)

        #Resize behavior
        self.canvas.bind("<Configure>", self.canvas.on_resize)
        self.canvas.addtag_all("all")


def stop(*args):
    app.canvas.stop()
    q.stopped = True


def run(*args):
    stop()
    def callback():
        q.config(app.learning_rate.get(), app.discount.get(), app.eligibility.get())
        q.learn(app.canvas.model, k=app.iteration_entry.get())
        recording = q.test(app.canvas.model)
        app.canvas.set_queue(recording)
        app.canvas.start()
    t = threading.Thread(target=callback)
    t.daemon = True
    t.start()

def load_file(filename):
    stop()
    filename = "files/" + filename
    scenario = Environment(file=filename)
    app.canvas.set_scenario(scenario)

def on_exit(*args):
    root.quit()

def get_file_listing():
    return os.listdir("files")

root = Tk()
app = AppUI(master=root)
root.bind('<Return>', run)
q = QLearning()
scenarios = get_file_listing()
if len(scenarios)>0:
    load_file(scenarios[0])

#TODO: init q-learner
#TODO: visualize results
root.mainloop()

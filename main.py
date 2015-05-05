from tkinter import *
from tkinter import ttk
import threading

from gui.visualization import FlatlandsDisplay
from simulator.environment import Environment
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
        menu.add_command(label="Load", command=lambda: load_temp_file(), accelerator="Ctrl+L")
        master.bind("<Control-l>", lambda event: load_temp_file())

        def run_pressed():
            run()

        def load_temp_file():
            load_file("ttt")

        def stop_pressed():
            stop()


        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            self.master.tk.call(master, "config", "-menu", self.menubar)


        self.canvas = FlatlandsDisplay(self)
        self.canvas.grid(row=0, column=0, columnspan=5, sticky=N ,padx=4, pady=4)
        self.test = Label(self, text="Test: ")
        self.test.grid(row=0, column=1, sticky=W ,padx=2, pady=4)
        self.columnconfigure(0, minsize="150")





def stop(*args):
    #TODO: stop Q-learner
    pass


def run(*args):
    #TODO: do Q-learning stuff

    def callback():
        pass


    t = threading.Thread(target=callback)
    t.daemon = True
    t.start()

def load_file(filename):
    filename = "files/1-simple.txt"
    scenario = Environment(file=filename)
    app.canvas.set_scenario(scenario)

def on_exit(*args):
    '''
    Exits application
    '''
    root.quit()


root = Tk()
app = AppUI(master=root)
root.bind('<Return>', run)

#TODO: load flatlands file
#TODO: init q-learner
#TODO: visualize results
root.mainloop()

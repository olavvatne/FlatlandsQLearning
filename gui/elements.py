from tkinter import *
from tkinter import ttk


class LabelledSelect(Frame):
    '''
    LabelledSelect is a gui component that create a label and drop down box with options and put them in
    a frame. This element can then be displayed in the GUI. The selected value can be retrieved using the
    get method.
    '''
    def __init__(self, parent, options, label_text, *args, **kwargs):
        command = {}
        if "command" in kwargs:
            command["command"] = kwargs["command"]
            del kwargs["command"]
        Frame.__init__(self, parent, *args, **kwargs)
        self.label = Label(self, text=label_text)
        self.selected = StringVar(self)
        self.selected.set(options[0])
        self.option_select = OptionMenu(self, self.selected, *options, **command)
        self.option_select.pack(side="right", anchor=E)
        self.label.pack(side="left", anchor=W, expand=True)

    def get(self):
        return self.selected.get()

    def add_option(self, option):
        menu = self.option_select["menu"]
        menu.add_command(label=str(option), command=lambda value=option:self.selected.set(str(option)))
class LabelledEntry(Frame):
    '''
    LabelledEntry created a gui component consisting of a label and an entry box. Numbers and text
    can be entered. The element can be put in the Gui. Several methods are supplied for retrieving
    the value.
    '''
    def __init__(self, parent, label_text, default_value,  *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.label = Label(self, text=label_text)
        self.content = StringVar(self)
        self.content.set(str(default_value))
        self.entry = Entry(self, textvariable=self.content)
        self.label.pack(side="left", anchor=W, expand=True)
        self.entry.pack(side="right", anchor=E)

    def get(self):
        '''
        Depending on what has been entered a integer, float or boolean are returned.
        The content of the entry is a string and this method returns a number or a boolean.
        '''
        v = self.content.get()
        if self._is_int(v):
            return int(v)
        elif self._is_float(v):
            return float(v)
        elif v == 'True' or v == 'False':
            return eval(v)
        else:
            raise RuntimeError(v + ". Not a number or bool!")

    def get_special(self):
        v = self.content.get()
        if not len(v)>0:
            return float("inf")
        else:
            return self.get()

    def _is_float(self, n):
        '''
        Test to see if content of entry is a float
        '''
        try:
            float(n)
            return True
        except ValueError:
            return False

    def _is_int(self, n):
        '''
        Test to see if content of entry is a integer
        '''
        try:
            int(n)
            return True
        except ValueError:
            return False



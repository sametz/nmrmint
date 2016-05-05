"""
A copy of main.py for testing varbar construction
"""

from tkinter import *
from guimixin import GuiMixin  # mix-in class that provides dev tools


class RadioFrame(Frame):
    """
    Creates and packs radio button frames into parent.
    arguments:
    -buttons: a tuple of (text, function) tuples
    -title: an optional title to put above the button list
    """
    def __init__(self, parent=None, buttons=(), title='', **options):
        Frame.__init__(self, parent, **options)
        Label(self, text=title).pack(side=TOP)
        self.var = StringVar()
        for button in buttons:
            Radiobutton(self, text=button[0], command=button[1],
                        variable=self.var,
                        value=button[0]).pack(anchor=NW)
        self.var.set(buttons[0][0])  # turns the top button on


# noinspection PyUnusedLocal
class CalcTypeFrame(GuiMixin, RadioFrame):
    """ Defines the Calc Type button frame for the upper left corner"""
    def __init__(self, parent=None, **options):
        title = 'Task'
        buttons = (('Simple',
                    lambda: Models.select_frame('multiplet')),
                   ('Complicated',
                    lambda: Models.select_frame('abc')))
        RadioFrame.__init__(self, parent, buttons=buttons, title=title)

    def show_selection(self):
        self.infobox(self.var.get(), self.var.get())


class ModelFrames(GuiMixin, Frame):
    """
    Creates a frame that stores and manages the individual button menus
    for the different calc types, which will be selected by
    CalcTypeFrame.
    """
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack(side=TOP, anchor=N, expand=YES, fill=X)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # menu placeholders: callbacks will be added as functionality added
        # 'Multiplet' menu: "canned" solutions for common spin systems
        multiplet_buttons = (('Simple Calc I', lambda: None),
                             ('Not So Simple Calc II', lambda: None))
        self.MultipletButtons = RadioFrame(self,
                                           buttons=multiplet_buttons,
                                           title='Simple Task')
        self.MultipletButtons.grid(row=0, column=0, sticky=N)

        # 'ABC...' menu: QM approach
        abc_buttons = (('AB', lambda: AB_bar()),
                       ('3-Spin', lambda: None),
                       ('4-Spin', lambda: None),
                       ('5-Spin', lambda: None),
                       ('6-Spin', lambda: None),
                       ('7-Spin', lambda: None),
                       ('8-Spin', lambda: None))  # 'Custom' omitted for now
        self.ABC_Buttons = RadioFrame(self,
                                      buttons=abc_buttons,
                                      title='2-7 Spins')
        self.ABC_Buttons.grid(row=0, column=0, sticky=N)

        # 'DNMR': models for DNMR line shape analysis
        dnmr_buttons = (('2-spin', lambda: none),
                        ('AB Coupled', lambda: None))
        self.DNMR_Buttons = RadioFrame(self,
                                       buttons=dnmr_buttons,
                                       title='DNMR')
        self.DNMR_Buttons.grid(row=0, column=0, sticky=N)

        # Custom: not implemented yet. Placeholder follows
        self.Custom = Label(self, text='Custom models not implemented yet')
        self.Custom.grid(row=0, column=0)

        self.framedic = {'multiplet': self.MultipletButtons,
                         'abc': self.ABC_Buttons,
                         'dnmr': self.DNMR_Buttons,
                         'custom': self.Custom}
        self.select_frame('multiplet')

    def select_frame(self, frame):
        for key in self.framedic:
            if key == frame:
                self.framedic[key].grid()
            else:
                self.framedic[key].grid_remove()


class VarBox(GuiMixin, Frame):
    """
    Eventually will emulate what the Reich entry box does, more or less.
    Idea is to fill the VarFrame with these modules.
    Current version: checks that only numbers are entered; returns contents
    in a popup.
    Looking ahead: trick may be linking their contents with the calls to
    nmrmath. Also, need to make sure floats, not ints, are returned. Can
    change the is_number routine so that if integer entered, replaced with
    float?
    Inputs:
    -text: appears above the entry box
    -default: default value in entry
    """
    def __init__(self, parent=None, text='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=text).pack(side=TOP)

        ent = Entry(self, validate='key')  # prohibits non-numerical entries
        ent.insert(0, default)
        ent.pack(side=TOP, fill=X)
        self.value = ent.get()
        ent.bind('<Return>', lambda event: self.result(self.value))

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # current design decision: sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    def result(self, value):
        self.infobox('Return', value)

    @staticmethod
    def is_number(entry):
        if not entry:
            return True
        try:
            float(entry)
            return True
        except ValueError:
            return False


class VarFrame(Frame):
    """
    A frame for holding the variable boxes and dictionary of contents

    """
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.dic = {}
        Label(self, text='text goes here').pack(side=TOP, expand=NO)

    def update(self):
        Label.text = str(self.dic)




def warw(bar):
    """
    Many of the models include Wa (width), Right-Hz, and WdthHz boxes.
    This function tacks these boxes onto a frame.
    Input:
    -frame for the Variables Bar
    Output:
    -frame with these three boxes and default values left-packed on end
    """
    pass

class AB_bar(VarFrame):
    """
    Creates a bar of AB quartet inputs.
    """
    def __init__(self, parent=None, **options):
        VarFrame.__init__(self, parent, **options)
        #a = VarBox(self, text='Variable A', default=1.3)
        #a.pack(side=LEFT)
        #a.bind("<FocusOut>", lambda: to_dict(a))
        c = VarBox(self, text='Variable C', default=2.6)
        c.pack(side=LEFT)
        q = VarBox(self, text='Variable Q', default=3.9)
        q.pack(side=LEFT)
        self.grid(sticky=W)

    def to_dict(self, entrybox):
        self.dic[entrybox.__name__] = entrybox.get()
        update()


# Create the main application window:
root = Tk()
root.title('ReichDNMR')  # working title only!

# Create the basic GUI structure: sidebar, topbar, and display area
# First, pack a sidebar frame to contain widgets
sideFrame = Frame(root, relief=RIDGE, borderwidth=3)
sideFrame.pack(side=LEFT, expand=NO, fill=Y)

# Next, pack the top frame where function variables will be entered
Label(root, text='Simple Task Toolbar').pack(side=TOP, expand=YES, fill=X)
variableFrame = Frame(root, relief=RIDGE, borderwidth=1)
variableFrame.pack(side=TOP, expand=NO, fill=X)
variableFrame.grid_rowconfigure(0, weight=1)
variableFrame.grid_columnconfigure(0, weight=1)
AB_bar()
Label(variableFrame, text='placeholder').pack()

# Remaining lower right area will be for a Canvas or matplotlib spectrum frame
# Because we want the spectrum clipped first, will pack it last

# Create sidebar widgets:

# CalcTypeFrame will select which frame of Models displays
CalcTypeFrame(sideFrame, relief=SUNKEN, borderwidth=1).pack(side=TOP,
                                                            expand=NO,
                                                            fill=X)

# modelFrame container will use .grid() to stack multiple RadioFrames
# these RadioFrames will be raised as dictated by the CalcTypeFrame
Models = ModelFrames(sideFrame, relief=SUNKEN, borderwidth=1)
Models.pack(side=TOP, expand=YES, fill=X, anchor=N)

# The clickyFrame for clicking on peaks and calculating frequency differences
# wil not be implemented until much later:
clickyFrame = Frame(sideFrame, relief=SUNKEN, borderwidth=1)
clickyFrame.pack(side=TOP, expand=YES, fill=X)
Label(clickyFrame, text='clickys go here').pack()

specCanvas = Canvas(root, width=800, height=600, bg='beige')
specCanvas.pack(anchor=SE, expand=YES, fill=BOTH)

root.mainloop()

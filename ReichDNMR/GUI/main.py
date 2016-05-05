"""
The main console for ReichDNMR
Currently defines the structure of the window: sidebar with subwidgets,
top bar to hold variable input (currently AB quartet only), display in lower
right. AB quartet toolbar causes a matplotlib plot to pop up.
To do next:
-need to either embed the matplotlib graph as a tkinter widget in lieu of the
canvas, or learn how to plot directly to the canvas
-add "not implemented yet" ToolBars as placeholders fon unimplemented models,
and/or grey out radio buttons for unimplemented routines
-add more models
eventually use warw() to add widgets to the toolbars, *after* nmrmath/nmrplot
is refactored to actually use them
"""

import matplotlib
matplotlib.use("TkAgg")
from ReichDNMR.nmrplot import nmrplot as nmrplt
from tkinter import *
from guimixin import GuiMixin  # mix-in class that provides dev tools
from ReichDNMR.nmrmath import AB


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
        title = 'Calc Type'
        buttons = (('Multiplet',
                    lambda: Models.select_frame('multiplet')),
                   ('ABC...',
                    lambda: Models.select_frame('abc')),
                   ('DNMR', lambda: Models.select_frame('dnmr')),
                   ('Custom', lambda: Models.select_frame('custom')))
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
        multiplet_buttons = (('AB', lambda: None),
                             ('AB2', lambda: None))
        self.MultipletButtons = RadioFrame(self,
                                           buttons=multiplet_buttons,
                                           title='Multiplet')
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


class ToolBar(Frame):
    """
    A frame object that contains entry widgets, a dictionary of
    their current contents, and a function to call the appropriate model.
    """
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.vars = {}

    def call_model(self):
        print('Sending to dummy_model: ', self.vars)


class VarBox(Frame):
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
    def __init__(self, parent=None, name='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))
        ent.bind('<Return>', lambda event: self.on_event(event))
        ent.bind('<FocusOut>', lambda event: self.on_event(event))

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    @staticmethod
    def is_number(entry):
        """
        tests to see if entry is acceptable (either empty, or able to be
        converted to a float.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def on_event(self, event):
        self.to_dict()
        self.master.call_model()
        event.widget.tk_focusNext().focus()

    def to_dict(self):
        """
        On event: Records widget's status to the container's dictionary of
        values, fills the entry with 0.00 if it was empty, tells the container
        to send data to the model, and shifts focus to the next entry box (after
        Return or Tab).
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = float(self.value.get())


# def warw(bar): pass
    """
    Many of the models include Wa (width), Right-Hz, and WdthHz boxes.
    This function tacks these boxes onto a ToolBar.
    Input:
    -ToolBar that has been filled out
    Output:
    -frame with these three boxes and default values left-packed on end
    ***actually, this could be a function in the ToolBar class definition!
    """


class AB_Bar(ToolBar):
    """
    Creates a bar of AB quartet inputs.
    """
    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jab    = VarBox(self, name='Jab',    default=12.00)
        Vab    = VarBox(self, name='Vab',    default=15.00)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jab.pack(side=LEFT)
        Vab.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jab = self.vars['Jab']
        _Vab = self.vars['Vab']
        _Vcentr = self.vars['Vcentr']
        spectrum = AB(_Jab, _Vab, _Vcentr, Wa=0.5, RightHz=0, WdthHz=300)
        nmrplt(spectrum)

# Create the main application window:
root = Tk()
root.title('ReichDNMR')  # working title only!

# Create the basic GUI structure: sidebar, topbar, and display area
# First, pack a sidebar frame to contain widgets
sideFrame = Frame(root, relief=RIDGE, borderwidth=3)
sideFrame.pack(side=LEFT, expand=NO, fill=Y)

# Next, pack the top frame where function variables will be entered
variableFrame = Frame(root, relief=RIDGE, borderwidth=1)
variableFrame.pack(side=TOP, expand=NO, fill=X)
variableFrame.grid_rowconfigure(0, weight=1)
variableFrame.grid_columnconfigure(0, weight=1)
AB_Bar(variableFrame).grid(sticky=W)

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

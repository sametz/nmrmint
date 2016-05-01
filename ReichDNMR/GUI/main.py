"""
The main console for ReichDNMR
Currently defines the structure of the window: sidebar with subwidgets,
top bar to hold variable input, display in lower right.
To do next:
-determine correct order of packing (widgets then container, or vice versa)
-adjust packing behavior in preparation for menuFrame .grid()
-have CalcTypeFrame control which menu displays in menuFrame
-have menuFrame choice create the top bar
-have top bar call a spectrum (probably a matplotlib popup for testing)"""

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
    Creates a frame that will store and manage the individual button menus
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
        abc_buttons = (('AB', lambda: none),
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


# Create the main application window:
root = Tk()
root.title('ReichDNMR')  # working title only!

# Create the basic GUI structure: sidebar, topbar, and display area
# First, pack a sidebar frame to contain widgets
sideFrame = Frame(root, relief=RIDGE, borderwidth=3, bg='orange')
sideFrame.pack(side=LEFT, expand=NO, fill=Y)

# Next, pack the top frame where function variables will be entered
variableFrame = Frame(root, relief=RIDGE, borderwidth=1)
variableFrame.pack(side=TOP, expand=NO, fill=X)
Label(variableFrame, text='variables go here').pack()

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

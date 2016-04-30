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
# from collections import OrderedDict


class RadioFrame(Frame):
    """
    Creates and packs radio button frames into parent.
    arguments:
    -buttons: a tuple of (text, function) tuples
    -title: an optional title to put above the button list
    """
    def __init__(self, parent=None, buttons=(), title='', **options):
        Frame.__init__(self, parent, **options)
        self.pack(side=TOP, expand=NO, fill=X)
        Label(self, text=title).pack(side=TOP)
        self.var = StringVar()
        for button in buttons:
            Radiobutton(self, text=button[0], command=button[1],
                        variable=self.var,
                        value=button[0]).pack(anchor=NW)
        self.var.set(buttons[0][0])


class CalcTypeFrameDeprecated(Frame):
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack()
        Label(self, text='Calc Type').pack(side=TOP)
        self.var = StringVar()
        Radiobutton(self, text='Multiplet',
                          command=lambda: None,
                          variable=self.var,
                          value='multiplet').pack(anchor=NW)
        Radiobutton(self, text='ABC...',
                          command=lambda: None,
                          variable=self.var,
                          value='abc').pack(anchor=NW)
        Radiobutton(self, text='DNMR',
                          command=lambda: None,
                          variable=self.var,
                          value='dnmr').pack(anchor=NW)
        Radiobutton(self, text='Custom',
                          command=lambda: None,
                          variable=self.var,
                          value='custom').pack(anchor=NW)
        self.var.set('multiplet')


# def select_modelframe(selection): reminder to address menu switching


# Create the main application window:
root = Tk()
root.title('ReichDNMR')  # working title only!

# Create the basic GUI structure: sidebar, topbar, and display area
# First, pack a sidebar frame to contain widgets
sideFrame = Frame(root, relief=RIDGE, borderwidth=1)
sideFrame.pack(side=LEFT, expand=NO, fill=Y)

# Next, pack the top frame where function variables will be entered
variableFrame = Frame(root, relief=RIDGE, borderwidth=1)
variableFrame.pack(side=TOP, expand=NO, fill=X)
Label(variableFrame, text='variables go here').pack()

# Remaining lower right area will be for a Canvas or matplotlib spectrum frame
# Because we want the spectrum clipped first, will pack it last

# Create sidebar widgets:
calctypeframe_buttons = (('Multiplet', lambda: None),
                         ('ABC...', lambda: None),
                         ('DNMR', lambda: None),
                         ('Custom', lambda: None))
CalcTypeFrame = RadioFrame(sideFrame,
                           buttons=calctypeframe_buttons,
                           title='Calc Type')
CalcTypeFrame.config(relief=SUNKEN, borderwidth=1)

# modelFrame container will use .grid() to stack multiple RadioFrames
# these RadioFrames will be raised as dictated by the CalcTypeFrame
modelFrame = Frame(sideFrame, relief=SUNKEN, borderwidth=1)

multiplet_buttons = (('AB', lambda: None),
                     ('AB2', lambda: None))
MultipletButtons = RadioFrame(modelFrame,
                              buttons=multiplet_buttons,
                              title='Multiplet')

# The clickyFrame for clicking on peaks and calculating frequency differences
# wil not be implemented until much later:
clickyFrame = Frame(sideFrame, relief=SUNKEN, borderwidth=1)

modelFrame.pack(side=TOP, expand=YES, fill=X)

clickyFrame.pack(side=TOP, expand=YES, fill=X)
Label(clickyFrame, text='clickys go here').pack()

specCanvas = Canvas(root, width=800, height=600, bg='beige')
specCanvas.pack(anchor=SE, expand=YES, fill=BOTH)

root.mainloop()

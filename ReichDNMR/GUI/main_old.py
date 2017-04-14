"""
Rethought the toolbar concept. More straightforward if the ModelFrames
directly controls the top bar contents.
"""

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,\
    NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler  # unused for now
from matplotlib.figure import Figure
from ReichDNMR.nmrplot import tkplot
from tkinter import *
from guimixin import GuiMixin  # mix-in class that provides dev tools
from ReichDNMR.nmrmath import AB, AB2, ABX, ABX3, AAXX, first_order, AABB
from numpy import arange, pi, sin, cos
from collections import deque


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
        """for debugging"""
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

        self.add_multiplet_buttons()  # Creates 'Multiplet' radio button menu
        self.add_abc_buttons()        # Creates 'ABC...' radio button menu
        self.add_dnmr_buttons()       # Creates 'DNMR' radio button menu
        self.add_custom_buttons()     # Creates 'Custom' radio bar menu

        # framedic makes it more convenient to control individual frames
        self.framedic = {'multiplet': self.MultipletButtons,
                         'abc': self.ABC_Buttons,
                         'dnmr': self.DNMR_Buttons,
                         'custom': self.Custom}

        # Initialize with default frame and toolbar
        self.currentframe = 'multiplet'
        self.currentbar = self.ab     # On program start, simulation set to ABq
        self.currentbar.grid(sticky=W)
        self.currentbar.call_model()

    # menu placeholders: callbacks will be added as functionality added

    def add_multiplet_buttons(self):
        """"'Multiplet' menu: 'canned' solutions for common spin systems"""
        multiplet_buttons = (('AB', lambda: self.select_toolbar(self.ab)),
                             ('AB2', lambda: self.select_toolbar(self.ab2)),
                             ('ABX', lambda: self.select_toolbar(self.abx)),
                             ('ABX3', lambda: self.select_toolbar(self.abx3)),
                             ("AA'XX'", lambda: self.select_toolbar(self.aaxx)),
                             ('1stOrd',
                              lambda: self.select_toolbar(self.firstorder)),
                             ("AA'BB'", lambda: self.select_toolbar(self.aabb)))
        self.MultipletButtons = RadioFrame(self,
                                           buttons=multiplet_buttons,
                                           title='Multiplet')
        self.MultipletButtons.grid(row=0, column=0, sticky=N)
        self.ab = AB_Bar(TopFrame)
        self.ab2 = AB2_Bar(TopFrame)
        self.abx = ABX_Bar(TopFrame)
        self.abx3 = ABX3_Bar(TopFrame)
        self.aaxx = AAXX_Bar(TopFrame)
        self.firstorder = FirstOrder_Bar(TopFrame)
        self.aabb = AABB_Bar(TopFrame)

    def add_abc_buttons(self):
        """ 'ABC...' menu: Quantum Mechanics approach"""
        abc_buttons = (('AB', lambda: None),
                       ('3-Spin', lambda: None),
                       ('4-Spin', lambda: None),
                       ('5-Spin', lambda: None),
                       ('6-Spin', lambda: None),
                       ('7-Spin', lambda: None),
                       ('8-Spin', lambda: None))  # 'Custom' omitted for now
        self.ABC_Buttons = RadioFrame(self,
                                      buttons=abc_buttons,
                                      title='2-7 Spins')

    def add_dnmr_buttons(self):
        """'DNMR': models for DNMR line shape analysis"""
        dnmr_buttons = (('2-spin', lambda: None),
                        ('AB Coupled', lambda: None))
        self.DNMR_Buttons = RadioFrame(self,
                                       buttons=dnmr_buttons,
                                       title='DNMR')

    def add_custom_buttons(self):
        # Custom: not implemented yet. Placeholder follows
        self.Custom = Label(self, text='Custom models not implemented yet')

    def select_frame(self, frame):
        if frame != self.currentframe:
            self.framedic[self.currentframe].grid_remove()
            self.currentframe = frame
            self.framedic[self.currentframe].grid()

    def select_toolbar(self, toolbar):
        self.currentbar.grid_remove()
        self.currentbar = toolbar
        self.currentbar.grid(sticky=W)
        try:
            self.currentbar.call_model()
        except ValueError:
            print('No model yet for this bar')


class ToolBox(Frame):
    """
    A frame object that will contain multiple toolbars gridded to (0,0).
    It will maintain a deque of [current, last] toolbars used. When a new model
    is selected by ModelFrames, the new ToolBar is added to the front of the
    deque and .grid(), the current toolbar is pushed down to the last
    position and .grid_remove(), and the previous last toolbar is knocked out
    of the deque.
    """
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.toolbars = deque([], 2)

    def add_toolbar(self, toolbar):
        self.toolbars.appendleft(toolbar)
        toolbar.grid(self)
        if len(self.toolbars) > 1:
            self.toolbars[1].grid_remove()


class MultipletBox(ToolBox):
    """
    A ToolBox for holding and controlling  a ToolBar for each Multiplet model.
    """
    def __init__(self, parent=None, **options):
        ToolBox.__init__(self, parent, **options)
        

class ToolBar(Frame):
    """
    A frame object that contains entry widgets, a dictionary of
    their current contents, and a function to call the appropriate model.
    """
    # f = Figure(figsize=(5, 4), dpi=100)
    # a = f.add_subplot(111)

    # canvas = FigureCanvasTkAgg(f, master=root)
    # canvas.show()
    # canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    # toolbar = NavigationToolbar2TkAgg(canvas, root)
    # toolbar.update()
    # canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.vars = {}

    def call_model(self):
        print('Sending to dummy_model: ', self.vars)


class EmptyToolBar(Frame):
    def __init__(self, parent=None, name='noname', **options):
        Frame.__init__(self, parent, **options)
        Label(self, text=name + ' model not implemented yet').pack()
        self.pack()


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
        ent = Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if a change is made
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())

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

    def entry_is_changed(self):
        return self.master.vars[self.widgetName] != float(self.value.get())

    def on_return(self, event):
        if self.entry_is_changed():
            self.to_dict()
            self.master.call_model()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        if self.entry_is_changed():
            self.to_dict()
            self.master.call_model()

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


class IntBox(Frame):
    """
    A modification of VarBox code. Restricts inputs to integers.
    Inputs:
    -text: appears above the entry box
    -default: default value in entry
    """
    # Future refactor options: either create a base class for an input box
    # that varies in its input restriction (float, int, str etc), and/or
    # look into tkinter built-in entry boxes as component.
    def __init__(self, parent=None, name='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP, expand=NO, fill=NONE)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, width=7, validate='key')  # check for int on keypress
        ent.pack(side=TOP, expand=NO, fill=NONE)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))
        ent.bind('<Return>', lambda event: self.on_event(event))
        ent.bind('<FocusOut>', lambda event: self.on_event(event))

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_int), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    @staticmethod
    def is_int(entry):
        """
        tests to see if entry string can be converted to integer
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            int(entry)
            return True
        except ValueError:
            return False

    def on_event(self, event):
        """
        On event: Records widget's status to the container's dictionary of
        values, fills the entry with 0 if it was empty, tells the container
        to send data to the model, and shifts focus to the next entry box (after
        Return or Tab).
        """
        self.to_dict()
        self.master.call_model()
        event.widget.tk_focusNext().focus()

    def to_dict(self):
        """
        Converts entry to integer, and stores data in container's vars
        dictionary.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = int(self.value.get())


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
    Creates a bar of AB quartet inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AB
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
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class AB2_Bar(ToolBar):
    """
    Creates a bar of AB2 spin system inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AB2
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
        spectrum = AB2(_Jab, _Vab, _Vcentr, Wa=0.5, RightHz=0, WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class ABX_Bar(ToolBar):
    """
    Creates a bar of ABX spin system inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.ABX
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jab = VarBox(self, name='Jab', default=12.00)
        Jax = VarBox(self, name='Jax', default=2.00)
        Jbx = VarBox(self, name='Jbx', default=8.00)
        Vab = VarBox(self, name='Vab', default=15.00)
        Vcentr = VarBox(self, name='Vcentr', default=118)
        Jab.pack(side=LEFT)
        Jax.pack(side=LEFT)
        Jbx.pack(side=LEFT)
        Vab.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jab = self.vars['Jab']
        _Jax = self.vars['Jax']
        _Jbx = self.vars['Jbx']
        _Vab = self.vars['Vab']
        _Vcentr = self.vars['Vcentr']
        spectrum = ABX(_Jab, _Jax, _Jbx, _Vab, _Vcentr, Wa=0.5, RightHz=0,
                       WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class ABX3_Bar(ToolBar):
    """
    Creates a bar of ABX3 spin system inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.ABX3
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jab = VarBox(self, name='Jab', default=-12.00)
        Jax = VarBox(self, name='Jax', default=7.00)
        Jbx = VarBox(self, name='Jbx', default=7.00)
        Vab = VarBox(self, name='Vab', default=14.00)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jab.pack(side=LEFT)
        Jax.pack(side=LEFT)
        Jbx.pack(side=LEFT)
        Vab.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jab = self.vars['Jab']
        _Jax = self.vars['Jax']
        _Jbx = self.vars['Jbx']
        _Vab = self.vars['Vab']
        _Vcentr = self.vars['Vcentr']
        spectrum = ABX3(_Jab, _Jax, _Jbx, _Vab, _Vcentr, Wa=0.5, RightHz=0,
                        WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class AAXX_Bar(ToolBar):
    """
    Creates a bar of AA'XX' spin system inputs. Currently assumes "canvas" is
    the MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AAXX
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jaa = VarBox(self, name="JAA'", default=15.00)
        Jxx = VarBox(self, name="JXX'", default=-10.00)
        Jax = VarBox(self, name="JAX", default=40.00)
        Jax_prime = VarBox(self, name="JAX'", default=6.00)
        Vcentr = VarBox(self, name="Vcentr", default=150)
        Jaa.pack(side=LEFT)
        Jxx.pack(side=LEFT)
        Jax.pack(side=LEFT)
        Jax_prime.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jaa = self.vars["JAA'"]
        _Jxx = self.vars["JXX'"]
        _Jax = self.vars["JAX"]
        _Jax_prime = self.vars["JAX'"]
        _Vcentr = self.vars["Vcentr"]
        spectrum = AAXX(_Jaa, _Jxx, _Jax, _Jax_prime, _Vcentr,
                        Wa=0.5, RightHz=0, WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class AABB_Bar(ToolBar):
    """
    Creates a bar of AA'BB' spin system inputs. Currently assumes "canvas" is
    the MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AABB
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Vab = VarBox(self, name='VAB', default=40.00)
        Jaa = VarBox(self, name="JAA'", default=15.00)
        Jbb = VarBox(self, name="JBB'", default=-10.00)
        Jab = VarBox(self, name="JAB", default=40.00)
        Jab_prime = VarBox(self, name="JAB'", default=6.00)
        Vcentr = VarBox(self, name="Vcentr", default=150)
        Vab.pack(side=LEFT)
        Jaa.pack(side=LEFT)
        Jbb.pack(side=LEFT)
        Jab.pack(side=LEFT)
        Jab_prime.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Vab = self.vars['VAB']
        _Jaa = self.vars["JAA'"]
        _Jbb = self.vars["JBB'"]
        _Jab = self.vars["JAB"]
        _Jab_prime = self.vars["JAB'"]
        _Vcentr = self.vars["Vcentr"]
        spectrum = AABB(_Vab, _Jaa, _Jbb, _Jab, _Jab_prime, _Vcentr,
                        Wa=0.5, RightHz=0, WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class FirstOrder_Bar(ToolBar):
    """
    Creates a bar of first-order coupling inputs. Currently assumes "canvas"
    is the MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.first_order
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        Jax = VarBox(self, name='JAX', default=7.00)
        a = IntBox(self, name='#A', default=2)
        Jbx = VarBox(self, name='JBX', default=3.00)
        b = IntBox(self, name='#B', default=1)
        Jcx = VarBox(self, name='JCX', default=2.00)
        c = IntBox(self, name='#C', default=0)
        Jdx = VarBox(self, name='JDX', default=7.00)
        d = IntBox(self, name='#D', default=0)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jax.pack(side=LEFT)
        a.pack(side=LEFT)
        Jbx.pack(side=LEFT)
        b.pack(side=LEFT)
        Jcx.pack(side=LEFT)
        c.pack(side=LEFT)
        Jdx.pack(side=LEFT)
        d.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def call_model(self):
        _Jax = self.vars['JAX']
        _a   = self.vars['#A']
        _Jbx = self.vars['JBX']
        _b = self.vars['#B']
        _Jcx = self.vars['JCX']
        _c   = self.vars['#C']
        _Jdx = self.vars['JDX']
        _d = self.vars['#D']
        _Vcentr = self.vars['Vcentr']
        singlet = (_Vcentr, 1)  # using default intensity of 1
        allcouplings = [(_Jax, _a), (_Jbx, _b), (_Jcx, _c), (_Jdx, _d)]
        couplings = [coupling for coupling in allcouplings if coupling[1] != 0]
        spectrum = first_order(singlet, couplings,
                               Wa=0.5, RightHz=0, WdthHz=300)
        x, y = tkplot(spectrum)
        canvas.clear()
        canvas.plot(x, y)


class MPLgraph(FigureCanvasTkAgg):
    def __init__(self, f, master=None, **options):
        FigureCanvasTkAgg.__init__(self, f, master, **options)
        self.f = f
        self.a = f.add_subplot(111)
        self.a.invert_xaxis()
        self.show()
        self.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self, master)
        self.toolbar.update()

    def plot(self, x, y):
        self.a.plot(x, y)
        self.f.canvas.draw()  # DRAW IS CRITICAL TO REFRESH

    def clear(self):
        self.a.clear()
        self.f.canvas.draw()


# Create the main application window:
root = Tk()
root.title('ReichDNMR')  # working title only!

# Create the basic GUI structure: sidebar, topbar, and display area
# First, pack a sidebar frame to contain widgets
sideFrame = Frame(root, relief=RIDGE, borderwidth=3)
sideFrame.pack(side=LEFT, expand=NO, fill=Y)

# Next, pack the top frame where function variables will be entered
TopFrame = Frame(root, relief=RIDGE, borderwidth=1)
TopFrame.pack(side=TOP, expand=NO, fill=X)
TopFrame.grid_rowconfigure(0, weight=1)
TopFrame.grid_columnconfigure(0, weight=1)

# Remaining lower right area will be for a Canvas or matplotlib spectrum frame
# Because we want the spectrum clipped first, will pack it last
f = Figure(figsize=(5, 4), dpi=100)
canvas = MPLgraph(f, root)

# Create sidebar widgets:
CalcTypeFrame(sideFrame, relief=SUNKEN, borderwidth=1).pack(side=TOP,
                                                            expand=NO,
                                                            fill=X)
Models = ModelFrames(sideFrame, relief=SUNKEN, borderwidth=1)
Models.pack(side=TOP, expand=YES, fill=X, anchor=N)

# The clickyFrame for clicking on peaks and calculating frequency differences
# will not be implemented until much later:
clickyFrame = Frame(sideFrame, relief=SUNKEN, borderwidth=1)
clickyFrame.pack(side=TOP, expand=YES, fill=X)
Label(clickyFrame, text='clickys go here').pack()

# Now we can pack the canvas (want it to be clipped first)
canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)

Button(root, text='clear', command=lambda: canvas.clear()).pack(side=BOTTOM)

#root.mainloop()

#workaround fix for Tk problems and mac mouse/trackpad:

while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass

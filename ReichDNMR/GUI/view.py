"""
Provides the View for the ReichDNMR Model-View-Controller.

Provides the following classes:
* MPLgraph: Extension of FigureCanvasTkAgg that includes a matplotlib Figure
reference and methods for plotting data.

* View: an extension of tkinter Frame that provides the main GUI.
"""
from tkinter import *

import matplotlib

matplotlib.use("TkAgg")  # must be invoked before the imports below
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from matplotlib.figure import Figure

from ReichDNMR.GUI.frames import RadioFrame
from ReichDNMR.GUI.toolbars import (AB_Bar, AB2_Bar, ABX_Bar, ABX3_Bar,
                                    AAXX_Bar, AABB_Bar, FirstOrder_Bar,
                                    SecondOrderSpinBar,
                                    DNMR_TwoSingletBar,
                                    DNMR_AB_Bar)


class MPLgraph(FigureCanvasTkAgg):
    """The Canvas object for plotting simulated spectra.

    MPLgraph extends on FigureCanvasTkAgg by including a reference to a
    matplotlib Figure object, plus methods for plotting.

    Attributes:
        (TODO: probably should all be private; learn about private attributes)

    Methods:
        plot: plot data to the Canvas
        clear: clear the Canvas

    """
    def __init__(self, figure, master=None, **options):
        """Extend FigureCanvasTkAgg with a Matplotlib Figure object, then add
        and pack itself plus a toolbar into the parent.

        :param figure: a matplotlib.figure.Figure object
        """
        # print('initializing MPLgraph super')
        FigureCanvasTkAgg.__init__(self, figure, master, **options)
        # print('super initialized')
        self.f = figure
        # print('figure associated with self.f')
        self.add = figure.add_subplot(111)
        # print('called figure.add_subplot')
        self.add.invert_xaxis()
        # print('inverted x axis')
        # line below used/worked in past...but is it really needed?
        # self.show()
        # print('showing MPLgraph')
        self.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        # print('tk widget packed')
        self.toolbar = NavigationToolbar2TkAgg(self, master)
        # print('created toolbar')
        self.toolbar.update()
        # print('toolbar updated')
        # print('MPLgraph initialized')

    def plot(self, x, y):
        """Plot x, y data to the Canvas.

        :param x: (numpy linspace)
        :param y: (numpy linspace)
        """
        self.add.plot(x, y)
        # apparently .draw_idle() gives faster refresh than .draw()
        self.f.canvas.draw_idle()  # DRAW IS CRITICAL TO REFRESH

    def clear(self):
        """Clear the Canvas."""
        self.add.clear()
        self.f.canvas.draw()


class View(Frame):
    """Provides the GUI for ReichDNMR by extending a tkinter Frame.

    Methods:
        initialize_spinbars, add_calc_type_frame, add_model_frames,
        add_multiplet_buttons, add_abc_buttons, add_dnmr_buttons,
        add_custom_buttons, add_plot: used by __init__ to instantiate the GUI.

        select_calc_type: select the type of calculation to use (i.e
        first-order {'Multiplet'), second-order {'abc...'}, DNMR, or Custom).

        select_toolbar: Display the toolbar for the selected calculation
        along the top of the GUI.

        initialize: Call the controller to initialize the plot on the Canvas

        clear: Clear the Canvas
        plot: Plot data to the Canvas
    """

    def __init__(self, parent, controller, **options):
        Frame.__init__(self, parent, **options)
        self.controller = controller

        self.SideFrame = Frame(self, relief=RIDGE, borderwidth=3)
        self.SideFrame.pack(side=LEFT, expand=NO, fill=Y)

        self.TopFrame = Frame(self, relief=RIDGE, borderwidth=1)
        self.TopFrame.pack(side=TOP, expand=NO, fill=X)
        self.TopFrame.grid_rowconfigure(0, weight=1)
        self.TopFrame.grid_columnconfigure(0, weight=1)

        spinbar_kwargs = {'controller': self.controller,
                          'realtime': True}
        self.initialize_spinbars(**spinbar_kwargs)
        self.add_calc_type_frame()
        # print('returned from add_calc_type frame; ')
        self.add_model_frames()
        # print('adding abc buttons')
        # self.add_abc_buttons()
        # print('returned from adding abc buttons')
        # print('adding plot')
        self.add_plot()
        # print('plot added')
        # print('View initialization complete')

    def initialize_spinbars(self, **kwargs):
        """Instantiate all of the SecondOrderSpinBar objects, and store
        references to them.

        Attributes created:
            spin_range: the number of spins the program will accomodate.
            spinbars: a list of SecondOrderSpinBar objects, one for each
            number of spins to simulate.

        Keyword arguments:
            **kwargs: standard SecondOrderSpinBar kwargs
        """
        self.spin_range = range(2, 9)  # hardcoded for only 2-8 spins
        self.spinbars = [SecondOrderSpinBar(self.TopFrame, n=spins,
                                            **kwargs)
                         for spins in self.spin_range]

    def add_calc_type_frame(self):
        """Add a menu for selecting the type of calculation to the upper left
        of the GUI.

        Attribute created:
            CalcTypeFrame: the RadioFrame being packed into the GUI.
        """
        # print('add_calc_type_frame called')
        title = 'Calc Type'
        # print('assigned title')
        buttons = (('Multiplet', lambda: self.select_calc_type('multiplet')),
                   ('ABC...', lambda: self.select_calc_type('abc')),
                   ('DNMR', lambda: self.select_calc_type('dnmr')),
                   ('Custom', lambda: self.select_calc_type('custom')))
        # print('defined buttons')
        self.CalcTypeFrame = RadioFrame(self.SideFrame,
                                        buttons=buttons, title=title,
                                        relief=SUNKEN, borderwidth=1)
        # print('instantiated CalcTypeFrame')
        self.CalcTypeFrame.pack(side=TOP, expand=NO, fill=X)
        # print('packed CalcTypeFrame')

    def add_model_frames(self):
        """Add a submenu for selecting the exact calculation model,
        below CalcTypeFrame.

        The different submenus are all grid() into a parent Frame(
        model_frame), allowing only one to be displayed at a time (toggled
        between via the CalcTypeFrame radio buttons).

        Attributes created:
        model_frame: (Frame) 'houses' the different submenus.

        framedic: {(str): (RadioFrame)} matches the name of a calculation
        submenu to the submenu object.

        active_bar_dict: {(str): (Toolbar object)} Keeps track of what the
        active toolbar is for each calculation type.

        currentframe: (RadioFrame) Keeps track of the current selected
        Calculation Type submenu.

        currentbar: (Toolbar object) Keeps track of the current displayed
        toolbar.

        """
        # Quick hack to see if we can circumvent bug due to grid/pack mixing
        self.model_frame = Frame(self.SideFrame)
        self.model_frame.pack(side=TOP, anchor=N, expand=YES, fill=X)
        # default grid configures are zero, so next 2 lines unneccessary?
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.add_multiplet_buttons()
        self.add_abc_buttons()
        self.add_dnmr_buttons()
        self.add_custom_buttons()

        # framedic used by CalcTypeFrame to control individual frames
        self.framedic = {'multiplet': self.MultipletButtons,
                         'abc': self.ABC_Buttons,
                         'dnmr': self.DNMR_Buttons,
                         'custom': self.Custom}

        # active_bar_dict used to keep track of the active model in each
        # individual button menu.
        self.active_bar_dict = {'multiplet': self.ab,
                                'abc': self.spinbars[0],
                                'dnmr': self.TwoSpinBar,
                                'custom': self.ab}
        self.currentframe = 'multiplet'
        self.currentbar = self.ab
        self.currentbar.grid(sticky=W)

    def add_multiplet_buttons(self):
        """"Add a 'Multiplet' menu: 'canned' solutions for common spin systems.

        Attributes created:
            MultipletButtons: (RadioFrame) Menu for selecting model

            ab, ab2, abx, abx3, aaxx, firstorder, aabb: (Toolbar objects)
            Toolbar frames associated with each type of 'Multiplet' calculation.
        """
        multiplet_buttons = (('AB', lambda: self.select_toolbar(self.ab)),
                             ('AB2', lambda: self.select_toolbar(self.ab2)),
                             ('ABX', lambda: self.select_toolbar(self.abx)),
                             ('ABX3', lambda: self.select_toolbar(self.abx3)),
                             ("AA'XX'", lambda: self.select_toolbar(self.aaxx)),
                             ('1stOrd',
                              lambda: self.select_toolbar(self.firstorder)),
                             ("AA'BB'", lambda: self.select_toolbar(self.aabb)))
        self.MultipletButtons = RadioFrame(self.model_frame,
                                           buttons=multiplet_buttons,
                                           title='Multiplet')
        self.MultipletButtons.grid(row=0, column=0, sticky=N)

        bar_kwargs = {'parent': self.TopFrame, 'controller': self.controller}
        self.ab = AB_Bar(**bar_kwargs)
        self.ab2 = AB2_Bar(**bar_kwargs)
        self.abx = ABX_Bar(**bar_kwargs)
        self.abx3 = ABX3_Bar(**bar_kwargs)
        self.aaxx = AAXX_Bar(**bar_kwargs)
        self.firstorder = FirstOrder_Bar(**bar_kwargs)
        self.aabb = AABB_Bar(**bar_kwargs)

    def add_abc_buttons(self):
        """Add a menu for selecting the number of nuclei to perform a
        second-order calculation on, and its corresponding toolbar.

        Attribute created:
            ABC_Buttons: (RadioFrame) Menu for selecting number of nuclei for
            the QM model.
        """
        abc_buttons_list = [
            (str(spins),
             lambda spins=spins: self.select_toolbar(self.spinbars[spins - 2])
             ) for spins in self.spin_range]
        abc_buttons = tuple(abc_buttons_list)
        self.ABC_Buttons = RadioFrame(self.model_frame,
                                      # self.SideFrame,
                                      buttons=abc_buttons,
                                      title='Number of Spins')
        # self.ABC_Buttons.grid(row=0, column=0, sticky=N)

    def add_dnmr_buttons(self):
        """Add a 'DNMR' menu: models for DNMR line shape analysis.

        Attributes created:
            DNMR_Buttons: (RadioFrame) Menu for selecting the type of DNMR
            calculation.

            TwoSpinBar: (TwoSingletBar) Toolbar associated with the '2-spin'
            DNMR model.

            DNMR_AB_Bar: (DNMR_AB_Bar) Toolbar associated with the 'AB
            Coupled' DNMR model.
        """
        dnmr_buttons = (('2-spin',
                         lambda: self.select_toolbar(self.TwoSpinBar)),
                        ('AB Coupled',
                         lambda: self.select_toolbar(self.DNMR_AB_Bar)))
        self.DNMR_Buttons = RadioFrame(self.model_frame,
                                       buttons=dnmr_buttons,
                                       title='DNMR')

        bar_kwargs = {'parent': self.TopFrame, 'controller': self.controller}
        self.TwoSpinBar = DNMR_TwoSingletBar(**bar_kwargs)
        self.DNMR_AB_Bar = DNMR_AB_Bar(**bar_kwargs)

    def add_custom_buttons(self):
        """Add a label notification that custom models are not implemented
        yet.
        """
        self.Custom = Label(self.model_frame,
                            text='Custom models not implemented yet')

    def add_plot(self):
        """Create a Matplotlib figure, instantiate a MPLgraph canvas with it,
        pack the canvas, and add a "Clear" button at the bottom of the GUI."""
        # print('creating figure')
        self.figure = Figure(figsize=(5, 4), dpi=100)
        # print('creating canvas')
        self.canvas = MPLgraph(self.figure, self)
        # print('packing canvas')
        self.canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)
        # print('adding clear button')
        Button(self, text="clear", command=lambda: self.canvas.clear()).pack(
            side=BOTTOM)
        # print('finished add_plot')

    def select_calc_type(self, calc_type):
        """Checks if a new calculation tupe submenu has been selected,
        and if so displays it and updates the currentframe reference.
        """
        if calc_type != self.currentframe:
            self.framedic[self.currentframe].grid_remove()
            self.currentframe = calc_type
            self.framedic[self.currentframe].grid()
            # retrieve and select current active bar of frame
            self.select_toolbar(self.active_bar_dict[self.currentframe])

    def select_toolbar(self, toolbar):
        """Replaces the old toolbar with the new toolbar.

        :param toolbar: the toolbar to replace currentbar in the GUI.
        """
        self.currentbar.grid_remove()
        self.currentbar = toolbar
        self.currentbar.grid(sticky=W)
        # record current bar of currentframe:
        self.active_bar_dict[self.currentframe] = toolbar
        try:
            self.currentbar.request_plot()
        except ValueError:
            print('No model yet for this bar')

    # The methods below provide the interface to the controller

    # To avoid a circular reference, a call to the Controller cannot be made
    # until View is fully instantiated. Initializing the plot with a call to
    # Controller is postponed by placing it in the following function and
    # having the Controller call it when the View is ready.
    def initialize(self):
        """Initialize the plot canvas with the simulation for currentbar.

        To avoid a circular reference, this method is called by the
        Controller after it instantiates View."""
        self.currentbar.request_plot()

    def clear(self):
        """ Erase the matplotlib canvas."""
        self.canvas.clear()

    def plot(self, x, y):
        """Plot the model's results to the matplotlib canvas.

        Arguments:
            x, y: numpy linspaces of x and y coordinates
        """
        self.canvas.plot(x, y)


if __name__ == '__main__':
    # Create the main application window:
    from ReichDNMR.controller import controller

    root = Tk()
    root.title('ReichDNMR')  # working title only!
    Controller = controller.Controller(root)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

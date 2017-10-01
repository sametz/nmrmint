"""
The main GUI for ReichDNMR.
"""
from tkinter import *

import matplotlib
import numpy as np

from ReichDNMR.GUI.frames import RadioFrame
from ReichDNMR.GUI.toolbars import SecondOrderSpinBar

matplotlib.use("TkAgg")  # must be invoked before the imports below
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from matplotlib.figure import Figure


class MPLgraph(FigureCanvasTkAgg):
    def __init__(self, figure, master=None, **options):
        FigureCanvasTkAgg.__init__(self, figure, master, **options)
        self.f = figure
        self.add = figure.add_subplot(111)
        self.add.invert_xaxis()
        self.show()
        self.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self, master)
        self.toolbar.update()

    def plot(self, x, y):
        self.add.plot(x, y)
        # apparently .draw_idle() gives faster refresh than .draw()
        self.f.canvas.draw_idle()  # DRAW IS CRITICAL TO REFRESH

    def clear(self):
        self.add.clear()
        self.f.canvas.draw()


class View(Frame):
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
        self.add_abc_buttons()
        self.add_plot()

    def initialize_spinbars(self, **kwargs):
        self.spin_range = range(2, 9)  # hardcoded for only 2-8 spins
        self.spinbars = [SecondOrderSpinBar(self.TopFrame, n=spins,
                                            **kwargs)
                         for spins in self.spin_range]

        self.currentbar = self.spinbars[0]  # two spins default
        self.currentbar.grid(sticky=W)

    def add_abc_buttons(self):
        """Populates ModelFrame with a RadioFrame for selecting the number of
        nuclei and the corresponding toolbar.
        """
        abc_buttons_list = [
            (str(spins),
             lambda spins=spins: self.select_toolbar(self.spinbars[spins - 2])
             ) for spins in self.spin_range]
        abc_buttons = tuple(abc_buttons_list)
        self.ABC_Buttons = RadioFrame(self.SideFrame,
                                      buttons=abc_buttons,
                                      title='Number of Spins')
        self.ABC_Buttons.grid(row=0, column=0, sticky=N)

    def add_plot(self):
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = MPLgraph(self.figure, self)
        self.canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)
        Button(self, text="clear", command=lambda: self.canvas.clear()).pack(
            side=BOTTOM)

    def select_toolbar(self, toolbar):
        """When called by a RadioButton, hides the old toolbar, shows the new
        toolbar, and requests that the plot be refreshed."

        :param toolbar: the toolbar (nSpinBar or AB_Bar object) that was
        selected by the RadioButton
        """
        self.currentbar.grid_remove()
        self.currentbar = toolbar
        self.currentbar.grid(sticky=W)

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
        self.currentbar.request_plot()

    def clear(self):
        """ Erase the matplotlib canvas."""
        self.canvas.clear()

    def plot(self, x, y):
        """Plot the model's results to the matplotlib canvas.

        Arguments:
            x, y: numpy arrays of x and y coordinates
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

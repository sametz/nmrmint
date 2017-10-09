"""
The main GUI for ReichDNMR.
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
                                    SecondOrderSpinBar, DNMR_TwoSingletBar,
                                    DNMR_AB_Bar)


class MPLgraph(FigureCanvasTkAgg):
    def __init__(self, figure, master=None, **options):
        print('initializing MPLgraph super')
        FigureCanvasTkAgg.__init__(self, figure, master, **options)
        print('super initialized')
        self.f = figure
        print('figure associated with self.f')
        self.add = figure.add_subplot(111)
        print('called figure.add_subplot')
        self.add.invert_xaxis()
        print('inverted x axis')
        # line below used/worked in past...but is it really needed?
        # self.show()
        # print('showing MPLgraph')
        self.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        print('tk widget packed')
        self.toolbar = NavigationToolbar2TkAgg(self, master)
        print('created toolbar')
        self.toolbar.update()
        print('toolbar updated')
        print('MPLgraph initialized')

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
        self.add_calc_type_frame()
        print('returned from add_calc_type frame; ')
        self.add_model_frames()
        # print('adding abc buttons')
        # self.add_abc_buttons()
        print('returned from adding abc buttons')
        print('adding plot')
        self.add_plot()
        print('plot added')
        print('View initialization complete')

    def initialize_spinbars(self, **kwargs):
        self.spin_range = range(2, 9)  # hardcoded for only 2-8 spins
        self.spinbars = [SecondOrderSpinBar(self.TopFrame, n=spins,
                                            **kwargs)
                         for spins in self.spin_range]

    def add_calc_type_frame(self):
        print('add_calc_type_frame called')
        title = 'Calc Type'
        print('assigned title')
        buttons = (('Multiplet', lambda: self.select_calc_type('multiplet')),
                   ('ABC...', lambda: self.select_calc_type('abc')),
                   ('DNMR', lambda: self.select_calc_type('dnmr')),
                   ('Custom', lambda: self.select_calc_type('custom')))
        print('defined buttons')
        self.CalcTypeFrame = RadioFrame(self.SideFrame,
                                        buttons=buttons, title=title,
                                        relief=SUNKEN, borderwidth=1)
        print('instantiated CalcTypeFrame')
        self.CalcTypeFrame.pack(side=TOP, expand=NO, fill=X)
        print('packed CalcTypeFrame')

    def add_model_frames(self):
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
        """"'Multiplet' menu: 'canned' solutions for common spin systems"""
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
        """Populates ModelFrame with a RadioFrame for selecting the number of
        nuclei and the corresponding toolbar.
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
        """'DNMR': models for DNMR line shape analysis"""
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
        # Custom: not implemented yet. Placeholder follows
        self.Custom = Label(self.model_frame,
                            text='Custom models not implemented yet')

    def add_plot(self):
        print('creating figure')
        self.figure = Figure(figsize=(5, 4), dpi=100)
        print('creating canvas')
        self.canvas = MPLgraph(self.figure, self)
        print('packing canvas')
        self.canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)
        print('adding clear button')
        Button(self, text="clear", command=lambda: self.canvas.clear()).pack(
            side=BOTTOM)
        print('finished add_plot')

    def select_calc_type(self, calc_type):
        if calc_type != self.currentframe:
            self.framedic[self.currentframe].grid_remove()
            self.currentframe = calc_type
            self.framedic[self.currentframe].grid()
            # retrieve and select current active bar of frame
            self.select_toolbar(self.active_bar_dict[self.currentframe])

    def select_toolbar(self, toolbar):
        """When called by a RadioButton, hides the old toolbar, shows the new
        toolbar, and requests that the plot be refreshed."

        :param toolbar: the toolbar (nSpinBar or AB_Bar object) that was
        selected by the RadioButton
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

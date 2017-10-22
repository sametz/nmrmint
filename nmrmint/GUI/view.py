"""
Provides the View for the UW-DNMR Model-View-Controller.

Provides the following classes:
* MPLplot: Extension of FigureCanvasTkAgg that includes a matplotlib Figure
reference and methods for plotting data.

* View: an extension of tkinter Frame that provides the main GUI.
"""
from tkinter import *

import matplotlib
import numpy as np

matplotlib.use("TkAgg")  # must be invoked before the imports below
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from matplotlib.figure import Figure

from nmrmint.GUI.frames import RadioFrame
from nmrmint.windnmr_defaults import multiplet_bar_defaults
from nmrmint.GUI.toolbars import (FirstOrderBar,
                                  SecondOrderSpinBar)
from nmrmint.GUI.widgets import SimpleVariableBox
from nmrmint.GUI.mixintest import HorizontalEntryFrame


class MPLplot(FigureCanvasTkAgg):
    """The Canvas object for plotting simulated spectra.

    MPLgraph extends on FigureCanvasTkAgg by including a reference to a
    matplotlib Figure object, plus methods for plotting.

    Attributes:
        (TODO: probably should all be private; learn about private attributes)

    Methods:
        plot_current: plot data to the top axis (i.e. the spectrum affected
        by the current toolbar inputs)
        plot_total: plot data to the bottom axis (i.e. the summation spectrum)
        clear_all: clears both plots
        clear_current: clears the top plot
        clear_total: clears the bottom plot

    """
    def __init__(self, figure, master=None, **options):
        """Extend FigureCanvasTkAgg with a Matplotlib Figure object, then add
        and pack itself plus a toolbar into the parent.

        :param figure: a matplotlib.figure.Figure object
        """
        FigureCanvasTkAgg.__init__(self, figure, master, **options)
        self.total_data = np.array([])
        self.f = figure
        self.current_plot = figure.add_subplot(211)
        self.current_plot.invert_xaxis()
        self.total_plot = figure.add_subplot(212)
        self.total_plot.invert_xaxis()
        self.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self, master)
        self.toolbar.update()

    def plot_current(self, x, y):
        """Plot x, y data to the current_plot axis.

        :param x: (numpy linspace)
        :param y: (numpy linspace)
        """
        # for some reason axes were getting flipped after adding, so:
        self.current_plot.invert_xaxis()
        self.current_plot.plot(x, y, linewidth=1)
        self.f.canvas.draw_idle()  # DRAW IS CRITICAL TO REFRESH

    def plot_total(self, x, y):
        """Plot x, y data to the total_plot axis.

        :param x: (numpy linspace)
        :param y: (numpy linspace)
        """
        # for some reason total_plot axis gets flipped, so:
        self.total_plot.invert_xaxis()
        self.total_plot.plot(x, y, linewidth=1)
        self.f.canvas.draw_idle()

    def clear_all(self):
        """Clear all spectra plots."""
        self.current_plot.clear()
        self.total_plot.clear()
        self.f.canvas.draw_idle()

    def clear_current(self):
        """Clear the current spectrum plot"""
        self.current_plot.clear()
        self.f.canvas.draw_idle()

    def clear_total(self):
        """Clear the summation spectrum plot."""
        self.total_plot.clear()
        self.f.canvas.draw_idle()


class View(Frame):
    """Provides the GUI for nmrmint by extending a tkinter Frame.

    The view assumes the controller offers the following method:
        * update_current_plot
    The toolbars (in toolbars.py) must ensure that the data they send via
    request_refresh_current_plot is of the type required by the controller's
    update_current_plot.

    Attributes:
    active_bar_dict: {(str): (Toolbar object)} Keeps track of what the
    active toolbar is for each calculation type.

    Methods:
        initialize_first_order_bar, initialize_spinbars,
        initialize_dnmr_bars, add_calc_type_frame, add_model_frames,
        add_multiplet_buttons, add_abc_buttons, add_dnmr_buttons,
        add_custom_buttons, add_current_plot: used by __init__ to instantiate
        the GUI.

        select_calc_type: select the type of calculation to use (i.e
        first-order {'Multiplet'), second-order {'abc...'}, DNMR, or Custom).

        select_toolbar: Display the toolbar for the selected calculation
        along the top of the GUI.

        initialize: Call the controller to initialize the plot on the Canvas

        clear: Clear the Canvas
        plot: Plot data to the Canvas
    """

    def __init__(self, parent, controller, **options):
        """Create the framework for the GUI then fill it in.

        :param parent: the parent tkinter object
        :param controller: the Controller to this View."""
        Frame.__init__(self, parent, **options)
        self.controller = controller
        self.nuclei_number = 2
        self.spectrometer_frequency = 300  # MHz
        # sys.settrace(trace_calls)

        # currently for debugging purposes, initial/blank spectra will have a
        # "TMS" peak at 0 that integrates to 1H.
        self.blank_spectrum = [(0, 1)]
        self.history_past = []
        self.history_future = []

        self.SideFrame = Frame(self, relief=RIDGE, borderwidth=3)
        self.SideFrame.pack(side=LEFT, expand=NO, fill=Y)

        self.TopFrame = Frame(self, relief=RIDGE, borderwidth=1)
        self.TopFrame.pack(side=TOP, expand=NO, fill=X)

        self.initialize_first_order_bar()
        self.initialize_spinbars()
        self.add_calc_type_frame()
        self.add_nuclei_number_entry()
        self.add_spec_freq_entry()
        self.add_width_entry()
        self.add_clear_buttons()
        self.add_plots()
        self.add_history_buttons()

    def initialize_first_order_bar(self):
        """Instantiate the toolbar for first-order model."""
        bar_kwargs = {'parent': self.TopFrame,
                      'controller': self.request_refresh_current_plot,
                      'spec_freq': self.spectrometer_frequency}
        self.first_order_bar = FirstOrderBar(**bar_kwargs)

    def initialize_spinbars(self):
        """Instantiate all of the toolbars used for the 'ABC...' subset of
        calculations, and store references to them.

        Attributes created:
            spin_range: the number of spins the program will accomodate.
            spinbars: a list of SecondOrderSpinBar objects, one for each
            number of spins to simulate.
        """
        kwargs = {'controller': self.request_refresh_current_plot,
                  'realtime': True}
        self.spin_range = range(2, 9)  # hardcoded for only 2-8 spins
        self.spinbars = [SecondOrderSpinBar(self.TopFrame, n=spins, **kwargs)
                         for spins in self.spin_range]



    def add_calc_type_frame(self):
        """Add a menu for selecting the type of calculation to the upper left
        of the GUI.

        Attribute created:
            CalcTypeFrame: the RadioFrame being packed into the GUI.
        """
        title = 'Simulation'
        buttons = (('First-Order',
                    lambda: self.select_first_order()),
                   ('Second-Order',
                    lambda: self.select_second_order()))

        self.CalcTypeFrame = RadioFrame(self.SideFrame,
                                        buttons=buttons, title=title,
                                        relief=SUNKEN, borderwidth=1)
        self.CalcTypeFrame.pack(side=TOP, expand=NO, fill=X)

    def select_first_order(self):
        self.calc_type = 'first-order'
        self.select_toolbar(self.first_order_bar)
        for child in self.nuc_number_frame.winfo_children():
            child.configure(state='disable')

    def select_second_order(self):
        self.calc_type = 'second-order'
        self.select_toolbar(self.spinbars[self.nuclei_number - 2])
        for child in self.nuc_number_frame.winfo_children():
            child.configure(state='normal')

    def select_toolbar(self, toolbar):
        """Replaces the old toolbar with the new toolbar.

        :param toolbar: the toolbar to replace currentbar in the GUI.
        """
        self.currentbar.grid_remove()
        self.currentbar = toolbar
        self.currentbar.grid(sticky=W)
        # record current bar of currentframe:
        self.active_bar_dict[self.calc_type] = toolbar
        try:
            self.currentbar.request_plot()
        except ValueError:
            print('No model yet for this bar')

    # def select_calc_type(self, calc_type):
    #     """Checks if a new calculation tupe submenu has been selected,
    #     and if so displays it and updates the currentframe reference.
    #     """
    #     if calc_type != self.currentframe:
    #         self.frame_dict[self.currentframe].grid_remove()
    #         self.currentframe = calc_type
    #         self.frame_dict[self.currentframe].grid()
    #         # retrieve and select current active bar of frame
    #         self.select_toolbar(self.active_bar_dict[self.currentframe])

    def add_nuclei_number_entry(self):
        self.nuc_number_frame = HorizontalEntryFrame(
            parent=self.SideFrame,
            name='Number of nuclei:',
            value=self.nuclei_number,
            controller=self.set_nuc_number)
        self.nuc_number_frame.pack(side=TOP)
        for child in self.nuc_number_frame.winfo_children():
            child.configure(state='disable')

    def set_nuc_number(self):
        print('# nuclei was: ', self.nuclei_number)
        self.nuclei_number = self.nuc_number_frame.current_value
        print('# nuclei is now: ', self.nuclei_number)
        self.select_toolbar(self.spinbars[self.nuclei_number - 2])

    # def add_model_frames(self):
    #     """Add a submenu for selecting the exact calculation model,
    #     below CalcTypeFrame.
    #
    #     The different submenus are all grid() into a parent Frame(
    #     model_frame), allowing only one to be displayed at a time (toggled
    #     between via the CalcTypeFrame radio buttons).
    #
    #     Attributes created:
    #     model_frame: (Frame) 'houses' the different submenus.
    #
    #     frame_dict: {(str): (RadioFrame)} matches the name of a calculation
    #     submenu to the submenu object.
    #
    #     active_bar_dict: {(str): (Toolbar object)} Keeps track of what the
    #     active toolbar is for each calculation type.
    #
    #     currentframe: (RadioFrame) Keeps track of the current selected
    #     Calculation Type submenu.
    #
    #     currentbar: (Toolbar object) Keeps track of the current displayed
    #     toolbar.
    #
    #     """
    #     self.model_frame = Frame(self.SideFrame)
    #     self.model_frame.pack(side=TOP, anchor=N, expand=YES, fill=X)
    #
    #     self.add_multiplet_buttons()
    #     self.add_abc_buttons()
    #
    #     # frame_dict used by CalcTypeFrame to control individual frames
    #     self.frame_dict = {'multiplet': self.MultipletButtons,
    #                        'abc': self.ABC_Buttons}
    #
    #     # active_bar_dict used to keep track of the active model in each
    #     # individual button menu.
    #     self.active_bar_dict = {'multiplet': self.first_order_bar,
    #                             'abc': self.spinbars[0]}
    #     self.currentframe = 'multiplet'
    #     self.currentbar = self.first_order_bar
    #     self.currentbar.grid(sticky=W)
    #
    # def add_multiplet_buttons(self):
    #     """"Hacked out for now so there's an empty frame to swap in/out.
    #     Will be factored out.
    #     """
    #     self.MultipletButtons = Frame(self.model_frame)
    #     self.MultipletButtons.grid(row=0, column=0, sticky=N)
    #
    # def add_abc_buttons(self):
    #     """Add a menu for selecting the number of nuclei to perform a
    #     second-order calculation on, and its corresponding toolbar.
    #
    #     Attribute created:
    #         ABC_Buttons: (RadioFrame) Menu for selecting number of nuclei for
    #         the QM model.
    #     """
    #     abc_buttons_list = [
    #         (str(spins),
    #          lambda spins=spins: self.select_toolbar(self.spinbars[spins - 2])
    #          ) for spins in self.spin_range]
    #     abc_buttons = tuple(abc_buttons_list)
    #     self.ABC_Buttons = RadioFrame(self.model_frame,
    #                                   # self.SideFrame,
    #                                   buttons=abc_buttons,
    #                                   title='Number of Spins')

    def add_spec_freq_entry(self):
        """Add a labeled widget for entering spectrometer frequency.
        """
        self.spec_freq_widget = SimpleVariableBox(
            self.SideFrame,
            name='Spectrometer Frequency',
            controller=self.set_spec_freq,
            value=self.spectrometer_frequency,
            min=1)
        self.spec_freq_widget.pack(side=TOP)

    def set_spec_freq(self):
        """Set the spectrometer frequency."""
        self.spectrometer_frequency = self.spec_freq_widget.current_value
        self.currentbar.set_freq(self.spectrometer_frequency)
        self.request_refresh_total_plot(self.total_spectrum)

    def add_width_entry(self):
        """Add a labeled widget for entering desired peak width.

        Feature currently inactive.
        """
        self.peak_width = 0.5
        self.peak_width_widget = SimpleVariableBox(
            self.SideFrame,
            name='Peak Width',
            controller=self.set_peak_width,
            value=self.peak_width,
            min=0.01)
        self.peak_width_widget.pack(side=TOP)

    def set_peak_width(self):
        """Currently has no effect."""
        self.peak_width = self.peak_width_widget.current_value

    def add_clear_buttons(self):
        """Add separate buttons for clearing the top (current) and bottom
        (total) spectra.
        """
        top_clear = Button(self.SideFrame, text="Clear Current Spectrum",
                           command=lambda: self.clear_current())
        bottom_clear = Button(self.SideFrame, text="Clear Total Spectrum",
                              command=lambda: self.clear_total())
        top_clear.pack()
        bottom_clear.pack()

    def add_plots(self):
        """Add a MPLplot canvas to the GUI"""
        self.figure = Figure(figsize=(7, 5.6), dpi=100)  # original figsize 5, 4
        self.canvas = MPLplot(self.figure, self)
        self.canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)

    def add_history_buttons(self):
        """Add buttons to the GUI for moving forward/back in the total
        spectrum creation history.

        Change DUMP = True to include the DUMP HISTORY button for debugging.
        """
        DUMP = True
        history_frame = Frame(self)
        history_frame.pack(side=TOP)
        back = Button(history_frame, text='Back',
                      command=lambda: self.go_back())
        forward = Button(history_frame, text='Forward',
                         command=lambda: self.go_forward())
        back.pack(side=LEFT)
        forward.pack(side=RIGHT)

        # Dump button for debugging history
        if DUMP:
            dump_button = Button(self, text='DUMP HISTORY',
                                 command=lambda: self.dump_history())
            dump_button.pack(side=TOP)

    def go_back(self):
        """Step back one point in the total spectrum history and refresh the
        spectrum plot, or beep if already at beginning.
        """
        if len(self.history_past) > 1:
            self.history_future.append(self.history_past.pop())
            self.total_spectrum = self.history_past[-1]
        else:
            self.bell()
            return

        self.request_refresh_total_plot(self.total_spectrum)

    def go_forward(self):
        """Step forward one point in the total spectrum history and refresh the
        spectrum plot, or beep if already at end.
        """
        try:
            self.history_past.append(self.history_future.pop())
            self.total_spectrum = self.history_past[-1]
        except IndexError:
            self.bell()
            return

        self.request_refresh_total_plot(self.total_spectrum)

    #########################################################################
    # Methods below provide the interface to the controller
    #########################################################################

    # Interface from View to Controller:
    def request_refresh_current_plot(self, model, **data):
        """Intercept the toolbar's plot request, include the total spectrum,
        and request an update from the Controller

        :param model: (str) Name of the model to use for calculation.
        :param data: (dict) kwargs for the requested model calculation.
        """
        self.controller.update_current_plot(model, **data)

    def request_add_plot(self, model, **data):
        """Add the current (top) spectrum to the sum (bottom) spectrum.

        :param model: (str) Name of the model used for calculating the
        current (top) spectrum.
        :param data: (dict) kwargs for the requested model calculation.
        """
        self.controller.add_view_plots(model, self.total_spectrum, **data)

    def request_refresh_total_plot(self, spectrum, *w):
        """Request a plot of the total (summation, botttom) spectrum using
        the provided spectrum and optional line width.

        :param spectrum: ([(float, float)...] A list of (frequency,
        intensity) tuples.
        :param w: optional peak width at half height.
        """
        self.controller.update_total_plot(spectrum, *w)

    # Interface from Controller to View:

    # To avoid a circular reference, a call to the Controller cannot be made
    # until View is fully instantiated. Initializing the plot with a call to
    # Controller is postponed by placing it in the following function and
    # having the Controller call it when the View is ready.
    def initialize(self):
        """Initialize the plots.

        To avoid a circular reference, this method is called by the
        Controller after it instantiates View."""
        self.currentbar = self.first_order_bar
        self.currentbar.grid(sticky=W)
        self.active_bar_dict = {'first-order': self.first_order_bar,
                                'second-order': self.spinbars[0]}
        self.total_spectrum = self.blank_spectrum
        self.currentbar.request_plot()
        self.controller.update_total_plot(self.total_spectrum)
        self.history_past.append(self.total_spectrum[:])

    def update_total_spectrum(self, new_total_spectrum):
        """Set the current total spectrum, adding it to the history list of
        changes, and deleting the forward history.

        :param new_total_spectrum: ([(float, float)...] A list of (frequency,
        intensity) tuples."""
        self.total_spectrum = new_total_spectrum
        self.history_past.append(self.total_spectrum[:])
        self.history_future = []

    def clear(self):
        """Erase all plots."""
        self.canvas.clear_all()
        self.total_spectrum = self.blank_spectrum

    def clear_current(self):
        """Erase the current (top) spectrum plot."""
        self.canvas.clear_current()

    def clear_total(self):
        """Erase the total (bottom) spectrum plot."""
        self.total_spectrum = self.blank_spectrum
        self.canvas.clear_total()

    def plot_current(self, x, y):
        """Plot data to the current spectrum's axis (top).

        Arguments:
            x, y: numpy linspaces of x and y coordinates
        """
        self.canvas.plot_current(x, y)

    def plot_total(self, x, y):
        """Plot data to the total spectrum's axis (bottom).

        Arguments:
            x, y: numpy linspaces of x and y coordinates
        """
        self.canvas.plot_total(x, y)

    # debugging below
    def dump_history(self):
        print('Current past history contents:')
        print(self.history_past)
        print('Current future history contents:')
        print(self.history_future)
        print('Current total_spectrum:')
        print(self.total_spectrum)


# Debugging routines:
def trace_calls(frame, event, arg):
    if event != 'call':
        return
    co = frame.f_code
    func_name = co.co_name
    if func_name == 'write':
        # Ignore write() calls from print statements
        return
    func_line_no = frame.f_lineno
    func_filename = co.co_filename

    if "/Users/geoffreysametz/Google Drive/Programming/NMR code/nmrmint" not \
            in func_filename:
        return

    caller = frame.f_back
    caller_line_no = caller.f_lineno
    caller_filename = caller.f_code.co_filename
    print('Call to %s on line %s of %s from line %s of %s' %
          (func_name, func_line_no, func_filename,
           caller_line_no, caller_filename))
    return


if __name__ == '__main__':
    # Create the main application window:
    from nmrmint.controller import controller

    root = Tk()
    root.title('nmrmint')  # working title only!
    Controller = controller.Controller(root)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

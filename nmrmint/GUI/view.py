"""
Provides the View for the UW-DNMR Model-View-Controller.

Provides the following classes:
* MPLplot: Extension of FigureCanvasTkAgg that includes a matplotlib Figure
reference and methods for plotting data.

* View: an extension of tkinter Frame that provides the main GUI.
"""
from tkinter import *
from tkinter.filedialog import asksaveasfilename

import matplotlib
import numpy as np

matplotlib.use("TkAgg")  # must be invoked before the imports below
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from matplotlib.backends.backend_pdf import FigureCanvasPdf
from matplotlib.backends.backend_ps import FigureCanvasPS
from matplotlib.figure import Figure

from nmrmint.GUI.adapter import Adapter
from nmrmint.GUI.frames import RadioFrame
from nmrmint.windnmr_defaults import multiplet_bar_defaults
from nmrmint.GUI.history import Subspectrum, History
from nmrmint.GUI.toolbars import (FirstOrderBar,
                                  SecondOrderBar,
                                  SecondOrderSpinBar)
from nmrmint.GUI.widgets import (HorizontalRangeEntryFrame,
                                 HorizontalEntryFrame,
                                 SimpleVariableBox)

history = History()


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
        self.x_min = -1  # ppm
        self.x_max = 12  # ppm
        self.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2TkAgg(self, master)
        self.toolbar.update()

    def plot_current(self, x, y):
        """Plot x, y data to the current_plot axis.

        :param x: (numpy linspace)
        :param y: (numpy linspace)
        """
        # print('view.plot_current received x ', x.size, ' y ', y.size)
        # for some reason axes were getting flipped after adding, so:
        self.current_plot.invert_xaxis()
        self.set_current_window(x, y)
        self.current_plot.plot(x, y, linewidth=1)
        # self.f.canvas.draw_idle()  # DRAW IS CRITICAL TO REFRESH
        self.draw_idle()

    def plot_total(self, x, y):
        """Plot x, y data to the total_plot axis.

        :param x: (numpy linspace)
        :param y: (numpy linspace)
        """
        # for some reason total_plot axis gets flipped, so:
        # self.total_plot.invert_xaxis()
        self.total_plot.plot(x, y, linewidth=1)
        # self.total_plot.set_xlim(self.x_max, self.x_min)  # should flip x axis
        # # self.f.canvas.draw_idle()
        # self.draw_idle()
        self.update_total_plot_window()

    def update_total_plot_window(self, *x_limits):

        # TODO: initially tried x_min, x_max = *x_limits, but get
        # error "can't use starred expression here"--learn how this
        # should work.
        if x_limits:
            if len(x_limits) == 2:
                self.x_min = x_limits[0]
                self.x_max = x_limits[1]
            else:
                print('update_total_plot_window called with bad args')
        # self.x_min = x_min
        # self.x_max = x_max
        self.total_plot.set_xlim(self.x_max, self.x_min)  # should flip x axis
        self.draw_idle()

    def set_current_window(self, x, y):
        left = False
        right = False
        # print('x, y', type(x), len(x), type(y), len(y))
        # print('checking x order')
        # ordered = True
        # for i, x_ in enumerate(x[:-2]):
        #     if x[i + 1] < x_:
        #         # print('x stopped increasing at: ', i)
        #         ordered = False
        #         break
        # if ordered:
        #     print('x always increased, from ', x[0], 'to ', x[-1])

        start = True
        for i, y_ in enumerate(y[:-2]):

            if y[i + 1] < y_ and start is True:
                # print('y max found at: ', i, y_)
                start = False
            if y[i + 1] > y_:
                start = True

        for i, intensity in enumerate(y):
            if intensity > 0.01:
                left = i
                # print('found left = ', left)
                # print('intensity: ', intensity)
                break
        # if not left:
        # print('no left found')
        for j, intensity in enumerate(reversed(y)):
            if intensity > 0.01:
                right = j
                # print('found right = ', right)
                # print('intensity: ', intensity)
                break
        # if not right:
        # print('no right found')
        x_min = x[left] - 0.2
        x_max = x[-right] + 0.2
        # print('x window ', x_min, x_max)
        self.current_plot.set_xlim(x_max, x_min)  # should flip x axis
        self.draw_idle()

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

    # def total_figure(self):
    #     total_figure = Figure()
    #     total_plot = total_figure.add_subplot(111)
    #     line = self.total_plot.get_lines()[0]
    #     xd = line.get_xdata()
    #     yd = line.get_ydata()
    #     total_plot.plot(xd, yd, linewidth=1)
    #     return total_figure
    #
    # def save_pdf(self):
    #     figure = self.total_figure()
    #     # self.f.savefig('test.pdf')
    #     figure.savefig('test.pdf')

class View(Frame):
    """Provides the GUI for nmrmint by extending a tkinter Frame.

    The view assumes the controller offers the following methods:
        * update_current_plot
        * add_view_plots
        * update_total_plot

    The toolbars (in toolbars.py) must ensure that the data they send via
    request_refresh_current_plot is of the type required by the controller's
    update_current_plot.

    Attributes:
        nuclei_number: (int) the number of nuclei being modeled in the current
        second-order toolbar

        spectrometer_frequency: the (proton resonance) frequency for the
        simulated spectrometer.

        blank_spectrum: [(int, int)...] the spectrum to instantiate the total
        spectrum window with. [(0, 0)] if blank (baseline) spectrum.

        The following two stacks provide backward/forward navigation:
        history_past: [[(int, int)...]...] A list of spectra constituting the
        history of changes made to the total spectrum.
        history_future: [[(int, int)...]...] A list of spectra constituting
        the "forward in time" changes to the total spectrum.

        SideFrame: (tkinter.Frame) Holds the side toolbar of the GUI

        TopFrame: (tkinter.Frame) Holds the top (model) toolbars of the GUI

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
        :param controller: the Controller to this View.
        """
        Frame.__init__(self, parent, **options)

        # for debugging:
        # sys.settrace(trace_calls)

        self.controller = controller
        self.adapter = Adapter(view=self)  # could this be defined outside View?
        self.nuclei_number = 2
        self.spectrometer_frequency = 300  # MHz
        self.v_min = -1  # ppm
        self.v_max = 12  # ppm

        # Currently, for debugging purposes, initial/blank spectra will have a
        # "TMS" peak at 0 that integrates to 1H.
        self.blank_spectrum = [(0, 0.05)]
        self.history_past = []
        self.history_future = []

        self.SideFrame = Frame(self, relief=RIDGE, borderwidth=3)
        self.SideFrame.pack(side=LEFT, expand=NO, fill=Y)

        self.TopFrame = Frame(self, relief=RIDGE, borderwidth=1)
        self.TopFrame.pack(side=TOP, expand=NO, fill=X)

        self.SubSpectrumButtonFrame = Frame(self, relief=RIDGE, borderwidth=1)
        self.SubSpectrumButtonFrame.pack(side=TOP, expand=NO, fill=X)

        self.SubSpectrumSelectionFrame = Frame(self, relief=RIDGE,
                                               borderwidth=1)
        self.SubSpectrumSelectionFrame.pack(side=TOP, expand=NO, fill=X)

        self.initialize_first_order_bar()
        # self.initialize_spinbars()
        self.initialize_nospinbars()
        self.add_calc_type_frame()
        self.add_nuclei_number_entry()
        self.add_spec_freq_entry()
        self.add_minmax_entries()
        # Width sidebar setting currently has no effect
        # self.add_width_entry()
        self.add_clear_buttons()
        self.add_filesave_buttons()
        self.add_subspectrum_buttons()
        self.add_subspectrum_navigation()
        self.add_plots()
        self.add_history_buttons()

    def initialize_first_order_bar(self):
        """Instantiate the toolbar for first-order model."""
        bar_kwargs = {'parent': self.TopFrame,
                      # 'controller': self.request_refresh_current_plot,
                      'controller': self.update_current_plot,
                      # Bad to set spec_freq here? Will it change if
                      # self.spectrometer_frequency changes?
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
        kwargs = {'controller': self.update_current_plot,
                  'realtime': True}
        self.spin_range = range(2, 9)  # hardcoded for only 2-8 spins
        self.spinbars = [SecondOrderSpinBar(self.TopFrame, n=spins, **kwargs)
                         for spins in self.spin_range]

    def initialize_nospinbars(self):
        """Used to test parent SecondOrderBar instead of child
        SecondOrderSpinBar. Change view initialization to call this method
        instead of initialize_spinbars.
        """
        kwargs = {'controller': self.update_current_plot}
        self.spin_range = range(2, 9)  # hardcoded for only 2-8 spins
        self.spinbars = [SecondOrderBar(self.TopFrame, n=spins, **kwargs)
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
        """Select the first-order calculation toolbar and deactivate the
        second-order "number of nuclei" entry.
        """
        self.calc_type = 'first-order'
        # If switching subspectrum's toolbars, cancel any activity
        # if history.current_subspectrum().active:
        #     self.toggle_subspectrum()
        self.select_toolbar(self.first_order_bar)
        for child in self.nuc_number_frame.winfo_children():
            child.configure(state='disable')

    def select_second_order(self):
        """Select the second-order calculation toolbar corresponding to the
        current "number of nuclei" setting, and activate the "number of
        nuclei" entry.
        """
        self.calc_type = 'second-order'
        # If switching subspectrum's toolbars, cancel any activity
        # if history.current_subspectrum().active:
        #     self.toggle_subspectrum()
        self.select_toolbar(self.spinbars[self.nuclei_number - 2])
        for child in self.nuc_number_frame.winfo_children():
            child.configure(state='normal')

    def select_toolbar(self, toolbar, deactivate=True):
        """Replaces the old toolbar with the new toolbar.

        :param toolbar: the toolbar to replace currentbar in the GUI.
        :param deactivate: (Bool) should subspectrum activity be toggled?
        Default behavior is to deactivate ss and delete it from total
        spectrum when changing toolbars (i.e. when selecting the model for
        the subspectrum). deactivate=False would be used when switching
        between subspectra.

        Rethink: maybe default should be to maintain activity, and refresh
        total if active.
        """
        #

        self.currentbar.grid_remove()
        self.currentbar = toolbar  # redundant with history.toolbar?
        # history.change_toolbar(toolbar)  # postpone?
        self.currentbar.grid(sticky=W)
        # record current bar of currentframe:
        self.active_bar_dict[self.calc_type] = toolbar
        # self.currentbar.set_freq(self.spectrometer_frequency)  # remove?

        # try:
        #     self.currentbar.request_plot()
        # except ValueError:
        #     print('No model yet for this bar')
        history.change_toolbar(self.currentbar)
        self.update_current_plot()

    def add_nuclei_number_entry(self):
        """Add the "number of nuclei" entry to the GUI, and instantiate it as
        "disabled".
        """
        self.nuc_number_frame = HorizontalRangeEntryFrame(
            parent=self.SideFrame,
            name='Number of nuclei:',
            value=self.nuclei_number,
            controller=self.set_nuc_number)
        self.nuc_number_frame.pack(side=TOP)
        for child in self.nuc_number_frame.winfo_children():
            child.configure(state='disable')

    def set_nuc_number(self):
        """Sets the nuclei number based on the "number of nuclei" entry,
        and activates the corresponding toolbar.
        """
        self.nuclei_number = self.nuc_number_frame.current_value
        # nuclei_number[0] is the toolbar for 2 spins, 1 for 3, etc. so:
        self.select_toolbar(self.spinbars[self.nuclei_number - 2])

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
        # self.currentbar.set_freq(self.spectrometer_frequency)
        # self.request_refresh_total_plot(self.total_spectrum)
        history.update_frequency(self.spectrometer_frequency)
        self.update_all_spectra()

    def update_all_spectra(self):
        """Recompute all lineshape data, store in history, and refresh."""
        history.save()
        history.total_x, history.total_y = self.blank_total_spectrum()
        converter = self.adapter.convert_toolbar_data
        # subspectra_data = [data for data in history.all_spec_data()]
        subspectra_data = history.all_spec_data()
        print('view received: ', subspectra_data)
        # print('subspectra data: ', subspectra_data)
        print('testing all_spec_data')
        for model, vars_ in history.all_spec_data():
            print(model, vars_)
        model_inputs = [(model, converter(model, vars_))
                        for model, vars_ in history.all_spec_data()]
        print('model inputs', model_inputs)
        subspectra_lineshapes = [self.controller.lineshape_data(*input_)
                                 for input_ in model_inputs]
        print('subspectra lineshapes: ', subspectra_lineshapes)
        history.update_all_spectra(subspectra_lineshapes)
        x, y = history.current_lineshape()
        self.clear_current()
        self.plot_current(x, y)
        x_total, y_total = history.total_x, history.total_y
        self.clear_total()
        self.plot_total(x_total, y_total)

    def add_minmax_entries(self):
        """Add entries for minimum and maximum frequency to display"""
        # set View.v_min and .v_max to initial default values
        self.v_min_frame = HorizontalEntryFrame(
            parent=self.SideFrame,
            name='v min',
            value=self.v_min,
            controller=self.set_v_min)
        self.v_max_frame = HorizontalEntryFrame(
            parent=self.SideFrame,
            name='v max',
            value=self.v_max,
            controller=self.set_v_max)
        self.v_min_frame.pack(side=TOP)
        self.v_max_frame.pack(side=TOP)

    def set_v_min(self):
        print('vmin change detected')
        self.v_min = self.v_min_frame.current_value
        print('v_min now: ', self.v_min)
        print('v_max is: ', self.v_max)
        # TODO: add refresh of spectrum
        # self.update_spec_window()
        self.canvas.update_total_plot_window(self.v_min, self.v_max)

    def set_v_max(self):
        print('vmax change detected')
        self.v_max = self.v_max_frame.current_value
        print('v_min is: ', self.v_min)
        print('v_max is now: ', self.v_max)
        # TODO: add refresh of spectrum
        # self.update_spec_window()
        self.canvas.update_total_plot_window(self.v_min, self.v_max)

    # def update_spec_window(self):
    #     """Changes the range of the x axis (frequency) on the total spectrum.
    #
    #     This should probably be a canvas method, not a view method.
    #     Which one should "own" the v_min/v_max variables?
    #     """
    #     self.canvas.total_plot.set_xlim(self.v_max, self.v_min)
    #     self.canvas.draw_idle()

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

    def add_filesave_buttons(self):
        """Add buttons for saving the total spectrum as EPS or PDF."""
        save_eps_button = Button(self.SideFrame, text="Save as EPS",
                                 command=lambda: self.save_as_eps())
        save_pdf_button = Button(self.SideFrame, text="Save as PDF",
                                 command=lambda: self.save_as_pdf())
        save_eps_button.pack()
        save_pdf_button.pack()

    def total_plot_figure(self):
        """Return a Figure for the current total plot."""
        figure = Figure()
        axes = figure.add_subplot(111)
        x, y = history.total_x, history.total_y
        axes.plot(x, y, linewidth=0.3)
        axes.set_xlim(self.v_max, self.v_min)
        return figure

    def save_as_eps(self):
        print('Save as EPS!')
        backend = FigureCanvasPS(self.total_plot_figure())
        filename = asksaveasfilename()
        if filename:
            if filename[-4:] != '.eps':
                filename += '.eps'
            backend.print_eps(filename)

    def save_as_pdf(self):
        print('Save as PDF!')
        backend = FigureCanvasPdf(self.total_plot_figure())
        filename = asksaveasfilename()
        if filename:
            if filename[-4:] != '.pdf':
                filename += '.pdf'
            backend.print_pdf(filename)

    def add_subspectrum_buttons(self):
        """Add buttons for requesting: Add to Spectrum; Remove from Spectrum;
        New Subspectrum; Delete Subspectrum.
        """
        self.add_subspectrum_button = Button(
            self.SubSpectrumButtonFrame,
            text="Add to Spectrum",
            highlightbackground='red',
            command=lambda:
            self.toggle_subspectrum())
        # remove_subspectrum_button = Button(self.SubSpectrumButtonFrame,
        #                                    text="Remove from Spectrum",
        #                                    command=lambda:
        #                                    self.remove_subspectrum())

        new_subspectrum_button = Button(self.SubSpectrumButtonFrame,
                                        text="New Subspectrum",
                                        command=lambda: self.new_subspectrum())
        delete_subspectrum_button = Button(
            self.SubSpectrumButtonFrame,
            text="Delete Subspectrum",
            command=lambda: self.delete_subspectrum())
        self.add_subspectrum_button.pack(side=LEFT)
        # remove_subspectrum_button.pack(side=LEFT)
        new_subspectrum_button.pack(side=LEFT)
        delete_subspectrum_button.pack(side=LEFT)

    def toggle_subspectrum(self):
        # print(self.add_subspectrum_button['bg'])
        subspectrum_active = history.current_subspectrum().toggle_active()
        if subspectrum_active:
            # self.add_subspectrum_button['highlightbackground'] = 'green'
            self.set_active_button_color('green')
            history.add_current_to_total()
        else:
            # self.add_subspectrum_button['highlightbackground'] = 'red'
            self.add_subspectrum_button['highlightbackground'] = 'red'
            history.remove_current_from_total()
        self.clear_total()
        self.plot_total(history.total_x, history.total_y)

    def reset_active_button_color(self):
        subspectrum = history.current_subspectrum()
        if subspectrum.active:
            self.set_active_button_color('green')
        else:
            self.set_active_button_color('red')

    def set_active_button_color(self, color):
        """Set the 'Add to Spectrum' button's color.

        :param color: (str) the color to change the button's background to.
        """
        try:
            self.add_subspectrum_button['highlightbackground'] = color
        except Exception:
            print('color not recognized')

    def add_subspectrum(self):
        history.save_current_linshape(self.current_x, self.current_y)
        print('current_lineshape', self.current_x, self.current_y)
        history.add_current_to_total()

    def remove_subspectrum(self):
        history.remove_current_from_total()

    def new_subspectrum(self):
        # Refactored. Adding story comments to try to make process clear

        # Slightly hacky: here, we don't want the old toolbar to deactivate
        # regardless of its activate status. CalcTypeFrame.click() will
        # normally deactiate an active bar. Adding the new subspectrum first
        # will point the .click() to it, see it as default deactive, and not
        # take action.
        history.add_subspectrum()

        # Possible refactor: reset ***all*** toolbars? or just allow their
        # last state to remain?

        self.currentbar.restore_defaults()

        # Want to switch to default 1st order bar, and to change radio
        # button, so easy way is to:
        self.CalcTypeFrame.click(0)

        # Restore default toolbar values
        self.currentbar.restore_defaults()

        # update history and subspectrum with its status
        history.change_toolbar(self.currentbar)

        # Necessary? make sure active button is correct
        self.reset_active_button_color()

        # update label with subspectrum number
        self.subspectrum_label.config(text="Subspectrum "
                                           + str(history.current + 1))

        # refresh current subspectrum plot
        self.update_current_plot()

    def delete_subspectrum(self):
        print('Delete the current subspectrum!')
        if history.length() < 2:
            print('Not deleting...only 1 subspectrum left')
            return
        if history.current_subspectrum().active:
            history.remove_current_from_total()
        history.delete()
        self.subspectrum_label.config(text="Subspectrum "
                                           + str(history.current + 1))
        self.select_toolbar(history.current_toolbar(),
                            deactivate=False)
        # self.currentbar.reset(history.current_subspectrum().vars)
        self.update_current_plot()
        self.clear_total()
        self.plot_total(history.total_x, history.total_y)

    def add_subspectrum_navigation(self):
        subspectrum_back = Button(self.SubSpectrumSelectionFrame,
                                  text="<-",
                                  command=lambda: self.prev_subspectrum())
        self.subspectrum_label = Label(
            self.SubSpectrumSelectionFrame,
            text="Subspectrum " + str(history.current + 1))
        subspectrum_forward = Button(self.SubSpectrumSelectionFrame,
                                     text="->",
                                     command=lambda: self.next_subspectrum())
        subspectrum_back.pack(side=LEFT)
        self.subspectrum_label.pack(side=LEFT)
        subspectrum_forward.pack(side=LEFT)

    def next_subspectrum(self):
        if history.forward():
            self.subspectrum_label.config(text="Subspectrum "
                                               + str(history.current + 1))
            self.select_toolbar(history.current_toolbar(), deactivate=False)
            self.currentbar.reset(history.current_subspectrum().vars)
            self.update_current_plot()

    def prev_subspectrum(self):
        # history.dump()
        if history.back():
            self.subspectrum_label.config(text="Subspectrum "
                                               + str(history.current + 1))
            self.select_toolbar(history.current_toolbar(), deactivate=False)
            self.currentbar.reset(history.current_subspectrum().vars)
            self.update_current_plot()
        # history.dump()
        # assert history.subspectra[history.current] is not history.subspectra[
        #     history.current - 1]
        # assert 1 == 2

    def add_plots(self):
        """Add a MPLplot canvas to the GUI"""
        self.figure = Figure(figsize=(7, 5.6), dpi=100)  # original figsize 5, 4
        self.canvas = MPLplot(self.figure, self)
        # View should override Canvas' default xlim
        self.canvas.x_min = self.v_min
        self.canvas.x_max = self.v_max
        self.canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)

    def add_history_buttons(self):
        """Add buttons to the GUI for moving forward/back in the total
        spectrum creation history.

        Change DUMP = True to include the DUMP HISTORY button for debugging.
        """
        DUMP = False
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
    # TODO: rename these

    def blank_total_spectrum(self):
        """Request and return a new blank total spectrum.

        :return: (np.linspace, np.array) tuple of x, y- lineshape data
        """
        return self.controller.total_plot(self.blank_spectrum)

    def request_refresh_current_plot(self, model, **data):
        """Intercept the toolbar's plot request, include the total spectrum,
        and request an update from the Controller

        :param model: (str) Name of the model to use for calculation.
        :param data: (dict) kwargs for the requested model calculation.
        """
        print('request_refresh_current_plot received ', model, data)
        self.controller.update_current_plot(model, data)

    # def update_current_plot(self, model, vars):
    #     """Will become replacement for request_refresh_current_plot"""
    #     print('update_current_plot received ', model, vars)
    #     # history.update_vars(model, vars)
    #     history.change_toolbar(self.currentbar)
    #     data = self.adapter.convert_toolbar_data(model, vars)
    #     self.controller.update_current_plot(model, data)

    def update_current_plot(self):
        """Testing a refactor where plots get needed data directly from
        history."""
        active = history.current_subspectrum().active
        if active:
            history.remove_current_from_total()
        history.save()
        model, vars_ = history.subspectrum_data()
        print('update_current_plot received ', model, vars_)
        data = self.adapter.convert_toolbar_data(model, vars_)
        self.controller.update_current_plot(model, data)
        if active:
            history.add_current_to_total()
            self.clear_total()
            self.plot_total(history.total_x, history.total_y)

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
        self.total_spectrum = self.blank_spectrum  # TODO refactor redundancy
        history.change_toolbar(self.currentbar)
        self.currentbar.request_plot()
        self.controller.update_total_plot(self.total_spectrum)
        # self.history_past.append(self.total_spectrum[:])

        # test routines below (normally hashed out)

        # self.currentbar.test_reset({'Vcentr': 5.0})  # for test purposes

        # self.select_second_order()
        # testbar = self.currentbar
        # v, j, w = testbar.v, testbar.j, testbar.w_array
        # testbar.test_reset(v, j, w)

    # def start_history(self):
    #     # self.history = History()
    #     ss = self.record_subspectrum()
    #     history.add_subspectrum(ss)
    #     print('history initiated with subspectrum ', history.current,
    #           " containing vars ", history.subspectra[history.current].vars)

    # def record_subspectrum(self):
    #     subspectrum = Subspectrum(vars=self.currentbar.vars)
    #     return subspectrum

    # TODO: rename, e.g. update_history
    def update_total_spectrum(self, new_total_spectrum):
        """Set the current total spectrum, adding it to the history list of
        changes, and deleting the forward history.

        :param new_total_spectrum: ([(float, float)...] A list of (frequency,
        intensity) tuples.
        """
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
        # print('x, y: ', x, y)
        self.current_x, self.current_y = x, y
        # print('current_x, current_y: ', self.current_x, self.current_y)
        history.save_current_linshape(x, y)
        self.canvas.plot_current(x, y)

    def plot_total(self, x, y):
        """Plot data to the total spectrum's axis (bottom).

        Arguments:
            x, y: numpy linspaces of x and y coordinates
        """
        history.save_total_linshape(x, y)
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

# following is taken from PyMOTW: https://pymotw.com/2/sys/tracing.html
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

"""
Provides the View for the UW-DNMR Model-View-Controller.

Provides the following classes:
* MPLplot: Extension of FigureCanvasTkAgg that includes a matplotlib Figure
reference and methods for plotting data.

* View: an extension of tkinter Frame that provides the main GUI.
"""
from tkinter import *
# from tkinter.filedialog import asksaveasfilename

# import matplotlib
import numpy as np

# matplotlib.use("TkAgg")  # must be invoked before the imports below
# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
#                                                NavigationToolbar2TkAgg)
# from matplotlib.backends.backend_pdf import FigureCanvasPdf
# from matplotlib.backends.backend_ps import FigureCanvasPS
# from matplotlib.figure import Figure

# from nmrmint.GUI.adapter import Adapter
from nmrmint.GUI.backends import MPLplot, save_as_eps, save_as_pdf
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
        # self.adapter = Adapter(view=self)  # could this be defined outside View?
        self.nuclei_number = 2
        self.spectrometer_frequency = 300  # MHz
        self.v_min = -1  # ppm
        self.v_max = 12  # ppm
        # self.is_landscape = True

        # Initial/blank spectra will have a "TMS" peak at 0 that integrates
        # to 0.05 H.
        # self.blank_spectrum = [(0, 0.05)]

        self.SideFrame = Frame(self, relief=RIDGE, borderwidth=3)
        self.SideFrame.pack(side=LEFT, expand=NO, fill=Y)

        self.TopFrame = Frame(self, relief=RIDGE, borderwidth=1)
        self.TopFrame.pack(side=TOP, expand=NO, fill=X)

        self.SubSpectrumButtonFrame = Frame(self)  # ,
        # relief=RIDGE,  borderwidth=1)
        self.SubSpectrumButtonFrame.pack(side=TOP,
                                         expand=NO)
        # fill=X)

        # self.SubSpectrumSelectionFrame = Frame(self, relief=RIDGE,
        #                                        borderwidth=1)
        # self.SubSpectrumSelectionFrame.pack(side=TOP, expand=NO, fill=X)

        self.initialize_first_order_bar()

        # Depending on whether spin widgets are wanted or not, select one of
        # the next two lines:
        # self.initialize_spinbars()
        self.initialize_nospinbars()

        self.add_calc_type_frame()
        self.add_nuclei_number_entry()
        self.add_specfreq_frame()
        # self.add_spec_freq_entry()
        # self.add_minmax_entries()
        # Width sidebar setting currently has no effect
        # self.add_width_entry()
        # self.add_clear_buttons()
        self.add_filesave_frame()
        # self.add_filesave_buttons()
        # self.add_orientation_buttons()
        self.add_plot_dimensions()
        self.add_subspectrum_buttons()
        self.add_subspectrum_navigation()
        self.add_plots()
        self.initialize_active_bars()
        # self.add_history_buttons()

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

    def select_toolbar(self, toolbar):  # , deactivate=True):
        """Replaces the old toolbar with the new toolbar.

        :param toolbar: the toolbar to replace currentbar in the GUI.
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
            # parent=self.SideFrame,
            parent=self.CalcTypeFrame,
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
        # self.nuc_number_frame.set_value(self.nuclei_number)
        # nuclei_number[0] is the toolbar for 2 spins, 1 for 3, etc. so:
        self.select_toolbar(self.spinbars[self.nuclei_number - 2])

    def add_specfreq_frame(self):
        self.specfreq_frame = Frame(
            self.SideFrame,
            relief=RIDGE, borderwidth=1)
        self.specfreq_frame.pack(side=TOP, fill=X)
        self.add_spec_freq_entry()
        self.add_minmax_entries()

    def add_spec_freq_entry(self):
        """Add a labeled widget for entering spectrometer frequency.
        """
        self.spec_freq_widget = SimpleVariableBox(
            self.specfreq_frame,
            name='Spectrometer Frequency',
            controller=self.set_spec_freq,
            value=self.spectrometer_frequency,
            min_=1, )
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
        history.total_x, history.total_y = \
            self.controller.blank_total_spectrum()

        # converter = self.adapter.convert_toolbar_data
        # subspectra_data = [data for data in history.all_spec_data()]
        subspectra_data = history.all_spec_data()
        print('view received: ', subspectra_data)
        # print('subspectra data: ', subspectra_data)
        print('testing all_spec_data')
        for model, vars_ in history.all_spec_data():
            print(model, vars_)
        # model_inputs = [(model, converter(model, vars_))
        #                 for model, vars_ in history.all_spec_data()]
        # print('model inputs', model_inputs)
        subspectra_lineshapes = [self.controller.lineshape_data(model, vars_)
                                 for model, vars_ in subspectra_data]
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
            parent=self.specfreq_frame,
            name='v min',
            value=self.v_min,
            controller=self.set_v_min)
        self.v_max_frame = HorizontalEntryFrame(
            parent=self.specfreq_frame,
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
        self.canvas.set_total_plot_window(self.v_min, self.v_max)

    def set_v_max(self):
        print('vmax change detected')
        self.v_max = self.v_max_frame.current_value
        print('v_min is: ', self.v_min)
        print('v_max is now: ', self.v_max)
        # TODO: add refresh of spectrum
        # self.update_spec_window()
        self.canvas.set_total_plot_window(self.v_min, self.v_max)

    # def update_spec_window(self):
    #     """Changes the range of the x axis (frequency) on the total spectrum.
    #
    #     This should probably be a canvas method, not a view method.
    #     Which one should "own" the v_min/v_max variables?
    #     """
    #     self.canvas.total_plot.set_xlim(self.v_max, self.v_min)
    #     self.canvas.draw_idle()

    # def add_width_entry(self):
    #     """Add a labeled widget for entering desired peak width.
    #
    #     Feature currently inactive.
    #     """
    #     self.peak_width = 0.5
    #     self.peak_width_widget = SimpleVariableBox(
    #         self.SideFrame,
    #         name='Peak Width',
    #         controller=self.set_peak_width,
    #         value=self.peak_width,
    #         min=0.01)
    #     self.peak_width_widget.pack(side=TOP)
    #
    # def set_peak_width(self):
    #     """Currently has no effect."""
    #     self.peak_width = self.peak_width_widget.current_value
    #
    # def add_clear_buttons(self):
    #     """Add separate buttons for clearing the top (current) and bottom
    #     (total) spectra.
    #     """
    #     top_clear = Button(self.SideFrame, text="Clear Current Spectrum",
    #                        command=lambda: self.clear_current())
    #     bottom_clear = Button(self.SideFrame, text="Clear Total Spectrum",
    #                           command=lambda: self.clear_total())
    #     top_clear.pack()
    #     bottom_clear.pack()

    def add_filesave_frame(self):
        self.filesave_frame = Frame(
            self.SideFrame,
            relief=RIDGE, borderwidth=1)
        self.filesave_frame.pack(side=TOP, fill=X)
        self.add_filesave_buttons()
        self.add_orientation_buttons()

    def add_filesave_buttons(self):
        """Add buttons for saving the total spectrum as EPS or PDF."""
        save_eps_button = Button(self.filesave_frame, text="Save as EPS",
                                 command=lambda: self.save_as_eps())
        save_pdf_button = Button(self.filesave_frame, text="Save as PDF",
                                 command=lambda: self.save_as_pdf())
        save_pdf_button.pack()
        save_eps_button.pack()

    # coverage
    # def total_plot_figure(self):
    #     """Return a Figure for the current total plot."""
    #     figure = Figure(figsize=(self.plot_width, self.plot_height))
    #     axes = figure.add_subplot(111)
    #     x, y = history.total_x, history.total_y
    #     axes.plot(x, y, linewidth=0.3)
    #     axes.set_xlim(self.v_max, self.v_min)
    #     return figure

    def save_as_eps(self):
        if self.is_landscape:
            orientation = 'landscape'
        else:
            orientation = 'portrait'
        save_as_eps(x=history.total_x,
                    y=history.total_y,
                    xlim=(self.v_max, self.v_min),
                    figsize=(self.plot_width, self.plot_height),
                    orientation=orientation)
        # print('Save as EPS!')
        # backend = FigureCanvasPS(self._create_figure())

        # filename = asksaveasfilename()
        # if filename:
        #     if filename[-4:] != '.eps':
        #         filename += '.eps'
        #     backend.print_eps(filename, orientation=orientation)

    def save_as_pdf(self):
        save_as_pdf(x=history.total_x,
                    y=history.total_y,
                    xlim=(self.v_max, self.v_min),
                    figsize=(self.plot_width, self.plot_height))
        # print('Save as PDF!')
        # figure = self._create_figure()
        # backend = FigureCanvasPdf(figure)
        # if self.is_landscape:
        #     orientation = 'landscape'
        # else:
        #     orientation = 'portrait'
        # filename = asksaveasfilename()
        # if filename:
        #     if filename[-4:] != '.pdf':
        #         filename += '.pdf'
        #     backend.print_pdf(filename, orientation=orientation)
        # figure.savefig(filename, orientation=orientation)

    def add_orientation_buttons(self):
        title = 'EPS Orientation'
        buttons = (('Landscape',
                    lambda: self.set_orientation(True)),
                   ('Portrait',
                    lambda: self.set_orientation(False)))

        self.OrientationFrame = RadioFrame(self.filesave_frame,
                                           buttons=buttons, title=title,
                                           relief=RIDGE, borderwidth=0)
        self.OrientationFrame.pack(side=TOP, expand=NO, fill=X)
        self.OrientationFrame.click(0)

    def set_orientation(self, is_landscape):
        self.is_landscape = is_landscape
        print('is_landscape: ', is_landscape)

    def add_plot_dimensions(self):
        self.plot_width = 6.5
        self.plot_height = 2.5
        self.plot_width_entry = HorizontalEntryFrame(
            parent=self.SideFrame,
            name='Plot Width (inches)',
            value=self.plot_width,
            controller=self.set_plot_width)
        self.plot_height_entry = HorizontalEntryFrame(
            parent=self.SideFrame,
            name='Plot Height(inches)',
            value=self.plot_height,
            controller=self.set_plot_height)
        self.plot_width_entry.pack(side=TOP)
        self.plot_height_entry.pack(side=TOP)

    def set_plot_width(self):
        self.plot_width = self.plot_width_entry.current_value

    def set_plot_height(self):
        self.plot_height = self.plot_height_entry.current_value

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
        # self.add_subspectrum_button.pack(side=LEFT)
        # new_subspectrum_button.pack(side=LEFT)
        # delete_subspectrum_button.pack(side=LEFT)
        self.add_subspectrum_button.grid(row=1, column=0)
        new_subspectrum_button.grid(row=1, column=1)
        delete_subspectrum_button.grid(row=1, column=2)

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
        self.add_subspectrum_button['highlightbackground'] = color

    # coverage
    # def add_subspectrum(self):
    #     history.save_current_linshape(self.current_x, self.current_y)
    #     print('current_lineshape', self.current_x, self.current_y)
    #     history.add_current_to_total()

    # coverage
    # def remove_subspectrum(self):
    #     history.remove_current_from_total()

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
        self.select_toolbar(history.current_toolbar())  # , deactivate=False)
        # self.currentbar.reset(history.current_subspectrum().vars)
        self.update_current_plot()
        self.clear_total()
        self.plot_total(history.total_x, history.total_y)

    def add_subspectrum_navigation(self):
        subspectrum_back = Button(
            # self.SubSpectrumSelectionFrame,
            self.SubSpectrumButtonFrame,
            text="<-",
            command=lambda: self.prev_subspectrum())
        self.subspectrum_label = Label(
            self.SubSpectrumButtonFrame,
            text="Subspectrum " + str(history.current + 1))
        subspectrum_forward = Button(
            self.SubSpectrumButtonFrame,
            text="->",
            command=lambda: self.next_subspectrum())
        # subspectrum_back.pack(side=LEFT)
        # self.subspectrum_label.pack(side=LEFT)
        # subspectrum_forward.pack(side=LEFT)
        subspectrum_back.grid(row=0, column=0, sticky=E)
        self.subspectrum_label.grid(row=0, column=1)
        subspectrum_forward.grid(row=0, column=2, sticky=W)

    def next_subspectrum(self):
        history.dump()
        if history.forward():
            self.subspectrum_label.config(text="Subspectrum "
                                               + str(history.current + 1))
            self.update_nuclei_number()

            self.select_toolbar(history.current_toolbar())  # ,
            # deactivate=False)
            self.currentbar.reset(history.current_subspectrum().vars)
            self.update_current_plot()
            history.dump()

    def prev_subspectrum(self):
        history.dump()
        if history.back():
            self.subspectrum_label.config(text="Subspectrum "
                                               + str(history.current + 1))
            self.update_nuclei_number()
            # self.select_toolbar(history.current_toolbar())  # ,
            # deactivate=False)
            self.currentbar.reset(history.current_subspectrum().vars)
            self.update_current_plot()
            history.dump()
        # assert history.subspectra[history.current] is not history.subspectra[
        #     history.current - 1]
        # assert 1 == 2

    def update_nuclei_number(self):
        current_model, current_vars = history.subspectrum_data()
        if current_model == 'nspin':
            nspins = len(current_vars['v'][0])
            print('nspins is now: ', nspins)
            self.nuc_number_frame.set_value(nspins)
            self.set_nuc_number()
            self.CalcTypeFrame.click(1)
        else:
            self.CalcTypeFrame.click(0)


    # noinspection PyProtectedMember
    def add_plots(self):
        """Add a MPLplot canvas to the GUI"""
        # self.figure = Figure(figsize=(7, 5.6), dpi=100)  # original figsize 5, 4
        self.canvas = MPLplot(master=self)
        # View should override Canvas' default xlim
        self.canvas.x_min = self.v_min
        self.canvas.x_max = self.v_max
        self.canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)

    def initialize_active_bars(self):
        """Initialize the GUI and history with the default toolbars for first
       and second
       order.
       """
        self.currentbar = self.first_order_bar
        self.currentbar.grid(sticky=W)
        self.active_bar_dict = {'first-order': self.first_order_bar,
                                'second-order': self.spinbars[0]}
        history.change_toolbar(self.currentbar)

    #########################################################################
    # Methods below provide the interface to the controller
    #########################################################################

    # TODO: rename these

    # To avoid a circular reference, a call to the Controller cannot be made
    # until View is fully instantiated. Initializing the plot with a call to
    # Controller is postponed by placing it in the following function and
    # having the Controller call it when the View is ready.
    # def initialize(self):
    #     """Initialize the plots.
    #
    #     To avoid a circular reference, this method is called by the
    #     Controller after it instantiates View."""
    #     # self.currentbar = self.first_order_bar
    #     # self.currentbar.grid(sticky=W)
    #     # self.active_bar_dict = {'first-order': self.first_order_bar,
    #     #                         'second-order': self.spinbars[0]}
    #     # # self.total_spectrum = self.blank_spectrum  # TODO refactor redundancy
    #     # history.change_toolbar(self.currentbar)
    #     # TODO refactor toolbars so don't have to use their request.plot()
    #     # but call controller directly with the toolbar vars.
    #     # If this is done, entire issue with circular reference can be
    #     # eliminated and entire initialize function can be removed.
    #
    #     # self.update_current_plot()
    #
    #     # self.currentbar.request_plot()
    #     # TODO move to just in controller
    #     # self.controller.update_total_plot(self.controller.blank_spectrum)
    #     # self.history_past.append(self.total_spectrum[:])
    #
    #     # test routines below (normally hashed out)
    #
    #     # self.currentbar.test_reset({'Vcentr': 5.0})  # for test purposes
    #
    #     # self.select_second_order()
    #     # testbar = self.currentbar
    #     # v, j, w = testbar.v, testbar.j, testbar.w_array
    #     # testbar.test_reset(v, j, w)
    # def blank_total_spectrum(self):
    #     """Request and return a new blank total spectrum.
    #
    #     :return: (np.linspace, np.array) tuple of x, y- lineshape data
    #     """
    #     return self.controller.total_plot(self.blank_spectrum)

    # coverage
    # def request_refresh_current_plot(self, model, **data):
    #     """Intercept the toolbar's plot request, include the total spectrum,
    #     and request an update from the Controller
    #
    #     :param model: (str) Name of the model to use for calculation.
    #     :param data: (dict) kwargs for the requested model calculation.
    #     """
    #     print('request_refresh_current_plot received ', model, data)
    #     self.controller.update_current_plot(model, data)

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
        # Remove old current plot from total plot if necessary
        # TODO: maybe change to a Subspectrum.deactivate() method?
        active = history.current_subspectrum().active
        if active:
            history.remove_current_from_total()

        history.save()
        model, vars_ = history.subspectrum_data()
        print('update_current_plot received ', model, vars_)

        # data = self.adapter.convert_toolbar_data(model, vars_)
        self.controller.update_current_plot(model, vars_)
        if active:
            history.add_current_to_total()
            self.clear_total()
            self.plot_total(history.total_x, history.total_y)

    # coverage
    # def request_add_plot(self, model, **data):
    #     """Add the current (top) spectrum to the sum (bottom) spectrum.
    #
    #     :param model: (str) Name of the model used for calculating the
    #     current (top) spectrum.
    #     :param data: (dict) kwargs for the requested model calculation.
    #     """
    #     self.controller.add_view_plots(model, self.total_spectrum, **data)

    # coverage
    # def request_refresh_total_plot(self, spectrum, *w):
    #     """Request a plot of the total (summation, botttom) spectrum using
    #     the provided spectrum and optional line width.
    #
    #     :param spectrum: ([(float, float)...] A list of (frequency,
    #     intensity) tuples.
    #     :param w: optional peak width at half height.
    #     """
    #     self.controller.update_total_plot(spectrum, *w)

    # Interface from Controller to View:

    # def start_history(self):
    #     # self.history = History()
    #     ss = self.record_subspectrum()
    #     history.add_subspectrum(ss)
    #     print('history initiated with subspectrum ', history.current,
    #           " containing vars ", history.subspectra[history.current].vars)

    # def record_subspectrum(self):
    #     subspectrum = Subspectrum(vars=self.currentbar.vars)
    #     return subspectrum

    # coverage
    # TODO: rename, e.g. update_history
    # def update_total_spectrum(self, new_total_spectrum):
    #     """Set the current total spectrum, adding it to the history list of
    #     changes, and deleting the forward history.
    #
    #     :param new_total_spectrum: ([(float, float)...] A list of (frequency,
    #     intensity) tuples.
    #     """
    #     self.total_spectrum = new_total_spectrum
    #     self.history_past.append(self.total_spectrum[:])
    #     self.history_future = []

    # coverage
    # def clear(self):
    #     """Erase all plots."""
    #     self.canvas.clear_all()
    #     self.total_spectrum = self.blank_spectrum

    def clear_current(self):
        """Erase the current (top) spectrum plot."""
        self.canvas.clear_current()

    def clear_total(self):
        """Erase the total (bottom) spectrum plot."""
        # self.total_spectrum = self.blank_spectrum
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

    # coverage
    # debugging below
    # def dump_history(self):
    #     print('Current past history contents:')
    #     print(self.history_past)
    #     print('Current future history contents:')
    #     print(self.history_future)
    #     print('Current total_spectrum:')
    #     print(self.total_spectrum)


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

"""
Provides the View for the UW-DNMR Model-View-Controller.

Provides the following class:
* View: an extension of tkinter.Frame that provides the main GUI.
"""
from tkinter import *

from nmrmint.GUI.backends import MPLplot, save_as_eps, save_as_pdf
from nmrmint.GUI.frames import RadioFrame
from nmrmint.GUI.history import History
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
        * lineshape_data
        * blank_total_spectrum

    The View provides the following attributes:
        spectrometer_frequency: the (proton resonance) frequency for the
        simulated spectrometer.

    The View provides the following methods:
        * update_current_plot: recalculates the plots that depend on the
    current subspectrum parameters
        * clear_current: clears the canvas for the current (top) plot
        * plot_current: plots x, y data to the current (top) axes
        * clear_total: clears the canvas for the total (bottom) plot
        * plot_total: plots x, y data to the total (bottom) axes
    """

    def __init__(self, parent, controller, **options):
        """Create the framework for the GUI then fill it in.

        :param parent: the parent tkinter object
        :param controller: the Controller for this View.
        """
        Frame.__init__(self, parent, **options)

        # for debugging:
        # sys.settrace(trace_calls)

        self._controller = controller
        self._nuclei_number = 2
        self.spectrometer_frequency = 300  # MHz
        self._v_min = -1  # ppm
        self._v_max = 12  # ppm

        self._side_frame = Frame(self, relief=RIDGE, borderwidth=3)
        self._side_frame.pack(side=LEFT, expand=NO, fill=Y)
        self._top_frame = Frame(self, relief=RIDGE, borderwidth=1)
        self._top_frame.pack(side=TOP, expand=NO, fill=X)

        self._subspectrum_button_frame = Frame(self)
        self._subspectrum_button_frame.pack(side=TOP,
                                            expand=NO)

        self._initialize_first_order_bar()

        # Depending on whether spin widgets are wanted or not, select one of
        # the next two lines:
        # self._initialize_spinbars()
        self._initialize_nospinbars()

        self._add_calc_type_frame()
        self._add_nuclei_number_entry()
        self._add_specfreq_frame()
        self._add_filesave_frame()
        self._add_plot_dimensions()
        self._add_subspectrum_buttons()
        self._add_subspectrum_navigation()
        self._add_plots()
        self._initialize_active_bars()

    def _initialize_first_order_bar(self):
        """Instantiate the toolbar for first-order model."""
        bar_kwargs = {'parent': self._top_frame,
                      'controller': self.update_current_plot,
                      'spec_freq': self.spectrometer_frequency}
        self._first_order_bar = FirstOrderBar(**bar_kwargs)

    def _initialize_spinbars(self):
        """Instantiate all of the toolbars used for the 'nspin' second-order
        calculations, and store references to them.
        """
        kwargs = {'controller': self.update_current_plot,
                  'realtime': True}
        spin_range = range(2, 9)  # hardcoded for only 2-8 spins
        self._spinbars = [SecondOrderSpinBar(self._top_frame, n=spins, **kwargs)
                          for spins in spin_range]

    def _initialize_nospinbars(self):
        """Instantiate all of the toolbars used for the 'nspin' second-order
        calculations, and store references to them.
        """
        kwargs = {'controller': self.update_current_plot}
        spin_range = range(2, 9)  # hardcoded for only 2-8 spins
        self._spinbars = [SecondOrderBar(self._top_frame, n=spins, **kwargs)
                          for spins in spin_range]

    def _add_calc_type_frame(self):
        """Add a menu for selecting the type of calculation to the upper left
        of the GUI.
        """
        title = 'Simulation'
        buttons = (('First-Order',
                    lambda: self._select_first_order()),
                   ('Second-Order',
                    lambda: self._select_second_order()))

        self._calc_type_frame = RadioFrame(self._side_frame,
                                           buttons=buttons, title=title,
                                           relief=SUNKEN, borderwidth=1)
        self._calc_type_frame.pack(side=TOP, expand=NO, fill=X)

    def _select_first_order(self):
        """Select the first-order calculation toolbar and deactivate the
        second-order "number of nuclei" entry.
        """
        self._calc_type = 'first-order'
        self._select_toolbar(self._first_order_bar)
        for child in self._nuc_number_frame.winfo_children():
            child.configure(state='disable')

    def _select_second_order(self):
        """Select the second-order calculation toolbar corresponding to the
        current "number of nuclei" setting, and activate the "number of
        nuclei" entry.
        """
        self._calc_type = 'second-order'
        self._select_toolbar(self._spinbars[self._nuclei_number - 2])
        for child in self._nuc_number_frame.winfo_children():
            child.configure(state='normal')

    def _select_toolbar(self, toolbar):
        """Replaces the old toolbar with the new toolbar.

        :param toolbar: the toolbar to replace _currentbar in the GUI.
        """
        self._currentbar.grid_remove()
        self._currentbar = toolbar  # redundant with history.toolbar?
        self._currentbar.grid(sticky=W)
        # record current bar of currentframe:
        self._active_bar_dict[self._calc_type] = toolbar
        history.change_toolbar(self._currentbar)
        self.update_current_plot()

    def _add_nuclei_number_entry(self):
        """Add the "number of nuclei" entry to the GUI, and instantiate it as
        "disabled".
        """
        self._nuc_number_frame = HorizontalRangeEntryFrame(
            # parent=self._side_frame,
            parent=self._calc_type_frame,
            name='Number of nuclei:',
            value=self._nuclei_number,
            controller=self.set_nuc_number)
        self._nuc_number_frame.pack(side=TOP)
        for child in self._nuc_number_frame.winfo_children():
            child.configure(state='disable')

    def set_nuc_number(self):
        """Sets the nuclei number based on the "number of nuclei" entry,
        and activates the corresponding toolbar.
        """
        self._nuclei_number = self._nuc_number_frame.current_value
        # self._nuc_number_frame.set_value(self._nuclei_number)
        # _nuclei_number[0] is the toolbar for 2 spins, 1 for 3, etc. so:
        self._select_toolbar(self._spinbars[self._nuclei_number - 2])

    def _add_specfreq_frame(self):
        self.specfreq_frame = Frame(
            self._side_frame,
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
        # self._currentbar.set_freq(self.spectrometer_frequency)
        # self.request_refresh_total_plot(self.total_spectrum)
        history.update_frequency(self.spectrometer_frequency)
        self.update_all_spectra()

    def update_all_spectra(self):
        """Recompute all lineshape data, store in history, and refresh."""
        history.save()
        history.total_x, history.total_y = \
            self._controller.blank_total_spectrum()

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
        subspectra_lineshapes = [self._controller.lineshape_data(model, vars_)
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
        # set View._v_min and ._v_max to initial default values
        self.v_min_frame = HorizontalEntryFrame(
            parent=self.specfreq_frame,
            name='v min',
            value=self._v_min,
            controller=self.set_v_min)
        self.v_max_frame = HorizontalEntryFrame(
            parent=self.specfreq_frame,
            name='v max',
            value=self._v_max,
            controller=self.set_v_max)
        self.v_min_frame.pack(side=TOP)
        self.v_max_frame.pack(side=TOP)

    def set_v_min(self):
        print('vmin change detected')
        self._v_min = self.v_min_frame.current_value
        print('_v_min now: ', self._v_min)
        print('_v_max is: ', self._v_max)
        # TODO: add refresh of spectrum
        # self.update_spec_window()
        self.canvas.set_total_plot_window(self._v_min, self._v_max)

    def set_v_max(self):
        print('vmax change detected')
        self._v_max = self.v_max_frame.current_value
        print('_v_min is: ', self._v_min)
        print('_v_max is now: ', self._v_max)
        # TODO: add refresh of spectrum
        # self.update_spec_window()
        self.canvas.set_total_plot_window(self._v_min, self._v_max)

    # def update_spec_window(self):
    #     """Changes the range of the x axis (frequency) on the total spectrum.
    #
    #     This should probably be a canvas method, not a view method.
    #     Which one should "own" the _v_min/_v_max variables?
    #     """
    #     self.canvas.total_plot.set_xlim(self._v_max, self._v_min)
    #     self.canvas.draw_idle()

    # def add_width_entry(self):
    #     """Add a labeled widget for entering desired peak width.
    #
    #     Feature currently inactive.
    #     """
    #     self.peak_width = 0.5
    #     self.peak_width_widget = SimpleVariableBox(
    #         self._side_frame,
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
    #     top_clear = Button(self._side_frame, text="Clear Current Spectrum",
    #                        command=lambda: self.clear_current())
    #     bottom_clear = Button(self._side_frame, text="Clear Total Spectrum",
    #                           command=lambda: self.clear_total())
    #     top_clear.pack()
    #     bottom_clear.pack()

    def _add_filesave_frame(self):
        self.filesave_frame = Frame(
            self._side_frame,
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
    #     axes.set_xlim(self._v_max, self._v_min)
    #     return figure

    def save_as_eps(self):
        if self.is_landscape:
            orientation = 'landscape'
        else:
            orientation = 'portrait'
        save_as_eps(x=history.total_x,
                    y=history.total_y,
                    xlim=(self._v_max, self._v_min),
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
                    xlim=(self._v_max, self._v_min),
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

    def _add_plot_dimensions(self):
        self.plot_width = 6.5
        self.plot_height = 2.5
        self.plot_width_entry = HorizontalEntryFrame(
            parent=self._side_frame,
            name='Plot Width (inches)',
            value=self.plot_width,
            controller=self.set_plot_width)
        self.plot_height_entry = HorizontalEntryFrame(
            parent=self._side_frame,
            name='Plot Height(inches)',
            value=self.plot_height,
            controller=self.set_plot_height)
        self.plot_width_entry.pack(side=TOP)
        self.plot_height_entry.pack(side=TOP)

    def set_plot_width(self):
        self.plot_width = self.plot_width_entry.current_value

    def set_plot_height(self):
        self.plot_height = self.plot_height_entry.current_value

    def _add_subspectrum_buttons(self):
        """Add buttons for requesting: Add to Spectrum; Remove from Spectrum;
        New Subspectrum; Delete Subspectrum.
        """
        self.add_subspectrum_button = Button(
            self._subspectrum_button_frame,
            text="Add to Spectrum",
            highlightbackground='red',
            command=lambda:
            self.toggle_subspectrum())
        # remove_subspectrum_button = Button(self._subspectrum_button_frame,
        #                                    text="Remove from Spectrum",
        #                                    command=lambda:
        #                                    self.remove_subspectrum())

        new_subspectrum_button = Button(self._subspectrum_button_frame,
                                        text="New Subspectrum",
                                        command=lambda: self.new_subspectrum())
        delete_subspectrum_button = Button(
            self._subspectrum_button_frame,
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
        # regardless of its activate status. _calc_type_frame.click() will
        # normally deactiate an active bar. Adding the new subspectrum first
        # will point the .click() to it, see it as default deactive, and not
        # take action.
        history.add_subspectrum()

        # Possible refactor: reset ***all*** toolbars? or just allow their
        # last state to remain?

        self._currentbar.restore_defaults()

        # Want to switch to default 1st order bar, and to change radio
        # button, so easy way is to:
        self._calc_type_frame.click(0)

        # Restore default toolbar values
        self._currentbar.restore_defaults()

        # update history and subspectrum with its status
        history.change_toolbar(self._currentbar)

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
        self._select_toolbar(history.current_toolbar())  # , deactivate=False)
        # self._currentbar.reset(history.current_subspectrum().vars)
        self.update_current_plot()
        self.clear_total()
        self.plot_total(history.total_x, history.total_y)

    def _add_subspectrum_navigation(self):
        subspectrum_back = Button(
            # self.SubSpectrumSelectionFrame,
            self._subspectrum_button_frame,
            text="<-",
            command=lambda: self.prev_subspectrum())
        self.subspectrum_label = Label(
            self._subspectrum_button_frame,
            text="Subspectrum " + str(history.current + 1))
        subspectrum_forward = Button(
            self._subspectrum_button_frame,
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

            self._select_toolbar(history.current_toolbar())  # ,
            # deactivate=False)
            self._currentbar.reset(history.current_subspectrum().vars)
            self.update_current_plot()
            history.dump()

    def prev_subspectrum(self):
        history.dump()
        if history.back():
            self.subspectrum_label.config(text="Subspectrum "
                                               + str(history.current + 1))
            self.update_nuclei_number()
            # self._select_toolbar(history.current_toolbar())  # ,
            # deactivate=False)
            self._currentbar.reset(history.current_subspectrum().vars)
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
            self._nuc_number_frame.set_value(nspins)
            self.set_nuc_number()
            self._calc_type_frame.click(1)
        else:
            self._calc_type_frame.click(0)


    # noinspection PyProtectedMember
    def _add_plots(self):
        """Add a MPLplot canvas to the GUI"""
        # self.figure = Figure(figsize=(7, 5.6), dpi=100)  # original figsize 5, 4
        self.canvas = MPLplot(master=self)
        # View should override Canvas' default xlim
        self.canvas.x_min = self._v_min
        self.canvas.x_max = self._v_max
        self.canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)

    def _initialize_active_bars(self):
        """Initialize the GUI and history with the default toolbars for first
       and second
       order.
       """
        self._currentbar = self._first_order_bar
        self._currentbar.grid(sticky=W)
        self._active_bar_dict = {'first-order': self._first_order_bar,
                                'second-order': self._spinbars[0]}
        history.change_toolbar(self._currentbar)

    #########################################################################
    # Methods below provide the interface to the controller
    #########################################################################

    def update_current_plot(self):
        """Recalculates lineshapes that depend on the current subspectrum's
        values, and replots them.

        Also records the changes to history. TODO: bad code smell--function
        doing too many things. May be solved when history is refactored into
        Controller and out of View.
        """
        # Remove old current plot from total plot if necessary
        # TODO: maybe change to a Subspectrum.deactivate() method?
        active = history.current_subspectrum().active
        if active:
            history.remove_current_from_total()

        history.save()
        model, vars_ = history.subspectrum_data()
        self._controller.update_current_plot(model, vars_)
        if active:
            history.add_current_to_total()
            self.clear_total()
            self.plot_total(history.total_x, history.total_y)

    def clear_current(self):
        """Erase the current (top) spectrum plot."""
        self.canvas.clear_current()

    def plot_current(self, x, y):
        """Plot data to the current (top) spectrum's axis, and save the
        lineshapes to the history.

        Arguments:
            x, y: (numpy.ndarray, numpy.ndarray) x and y coordinates
        """
        self.current_x, self.current_y = x, y
        # print('current_x, current_y: ', self.current_x, self.current_y)
        history.save_current_linshape(x, y)
        self.canvas.plot_current(x, y)

    def clear_total(self):
        """Erase the total (bottom) spectrum plot."""
        # self.total_spectrum = self.blank_spectrum
        self.canvas.clear_total()

    def plot_total(self, x, y):
        """Plot data to the total (bottom) spectrum's axis.

        Arguments:
            x, y: numpy linspaces of x and y coordinates
        """
        history.save_total_linshape(x, y)
        self.canvas.plot_total(x, y)

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

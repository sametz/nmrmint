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
                      'callback': self.update_current_plot}
        self._first_order_bar = FirstOrderBar(**bar_kwargs)

    def _initialize_spinbars(self):
        """Instantiate all of the toolbars used for the 'nspin' second-order
        calculations, and store references to them.
        """
        kwargs = {'callback': self.update_current_plot,
                  'realtime': True}
        spin_range = range(2, 9)  # hardcoded for only 2-8 spins
        self._spinbars = [SecondOrderSpinBar(self._top_frame, n=spins, **kwargs)
                          for spins in spin_range]

    def _initialize_nospinbars(self):
        """Instantiate all of the toolbars used for the 'nspin' second-order
        calculations, and store references to them.
        """
        kwargs = {'callback': self.update_current_plot}
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
            parent=self._calc_type_frame,
            name='Number of nuclei:',
            value=self._nuclei_number,
            callback=self._set_nuc_number)
        self._nuc_number_frame.pack(side=TOP)
        for child in self._nuc_number_frame.winfo_children():
            child.configure(state='disable')

    def _set_nuc_number(self):
        """Set the nuclei number based on the "number of nuclei" entry,
        and activate the corresponding toolbar.
        """
        self._nuclei_number = self._nuc_number_frame.current_value
        # _nuclei_number[0] is the toolbar for 2 spins, 1 for 3, etc. so:
        self._select_toolbar(self._spinbars[self._nuclei_number - 2])

    def _add_specfreq_frame(self):
        """Add the entries for spectrometer frequency and min/max chemical
        shift range to the sidebar.
        """
        self._specfreq_frame = Frame(
            self._side_frame,
            relief=RIDGE, borderwidth=1)
        self._specfreq_frame.pack(side=TOP, fill=X)
        self._add_spec_freq_entry()
        self._add_minmax_entries()

    def _add_spec_freq_entry(self):
        """Add a labeled widget for entering spectrometer frequency.
        """
        self._spec_freq_widget = SimpleVariableBox(
            self._specfreq_frame,
            name='Spectrometer Frequency',
            callback=self._set_spec_freq,
            value=self.spectrometer_frequency,
            min_=1, )
        self._spec_freq_widget.pack(side=TOP)

    def _set_spec_freq(self):
        """Set the spectrometer frequency."""
        self.spectrometer_frequency = self._spec_freq_widget.current_value
        self._update_all_spectra()

    def _update_all_spectra(self):
        """Recompute all lineshape data, store in history, and refresh."""
        subspectra_lineshapes = [self._controller.lineshape_data(model, vars_)
                                 for model, vars_ in history.all_spec_data()]
        history.update_all_spectra(self._controller.blank_total_spectrum(),
                                   subspectra_lineshapes)

        self.clear_current()
        self.plot_current(*history.current_lineshape())
        self.clear_total()
        self.plot_total(*history.total_lineshape())

    def _add_minmax_entries(self):
        """Add entries for minimum and maximum frequency to display."""
        # set View._v_min and ._v_max to initial default values
        self._v_min_frame = HorizontalEntryFrame(
            parent=self._specfreq_frame,
            name='v min',
            value=self._v_min,
            callback=self._set_v_min)
        self._v_max_frame = HorizontalEntryFrame(
            parent=self._specfreq_frame,
            name='v max',
            value=self._v_max,
            callback=self._set_v_max)
        self._v_min_frame.pack(side=TOP)
        self._v_max_frame.pack(side=TOP)

    def _set_v_min(self):
        """Set the minimum ppm limit for the total plot."""
        self._v_min = self._v_min_frame.current_value
        self.canvas.set_total_plot_window(self._v_min, self._v_max)

    def _set_v_max(self):
        """Set the maximum ppm limit for the total plot."""
        self._v_max = self._v_max_frame.current_value
        self.canvas.set_total_plot_window(self._v_min, self._v_max)

    def _add_filesave_frame(self):
        """add widgets for exporting the total spectrum to the sidebar."""
        self.filesave_frame = Frame(
            self._side_frame,
            relief=RIDGE, borderwidth=1)
        self.filesave_frame.pack(side=TOP, fill=X)
        self._add_filesave_buttons()
        self._add_orientation_buttons()

    def _add_filesave_buttons(self):
        """Add buttons for saving the total spectrum as EPS or PDF."""
        save_eps_button = Button(self.filesave_frame, text="Save as EPS",
                                 command=lambda: self._save_as_eps())
        save_pdf_button = Button(self.filesave_frame, text="Save as PDF",
                                 command=lambda: self._save_as_pdf())
        save_pdf_button.pack()
        save_eps_button.pack()

    def _save_as_eps(self):
        """Save the total spectrum as an EPS file."""
        if self._is_landscape:
            orientation = 'landscape'
        else:
            orientation = 'portrait'
        save_as_eps(x=history.total_x,
                    y=history.total_y,
                    xlim=(self._v_max, self._v_min),
                    figsize=(self._plot_width, self._plot_height),
                    orientation=orientation)

    def _save_as_pdf(self):
        """Save the total spectrum as a PDF file."""
        save_as_pdf(x=history.total_x,
                    y=history.total_y,
                    xlim=(self._v_max, self._v_min),
                    figsize=(self._plot_width, self._plot_height))

    def _add_orientation_buttons(self):
        """Add buttons to select the EPS orientation."""
        # Seems that this feature isn't available for PDF in matplotlib?
        title = 'EPS Orientation'
        buttons = (('Landscape',
                    lambda: self._set_orientation(True)),
                   ('Portrait',
                    lambda: self._set_orientation(False)))

        self._orientation_frame = RadioFrame(self.filesave_frame,
                                             buttons=buttons, title=title,
                                             relief=RIDGE, borderwidth=0)
        self._orientation_frame.pack(side=TOP, expand=NO, fill=X)
        self._orientation_frame.click(0)

    def _set_orientation(self, is_landscape):
        """Callback for EPS orientation selection buttons.

        :param is_landscape: (bool)
        """
        self._is_landscape = is_landscape

    def _add_plot_dimensions(self):
        """Add widgets for entering dimensions in inches for exported plots."""
        self._plot_width = 6.5
        self._plot_height = 2.5
        self._plot_width_entry = HorizontalEntryFrame(
            parent=self._side_frame,
            name='Plot Width (inches)',
            value=self._plot_width,
            callback=self._set_plot_width)
        self._plot_height_entry = HorizontalEntryFrame(
            parent=self._side_frame,
            name='Plot Height(inches)',
            value=self._plot_height,
            callback=self._set_plot_height)
        self._plot_width_entry.pack(side=TOP)
        self._plot_height_entry.pack(side=TOP)

    def _set_plot_width(self):
        """Callback for plot width entry."""
        self._plot_width = self._plot_width_entry.current_value

    def _set_plot_height(self):
        """Callback for plot height entry."""
        self._plot_height = self._plot_height_entry.current_value

    def _add_subspectrum_buttons(self):
        """Add buttons for requesting: Add/Remove from Spectrum;
        New Subspectrum; Delete Subspectrum.
        """
        self._add_subspectrum_button = Button(
            self._subspectrum_button_frame,
            text="Add to Spectrum",
            highlightbackground='red',
            command=lambda: self._toggle_subspectrum())
        new_subspectrum_button = Button(self._subspectrum_button_frame,
                                        text="New Subspectrum",
                                        command=lambda: self._new_subspectrum())
        delete_subspectrum_button = Button(
            self._subspectrum_button_frame,
            text="Delete Subspectrum",
            command=lambda: self._delete_subspectrum())

        self._add_subspectrum_button.grid(row=1, column=0)
        new_subspectrum_button.grid(row=1, column=1)
        delete_subspectrum_button.grid(row=1, column=2)

    def _toggle_subspectrum(self):
        """Toggle whether the current subspectrum plot is added to the total
        spectrum or not.

        Callback for the "Add to Spectrum" button. """
        subspectrum_active = history.current_subspectrum().toggle_active()
        if subspectrum_active:
            self._set_active_button_color('green')
            history.add_current_to_total()
        else:
            self._add_subspectrum_button['highlightbackground'] = 'red'
            history.remove_current_from_total()

        self.clear_total()
        self.plot_total(*history.total_lineshape())

    def _reset_active_button_color(self):
        """Set the color of the "Add to Spectrum" button according to the
        current subspectrum's activity.

        Used when resetting the GUI after switching subspectra.
        """
        if history.current_subspectrum().active:
            self._set_active_button_color('green')
        else:
            self._set_active_button_color('red')

    def _set_active_button_color(self, color):
        """Set the 'Add to Spectrum' button's color.

        :param color: (str) the color to change the button's background to.
        """
        # Mac doesn't allow changing the button color itself, so using the
        # background color to indicate activity.
        self._add_subspectrum_button['highlightbackground'] = color

    def _new_subspectrum(self):
        """Add a new subspectrum and set it and GUI to default first-order."""
        # Refactored. Adding story comments to try to make process clear
        # TODO: this method is very low-level/granular. Refactor View and
        # History to make more clear?

        # Slightly hacky: here, we don't want the old toolbar to deactivate
        # regardless of its activate status. _calc_type_frame.click() will
        # normally deactiate an active bar. Adding the new subspectrum first
        # will point the .click() to it, see it as default deactive, and not
        # take action.
        history.add_subspectrum()

        # Reset current toolbar to default settings before leaving it
        self._currentbar.restore_defaults()

        # TODO: _update_simulation_frame (via _refresh_GUI_widgets) also does
        #  a click. Refactor out?
        # Want to switch to default 1st order bar, and to change radio
        # button, so easy way is to:
        self._calc_type_frame.click(0)

        # update history and subspectrum with its status
        history.change_toolbar(self._currentbar)

        self._refresh_current_GUI()

    def _refresh_current_GUI(self):
        """Refresh GUI widgets and current subspectrum plot to match current
        subspectrum."""
        self._refresh_GUI_widgets()
        self.update_current_plot()

    def _refresh_GUI_widgets(self):
        """Refresh GUI widgets to agree with a change of subspectrum."""
        self._reset_active_button_color()
        self._subspectrum_label.config(text="Subspectrum "
                                            + str(history.current + 1))
        self._update_simulation_frame()

    def _update_simulation_frame(self):
        """Reset the simulation frame widgets to match the current toolbar."""
        current_model, current_vars = history.subspectrum_data()
        if current_model == 'nspin':
            nspins = len(current_vars['v'][0])
            self._nuc_number_frame.set_value(nspins)
            self._set_nuc_number()
            self._calc_type_frame.click(1)
        else:
            self._calc_type_frame.click(0)

    def _delete_subspectrum(self):
        """Delete the current subspectrum object.

        See History.delete() for default behavior for reset of subspectrum
        after deletion.
        """
        if history.delete():
            self._refresh_current_GUI()
            self.clear_total()
            self.plot_total(*history.total_lineshape())

    def _add_subspectrum_navigation(self):
        """Add subspectrum navigation tools to the GUI."""
        subspectrum_back = Button(
            self._subspectrum_button_frame,
            text="<-",
            command=lambda: self._prev_subspectrum())
        self._subspectrum_label = Label(
            self._subspectrum_button_frame,
            text="Subspectrum " + str(history.current + 1))
        subspectrum_forward = Button(
            self._subspectrum_button_frame,
            text="->",
            command=lambda: self._next_subspectrum())
        subspectrum_back.grid(row=0, column=0, sticky=E)
        self._subspectrum_label.grid(row=0, column=1)
        subspectrum_forward.grid(row=0, column=2, sticky=W)

    def _next_subspectrum(self):
        """Advance in the history, if possible, and refresh the GUI."""
        if history.forward():
            self._refresh_current_GUI()

    def _prev_subspectrum(self):
        """Backtrack in the history, if possible, and refresh the GUI."""
        if history.back():
            self._refresh_current_GUI()

    # noinspection PyProtectedMember
    def _add_plots(self):
        """Add a MPLplot canvas to the GUI"""
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
            self.plot_total(*history.total_lineshape())

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
        history.save_current_lineshape(x, y)
        self.canvas.plot_current(x, y)

    def clear_total(self):
        """Erase the total (bottom) spectrum plot."""
        self.canvas.clear_total()

    def plot_total(self, x, y):
        """Plot data to the total (bottom) spectrum's axis.

        Arguments:
            x, y: (numpy.ndarray, numpy.ndarray) x and y coordinates
        """
        history.save_total_lineshape(x, y)
        self.canvas.plot_total(x, y)

# Debugging routines:

# following is taken from PyMOTW: https://pymotw.com/2/sys/tracing.html


def trace_calls(frame, event, arg):
    if arg:
        print('arg passed to trace_calls')  # need to recheck why arg is needed
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

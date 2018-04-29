"""Custom tkinter frames that hold multiple widgets plus capabilities to
store data and send it to a controller.

Provides the following classes:
* ToolBar: A base class for creating toolbars, intended to be subclassed and
extended.

* AB_Bar, AB2_Bar, ABX_Bar, ABX3_Bar, AAXX_Bar, AABB_Bar: hold numerical inputs
required for simulating AB, AB2, ABX, ABX3, AA'XX', and AA'BB' spin systems.

* FirstOrder_Bar: holds numerical inputs required for first-order simulation

* SecondOrderBar: holds numerical inputs, plus a button with a pop-up 2D
array for entering chemical shifts and J coupling constants, for second-order
simulations of up to 8 coupled spins.

* DNMR_TwoSingletBar: holds "custom SpinBox" numerical inputs for the
simulation of a DNMR lineshape for two uncoupled spins.

* DNMR_AB: holds "custom spinbox" numerical inputs for the simulation of a
DNMR lineshape for two coupled spins (AB quartet at the slow exchange limit).

TODO:
* Many of these classes for 'Multiplet' non-QM calculations can be reduced to
a single class, with the exact widget layouts specified by a dict argument.
* DNMR bar code can be simplified
"""

import copy

from tkinter import *

import numpy as np

from nmrmint.GUI.widgets import (ArrayBox, ArraySpinBox, VarBox, IntBox,
                                 VarButtonBox)
from nmrmint.initialize import getWINDNMRdefault


class ToolBar(Frame):
    """Extend tkinter.Frame with a controller reference, a model
    name, and a function to call the controller.

    Intended to be subclassed, and not instantiated itself.

    methods:
        request_plot: sends model type and data to the controller. Assumes
        controller has an update_current_plot function.
        add_spectra: adds the spectrum the ToolBar is currently modeling to
        the total spectrum.

    Attributes:
        controller: the Controller object of the Model-View-Controller
        architecture.
        model (str): the type of calculation requested (interpreted by the
        controller). To be overwritten by subclass.
        vars (dict): holds the kwargs that the controller is called with.
        Intent is that child widgets will store and update their data to this
        dict. Intended to be overwritten by subclass.
    """

    def __init__(self, parent=None, controller=None, **options):
        """Initialize the ToolBar object with a reference to a controller.

        Keyword arguments:
        :param parent: the parent tkinter object
        :param controller: the Controller object of the MVC application
        :param options: standard optional kwargs for a tkinter Frame
        """
        Frame.__init__(self, parent, **options)
        self.controller = controller
        self.model = 'model'  # must be overwritten by subclasses
        self.defaults = {}  # overwrite for subclasses
        self.vars = {}
        self.add_spectra_button = Button(self,
                                         name='addbutton',
                                         text='Add To Total',
                                         command=lambda: self.add_spectra())
        self.add_spectra_button.pack(side=RIGHT)
        # for testing:
        self.reset_button = Button(self,
                                   name='reset_button',
                                   text='Reset',
                                   command=lambda: self.restore_defaults())
        self.reset_button.pack(side=RIGHT)

    def request_plot(self):
        """Send request to controller to recalculate and refresh the view's
        plot.
        """
        # self.controller.update_current_plot(self.model, **self.vars)
        self.controller(self.model, **self.vars)

    def add_spectra(self):
        """Send request to controller to add the current spectrum to the
        total spectrum.
        """
        self.master.master.request_add_plot(self.model, **self.vars)

    def restore_defaults(self):
        self.reset(self.defaults)

    def reset(self, vars):
        pass


class FirstOrderBar(ToolBar):
    """A subclass of ToolBar designed for use with first-order (single-signal)
    simulations.

    Extends ToolBar with the following attributes:
        spec_freq: (float) the simulated spectrometer frequency.

    Extends ToolBar with the following methods:
        set_freq(freq: float): sets attribute spec_freq and update the
        current spectrum accordingly.
        make_kwargs: converts toolbar data to appropriate kwargs for calling
        the controller. Includes conversion from ppm to Hz.

    Overrides the following methods, to make use of make_kwargs:
        request_plot
        add_spectra
    """

    def __init__(self, parent=None, spec_freq=300, **options):
        """Instantiate the ToolBar with appropriate widgets for first-order
        calculations.

        :param spec_freq: the frequency of the simulated spectrometer.
        """
        ToolBar.__init__(self, parent, **options)
        self.spec_freq = spec_freq
        self.model = 'first_order'
        self.defaults = {'JAX': 7.00,
                         '#A': 2,
                         'JBX': 3.00,
                         '#B': 1,
                         'JCX': 2.00,
                         '#C': 0,
                         'JDX': 7,
                         '#D': 0,
                         'Vcentr': 150 / self.spec_freq,
                         '# of nuclei': 1,
                         'width': 0.5}
        self.vars = self.defaults.copy()
        self.fields = {}
        kwargs = {'dict_': self.vars,
                  'controller': self.request_plot}
        for key in ['# of nuclei', 'JAX', '#A', 'JBX', '#B', 'JCX', '#C',
                    'JDX', '#D', 'Vcentr', 'width']:
            if '#' not in key:
                widget = VarBox(self, name=key, **kwargs)
            else:
                widget = IntBox(self, name=key, **kwargs)
            self.fields[key] = widget
            widget.pack(side=LEFT)

        # self.test_reset(self.vars)

    def reset(self, vars):
        for key, val in vars.items():
            self.vars[key] = val
            widget = self.fields[key]
            widget.set_value(val)

        # self.vars = copy.deepcopy(vars)
        # for key, val in self.vars.items():
        #     widget = self.fields[key]
        #     widget.set_value(val)

    def test_reset(self, vars):
        for key, val in vars.items():
            self.vars[key] = val
            widget = self.fields[key]
            print('found ', key, 'with value ',
                  widget.get_value())
            widget.set_value(val)
            print('changed it to: ', widget.get_value())

        # self.request_plot()
        # res = self.nametowidget("width")
        # print(res, res.value_var.get())
        # widgets = self.children
        # for widget in widgets:
        #     print(widget)
        #     try:
        #         print(self.nametowidget('addbutton'))
        #     except:
        #         print('FAIL')
        # for key, val in vars.items():
        #     name = ".!view.!frame2.!firstorderbar." + key
        #     try:
        #         print(self.nametowidget(name))
        #     except:
        #         print('FAIL')

    def set_freq(self, freq):
        """Set the simulated spectrometer frequency and update the current
        plot accordingly.

        :param freq: (float) the frequency of the spectrometer to simulate.
        """
        self.spec_freq = freq
        self.request_plot()

    def request_plot(self):
        """Request the Controller to plot the spectrum."""
        # kwargs = self.make_kwargs()
        # print('request: ', kwargs)
        # self.controller(self.model, **kwargs)
        self.controller(self.model, self.vars)

    # def make_kwargs(self):
    #     """Convert the dictionary of widget entries (self.vars) to a dict
    #     that is compliant with the controller interface.
    #
    #     The controller needs to pass a (signal, couplings) tuple to the model.
    #     - signal is a (frequency, intensity) tuple representing the frequency
    #     and intensity of the signal in the absence of coupling. Intensity is
    #     1 by default.
    #     - couplings is a list of (J, n) tuples, where J is the coupling
    #     constant and n is the number of nuclei coupled to the nucleus of
    #     interest with that same J value.
    #     """
    #     _Jax = self.vars['JAX']
    #     _a = self.vars['#A']
    #     _Jbx = self.vars['JBX']
    #     _b = self.vars['#B']
    #     _Jcx = self.vars['JCX']
    #     _c = self.vars['#C']
    #     _Jdx = self.vars['JDX']
    #     _d = self.vars['#D']
    #     _Vcentr = self.vars['Vcentr'] * self.spec_freq
    #     _integration = self.vars['# of nuclei']
    #     singlet = (_Vcentr, _integration)
    #     allcouplings = [(_Jax, _a), (_Jbx, _b), (_Jcx, _c), (_Jdx, _d)]
    #     couplings = [coupling for coupling in allcouplings if coupling[1] != 0]
    #     data = {'signal': singlet,
    #             'couplings': couplings}
    #     return data

    def add_spectra(self):
        """Add the (top) current spectrum simulation to the (bottom) total
        simulated spectrum plot.
        """
        kwargs = self.make_kwargs()
        self.master.master.request_add_plot(self.model, **kwargs)


class SecondOrderBar(ToolBar):
    """
    Extends Frame to hold n frequency entry boxes, an entry box for peak
    width (default 0.5 Hz), a 2-D numpy array for frequencies (see below),
    a 2-D numpy array for coupling constants, and a button to pop up a window
    for entering J values as well as frequencies.

    The ArrayBox and ArraySpinBox widgets currently handle 2-D arrays only,
    so the frequencies only occupy the first row of a 1-row 2-dimensional
    array (self.v), and the peak widths the first column of the first row of a
    1-cell 2-D array (self.w). i.e. self.v[0, :] provides a 1-D numpy array
    of the frequencies, and self.v[0, 0] provides the peak width.

    Methods:
        * add_frequency_widgets, add_peakwidth_widget, add_J_button,
        add_addspectra_button: add the required widgets to the toolbar. Only
        intented to be called by __init__. TODO: review all code and learn
        appropriate use of private methods to refactor.
        * vj_popup: opens a window for the entry of J values as well as
        frequencies.
        * set_freq(freq: float): sets attribute spec_freq and update the
        current spectrum accordingly.
        * update_v: converts the current ppm values (v_ppm) to Hz and
        overwrites v with them (provides interface between the ppm-using
        toolbar and the Hz-using controller/model)
        * request_plot: sends model type and data to the controller
        * add_spectra: adds the spectrum the ToolBar is currently modeling to
        the total spectrum.

    Attributes:
        * controller: the Controller object of the Model-View-Controller
        architecture. Assumes controller has an update_current_plot method.
        model (str): the type of calculation requested (interpreted by the
        controller).
        * v (numpy 2D array): the frequency list (located in v[0, :]
        * j (numpy 2D array): the symmetric matrix of J coupling constants
        (j[m, n] = j[n, m] = coupling between nuclei m and n)
        * w (numpy 2D array): the width of the signal at half height (located
        in w[0, 0]
        * spec_freq: (float) the simulated spectrometer frequency.
        * v_ppm: The conversion of v (in Hz) to ppm.
    """

    def __init__(self, parent=None, controller=None, n=4, spec_freq=300,
                 **options):
        """Initialize the frame with necessary widgets and attributes.

        Keyword arguments:
        :param parent: the parent tkinter object
        :param controller: the Controller object of the MVC application
        :param n: the number of nuclei in the spin system
        :param spec_freq: (float) the frequency of the simulated spectrometer.
        :param options: standard optional kwargs for a tkinter Frame
        """
        ToolBar.__init__(self, parent, **options)
        self.controller = controller
        self.model = 'nspin'
        self.v, self.j = getWINDNMRdefault(n)
        self.w_array = np.array([[0.5]])
        # self.defaults = {'v': self.v,
        #                  'j': self.j,
        #                  'w': self.w_array}
        self.vars = copy.deepcopy(self.defaults)
        self.spec_freq = spec_freq
        self.v_ppm = self.v / self.spec_freq

        self.defaults = self.create_var_dict()
        # TODO: see if deepcopy is needed here

        # following seems to be a hack to get a spinbox for w, when currently
        # only spinbox uses arrays and not single numbers. Change in future?

        # self.vars = (self.v, self.j, self.w_array)
        self.fields = {}
        # print('start creation of spinbar ', n)
        self.add_frequency_widgets(n)
        # print('called add_frequency_widgets')
        self.add_peakwidth_widget()
        self.add_J_button(n)
        self.add_addspectra_button()
        self.reset_button = Button(self,
                                   name='reset_button',
                                   text='Reset',
                                   command=lambda: self.restore_defaults())
        self.reset_button.pack(side=RIGHT)

    def create_var_dict(self):
        return {'v': self.v_ppm,
                'j': self.j,
                'w': self.w_array}

    def add_frequency_widgets(self, n):
        """Add frequency-entry widgets to the toolbar.

        :param n: (int) The number of nuclei being simulated.
        """
        # print('entered add_frequency widgets ', n)
        for freq in range(n):
            name = 'V' + str(freq + 1)
            # print('add_frequency_units working with name ', name)
            vbox = ArrayBox(self, array=self.v_ppm, coord=(0, freq),
                            name=name,
                            controller=self.request_plot)
            self.fields[name] = vbox
            vbox.pack(side=LEFT)
        # print('spinbar ', n, ' fields:')
        # for key, val in self.fields.items():
        #     print(key, val)

    def add_peakwidth_widget(self):
        """Add peak width-entry widget to the toolbar."""
        wbox = ArrayBox(self, array=self.w_array, coord=(0, 0), name="W",
                        controller=self.request_plot)
        self.fields['W'] = wbox
        wbox.pack(side=LEFT)

    def add_J_button(self, n):
        """Add a button to the toolbar that will pop up the J-entry window.

        :param n: (int) The number of nuclei being simulated.
        """
        vj_button = Button(self, text="Enter Js",
                           command=lambda: self.vj_popup(n))
        vj_button.pack(side=LEFT, expand=N, fill=NONE)

    def add_addspectra_button(self):
        """Add a button to the toolbar that will add the (top) current
        simulated spectrum to the (bottom) total spectrum plot.
        """
        self.add_spectra_button = Button(self,
                                         text='Add To Total',
                                         command=lambda: self.add_spectra())
        self.add_spectra_button.pack(side=RIGHT)

    def vj_popup(self, n):
        """
        Creates a new Toplevel window that provides entries for both
        frequencies and J couplings, and updates self.v and self.j when
        entries change.
        :param n: number of spins
        """
        tl = Toplevel()
        Label(tl, text='Second-Order Simulation').pack(side=TOP)
        datagrid = Frame(tl)

        # For gridlines, background set to the line color (e.g. 'black')
        datagrid.config(background='black')

        Label(datagrid, bg='gray90').grid(row=0, column=0, sticky=NSEW,
                                          padx=1, pady=1)
        for col in range(1, n + 1):
            Label(datagrid, text='V%d' % col, width=8, height=3,
                  bg='gray90').grid(
                row=0, column=col, sticky=NSEW, padx=1, pady=1)

        for row in range(1, n + 1):
            vtext = "V" + str(row)
            v = ArrayBox(datagrid, array=self.v_ppm,
                         coord=(0, row - 1),  # V1 stored in v[0, 0], etc.
                         name=vtext, color='gray90',
                         controller=self.request_plot)
            v.grid(row=row, column=0, sticky=NSEW, padx=1, pady=1)
            for col in range(1, n + 1):
                if col < row:
                    j = ArrayBox(datagrid, array=self.j,
                                 # J12 stored in j[0, 1] (and j[1, 0]) etc
                                 coord=(col - 1, row - 1),
                                 name="J%d%d" % (col, row),
                                 controller=self.request_plot)
                    j.grid(row=row, column=col, sticky=NSEW, padx=1, pady=1)
                else:
                    Label(datagrid, bg='grey').grid(
                        row=row, column=col, sticky=NSEW, padx=1, pady=1)

        datagrid.pack()

    def set_freq(self, freq):
        """Set the simulated spectrometer frequency and update the current
        plot accordingly.

        :param freq: (float) the frequency of the spectrometer to simulate.
        """
        self.spec_freq = freq
        self.request_plot()

    def update_v(self):
        """Translate the ppm frequencies in v_ppm to Hz, and overwrite v
        with the result.
        """
        self.v = self.v_ppm * self.spec_freq
        self.vars = self.create_var_dict()

    def request_plot(self):
        """Adapt 2D array data to kwargs of correct type for the controller."""
        self.update_v()
        # kwargs = {'v': self.v[0, :],  # controller takes 1D array of freqs
        #           'j': self.j,
        #           'w': self.w_array[0, 0]}  # controller takes float for w

        # kwargs = {'v': self.v,  # controller takes 1D array of freqs
        #           'j': self.j,
        #           'w': self.w_array}  # controller takes float for w

        # self.controller('nspin', kwargs)
        self.controller('nspin', self.vars)

    def add_spectra(self):
        """Adapt 2D array data to kwargs of correct type for the controller."""
        self.update_v()
        kwargs = {'v': self.v[0, :],  # controller takes 1D array of freqs
                  'j': self.j,
                  'w': self.w_array[0, 0]}  # controller takes float for w

        # self.controller.update_current_plot('nspin', **kwargs)
        self.master.master.request_add_plot('nspin', **kwargs)

    def reset(self, vars):
        self.vars = copy.deepcopy(vars)
        self.v = self.vars['v']
        self.j = self.vars['j']
        self.w = self.vars['w']
        self.v_ppm = self.v / self.spec_freq

        for i, freq in enumerate(self.v_ppm[0]):
            name = 'V' + str(i + 1)
            widget = self.fields[name]
            widget.set_value(freq)

        self.controller('nspin', self.vars)

    def test_reset(self, v, j, w):
        pass
        # self.v = v
        # print('start of test: v = ', self.v)
        # self.v += 300
        # print('v changed to: ', self.v)
        # self.v_ppm = v / self.spec_freq
        # self.j = j
        # self.w_array = w

        # for freq in range(1, len(self.v_ppm[0]) + 1):
        #     name = 'V' + str(freq)
        #     print('n = ', len(self.v) + 1, ' name: ', name)
        #     widget = self.fields[name]
        #     print('found widget: ', widget)

        # for i, freq in enumerate(self.v_ppm[0]):
        #     print(i, freq)
        #     name = 'V' + str(i + 1)
        #     print(name)
        #     widget = self.fields[name]
        #     if float(widget.get_value()) != freq:
        #         print('CHANGE DETECTED: ',
        #               float(widget.get_value()),
        #               freq)
        #         widget.set_value(freq)
        #         print('value is now ', widget.get_value())


class SecondOrderSpinBar(SecondOrderBar):
    """A subclass of SecondOrderBar that uses ArraySpinBox widgets for the
    toolbar.

    Overrides add_frequency_widgets and add_peakwidth_widget.
    """
    def __init__(self, parent=None,
                 from_=-10000.00, to=10000.00, increment=10, realtime=False,
                 **options):
        """Initialize subclass of SecondOrderBar with extra arguments for the
        SpinBox minimum and maximum values, standard increment, and realtime
        behavior.

        :param from_: (float) the minimum value for the spinboxes
        :param to: (float) the maximum value for the spinboxes
        :param increment: (float) the amount to increment/decrement the SpinBox
        contents per arrow click.
        :param realtime: (bool) True if controller should be repeatedly called
        as a SpinBox arrow is being held down.
        """
        self.spinbox_kwargs = {'from_': from_,
                               'to': to,
                               'increment': increment,
                               'realtime': realtime}
        SecondOrderBar.__init__(self, parent, **options)

    def add_frequency_widgets(self, n):
        for freq in range(n):
            vbox = ArraySpinBox(self, array=self.v_ppm, coord=(0, freq),
                                name='V' + str(freq + 1),
                                controller=self.request_plot,
                                **self.spinbox_kwargs)
            vbox.pack(side=LEFT)

    def add_peakwidth_widget(self):
        """
        Currently hard-wired to vary from 0.01 to 100 Hz, with an increment
        of 0.1 Hz.
        """
        wbox = ArraySpinBox(self, array=self.w_array, coord=(0, 0),
                            name="W",
                            controller=self.request_plot,
                            from_=0.01, to=100, increment=0.1,
                            realtime=self.spinbox_kwargs['realtime'])
        wbox.pack(side=LEFT)


if __name__ == '__main__':

    from nmrmint.windnmr_defaults import multiplet_bar_defaults


    class DummyController:
        @staticmethod
        def update_view_plot(*args, **kwargs):
            print(args)
            print(kwargs)

    dummy_controller = DummyController()

    root = Tk()
    root.title('test toolbars')

    toolbars = [FirstOrderBar, SecondOrderBar, SecondOrderSpinBar]
    for toolbar in toolbars:
        toolbar(root, controller=dummy_controller).pack(side=TOP)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

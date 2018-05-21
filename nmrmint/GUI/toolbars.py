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
from nmrmint.initialize import nspin_defaults


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
        self._vars = {}
        # self.add_spectra_button = Button(self,
        #                                  name='addbutton',
        #                                  text='Add To Total',
        #                                  command=lambda: self.add_spectra())
        # self.add_spectra_button.pack(side=RIGHT)
        # for testing:
        self.reset_button = Button(self,
                                   name='reset_button',
                                   text='Reset',
                                   command=lambda:
                                   self.restore_defaults_and_refresh())
        self.reset_button.pack(side=RIGHT)

    @property
    def vars(self):
        return self._vars

    @vars.setter
    def vars(self, value):
        self._vars = value

    @vars.getter
    def vars(self):
        return self._vars

    # def request_plot(self):
    #     """Send request to controller to recalculate and refresh the view's
    #     plot.
    #     """
    #     # self.controller.update_current_plot(self.model, **self.vars)
    #     self.controller(self.model, **self.vars)

    # def add_spectra(self):
    #     """Send request to controller to add the current spectrum to the
    #     total spectrum.
    #     """
    #     self.master.master.request_add_plot(self.model, **self.vars)

    def restore_defaults_and_refresh(self):
        self.restore_defaults()
        self.controller()

    def restore_defaults(self):
        self.reset(self.defaults)

    def reset(self, _vars):
        pass


class FirstOrderBar(ToolBar):
    """A subclass of ToolBar designed for use with first-order (single-signal)
    simulations.

    Extends ToolBar with the following methods:
        make_kwargs: converts toolbar data to appropriate kwargs for calling
        the controller. Includes conversion from ppm to Hz.

    Overrides the following methods, to make use of make_kwargs:
        request_plot
        add_spectra
    """

    def __init__(self, parent=None, **options):
        """Instantiate the ToolBar with appropriate widgets for first-order
        calculations.
        """
        ToolBar.__init__(self, parent, **options)
        self.model = 'first_order'
        self.defaults = {'JAX': 7.00,
                         '#A': 2,
                         'JBX': 3.00,
                         '#B': 1,
                         'JCX': 2.00,
                         '#C': 0,
                         'JDX': 7,
                         '#D': 0,
                         'Vcentr': 0.5,
                         '# of nuclei': 1,
                         'width': 0.5}
        self._vars = self.defaults.copy()
        self.fields = {}
        kwargs = {'dict_': self.vars,
                  'controller': self.controller}
        for key in ['# of nuclei', 'JAX', '#A', 'JBX', '#B', 'JCX', '#C',
                    'JDX', '#D', 'Vcentr', 'width']:
            if '#' not in key:
                widget = VarBox(self, name=key, **kwargs)
            else:
                widget = IntBox(self, name=key, **kwargs)
            self.fields[key] = widget
            widget.pack(side=LEFT)

        # self.test_reset(self.vars)

    def reset(self, vars_):
        for key, val in vars_.items():
            self.vars[key] = val
            widget = self.fields[key]
            widget.set_value(val)
        print('Bar reset with vars: ', self.vars)
        # self.vars = copy.deepcopy(vars)
        # for key, val in self.vars.items():
        #     widget = self.fields[key]
        #     widget.set_value(val)


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
        * v_ppm: The conversion of v (in Hz) to ppm.
    """

    def __init__(self, parent=None, controller=None, n=4, **options):
        """Initialize the frame with necessary widgets and attributes.

        Keyword arguments:
        :param parent: the parent tkinter object
        :param controller: the Controller object of the MVC application
        :param n: the number of nuclei in the spin system
        :param options: standard optional kwargs for a tkinter Frame
        """
        # Debugging note: seems to be a problem with ppm frequencies at some
        # point being divided by spec freq causing them to lump as a singlet
        # at 0. This is first detected when a second-order subspectrum is
        # reloaded.
        # Need to be clear about what the "official record" for subspectra
        # saves and controller calls should be--vars with v in ppm. v in Hz
        # should really just be an artefact carried over from previous uses.
        # Once default vars are translated into v_ppm, v in Hz should no
        # longer be needed by toolbar.
        # Abstracting out further: if toolbar status is stored in Subspectrum
        # object, then data structures could be entirely stripped from
        # toolbars and held in Subspectrum. For now, concentrate on fixing
        # data corruption issue.

        ToolBar.__init__(self, parent, **options)
        self.controller = controller
        self.model = 'nspin'
        # self.v, self.j = nspin_defaults(n)
        self.v_ppm, self.j = nspin_defaults(n)

        self.w_array = np.array([[0.5]])

        self._vars = self.create_var_dict()
        self.defaults = copy.deepcopy(self._vars)  # for resetting toolbar
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
        # self.add_addspectra_button()
        self.reset_button = Button(self,
                                   name='reset_button',
                                   text='Reset',
                                   command=lambda: self.restore_defaults_and_refresh())
        self.reset_button.pack(side=RIGHT)

    @property
    def vars(self):
        return self._vars

    @vars.getter
    def vars(self):
        self._vars = self.create_var_dict()
        return self._vars

    @vars.setter
    def vars(self, value):
        print('setter given ', value)
        self._vars = value

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
                            controller=self.controller)
            self.fields[name] = vbox
            vbox.pack(side=LEFT)

    def add_peakwidth_widget(self):
        """Add peak width-entry widget to the toolbar."""
        wbox = ArrayBox(self, array=self.w_array, coord=(0, 0), name="W",
                        controller=self.controller)
        self.fields['W'] = wbox
        wbox.pack(side=LEFT)

    def add_J_button(self, n):
        """Add a button to the toolbar that will pop up the J-entry window.

        :param n: (int) The number of nuclei being simulated.
        """
        vj_button = Button(self, text="Enter Js",
                           command=lambda: self.vj_popup(n))
        vj_button.pack(side=LEFT, expand=N, fill=NONE)

    # def add_addspectra_button(self):
    #     """Add a button to the toolbar that will add the (top) current
    #     simulated spectrum to the (bottom) total spectrum plot.
    #     """
    #     self.add_spectra_button = Button(self,
    #                                      text='Add To Total',
    #                                      command=lambda: self.add_spectra())
    #     self.add_spectra_button.pack(side=RIGHT)

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
                         controller=self.controller)
            v.grid(row=row, column=0, sticky=NSEW, padx=1, pady=1)
            for col in range(1, n + 1):
                if col < row:
                    j = ArrayBox(datagrid, array=self.j,
                                 # J12 stored in j[0, 1] (and j[1, 0]) etc
                                 coord=(col - 1, row - 1),
                                 name="J%d%d" % (col, row),
                                 controller=self.controller)
                    j.grid(row=row, column=col, sticky=NSEW, padx=1, pady=1)
                else:
                    Label(datagrid, bg='grey').grid(
                        row=row, column=col, sticky=NSEW, padx=1, pady=1)

        datagrid.pack()

    def reset(self, _vars):
        """Reset the toolbar with supplied vars.

        :param _vars: {'v': 2D np.array of [[ppm chemical shifts...]],
        'j': 2D np.array of Js in Hz,
        'w': 2D np.array of [[peak width]]}

        TODO: factor out clunky use of 2D arrays for v and w, to 1D array and
        float."""

        print('second-order reset with vars: ', _vars)
        # print('test setter')
        # self.vars = copy.deepcopy(_vars)
        # print('test getter: ', self.vars)
        self.v_ppm = _vars['v']
        self.j = _vars['j']
        self.w = _vars['w']

        for i, freq in enumerate(self.v_ppm[0]):
            name = 'V' + str(i + 1)
            widget = self.fields[name]
            widget.set_value(freq)
            widget.array = self.v_ppm
            print(name, 'was set to : ', freq)

        width_widget = self.fields['W']
        width = self.w[0][0]
        width_widget.set_value(width)
        # width_widget.array = self.w
        # print('W was set to: ', width_widget.array)
        print('W field was set to: ', width_widget.get_value())

        # self.controller('nspin', self.vars)
        self.controller()


# TODO: most recent changes have used SecondOrderBar. If SecondOrderSpinBar
# is still a possible option, make sure that it is updated to be a complete
# swap for SecondOrderBar
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

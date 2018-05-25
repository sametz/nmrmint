"""Custom tkinter frames that hold multiple widgets plus capabilities to
store data and send it to a callback.

Provides the following classes:
    * _ToolBar: A base class for creating toolbars, intended to be subclassed
and extended.
    * FirstOrderBar: holds numerical inputs required for first-order simulation
    * SecondOrderBar: holds numerical inputs, plus a button with a pop-up 2D
array for entering chemical shifts and J coupling constants, for second-order
simulations of up to 8 coupled spins.
    *SecondOrderSpinBar: Subclass of SecondOrderBar that uses spinbox widgets.
"""

import copy
from tkinter import *

import numpy as np

from nmrmint.GUI.widgets import (ArrayBox, ArraySpinBox, VarBox, IntBox)
from nmrmint.initialize import nspin_defaults


class _ToolBar(Frame):
    """Extend tkinter.Frame with a callback reference, a model
    name, a _vars property, a reset button, and methods for the reset callback.

    Intended to be subclassed, and not instantiated itself.

    Methods:
        * reset: resets the toolbar with provided vars Must be overridden by
        subclass.
        * restore_defaults: resets the toolbar with default vars.

    Attributes:
        * callback: the function to be called when a change to the toolbar's
    widgets is detected
        * model (str): the type of calculation requested (interpreted by the
    Controller via the callback). To be overwritten by subclass.
        * vars: (dict) The kwargs that the callback is called with.
    """

    def __init__(self, parent=None, callback=None, **options):
        """Initialize the _ToolBar object with a reference to a callback.

        Keyword arguments:
        :param parent: the parent tkinter object
        :param callback: the function to be called when a change to the
        toolbar's widgets is detected
        :param options: standard optional kwargs for a tkinter Frame
        """
        Frame.__init__(self, parent, **options)
        self.callback = callback
        self.model = 'model'  # must be overwritten by subclasses
        self._defaults = {}  # overwrite for subclasses
        self._vars = {}  # overwrite for subclasses

        self._reset_button = Button(self,
                                    name='reset_button',
                                    text='Reset',
                                    command=lambda:
                                    self._restore_defaults_and_refresh())
        self._reset_button.pack(side=RIGHT)

    @property
    def vars(self):
        return self._vars

    # @vars.setter not needed

    @vars.getter
    def vars(self):
        return self._vars

    def _restore_defaults_and_refresh(self):
        self.restore_defaults()
        self.callback()

    def restore_defaults(self):
        # deepcopy to prevent corruption of _defaults by reset
        self.reset(copy.deepcopy(self._defaults))

    def reset(self, _vars):
        pass


class FirstOrderBar(_ToolBar):
    """A subclass of _ToolBar designed for use with first-order (single-signal)
    simulations.

    Extends _ToolBar with a series of input widgets and a _fields dict to
    reference them.

    Overrides the following methods:
        * reset

    Overrides the following attributes:
        * self.model
        * self._defaults
        * self._vars
    """

    def __init__(self, parent=None, **options):
        """Instantiate the _ToolBar with appropriate widgets for first-order
        calculations.
        """
        _ToolBar.__init__(self, parent, **options)
        self.model = 'first_order'
        self._defaults = {'JAX': 7.00,
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
        self._vars = self._defaults.copy()
        self._fields = {}
        kwargs = {'dict_': self.vars,
                  'callback': self.callback}
        for key in ['# of nuclei', 'JAX', '#A', 'JBX', '#B', 'JCX', '#C',
                    'JDX', '#D', 'Vcentr', 'width']:
            if '#' not in key:
                widget = VarBox(self, name=key, **kwargs)
            else:
                widget = IntBox(self, name=key, **kwargs)
            self._fields[key] = widget
            widget.pack(side=LEFT)

    def reset(self, vars_):
        """Reset the toolbar with provided variables.

        :param vars_: {}
        """
        for key, val in vars_.items():
            self.vars[key] = val
            widget = self._fields[key]
            widget.set_value(val)


class SecondOrderBar(_ToolBar):
    """
    Extends Frame to hold n frequency entry boxes, an entry box for peak
    width (default 0.5 Hz), a 2-D numpy array for frequencies (see below),
    a 2-D numpy array for coupling constants, and a button to pop up a window
    for entering J values as well as frequencies.

    Overrides the following methods:
        * reset

    Overrides the following attributes:
        * self.model
        * self._defaults
        * self._vars
        * self.vars (@property)
    """

    def __init__(self, parent=None, n=4, **options):
        """Initialize the frame with necessary widgets and attributes.

        Keyword arguments:
        :param parent: the parent tkinter object
        :param callback: the Controller object of the MVC application
        :param n: the number of nuclei in the spin system
        :param options: standard optional kwargs for a tkinter Frame
        """
        # The ArrayBox and ArraySpinBox widgets currently handle 2-D arrays
        # only, so the frequencies only occupy the first row of a 1-row
        # 2-dimensional array (self._v_ppm), and the peak widths the first
        # column of the first row of a 1-cell 2-D array (self._w_array). i.e.
        #  self._v_ppm [0,:] provides a 1-D numpy array of the frequencies,
        # and self._w_array[0, 0] provides the peak width.
        # TODO: refactor this so v and w have an intuitive data type

        _ToolBar.__init__(self, parent, **options)
        self.model = 'nspin'
        self._v_ppm, self._j = nspin_defaults(n)
        self._w_array = np.array([[0.5]])
        self._vars = self._create_var_dict()
        self._defaults = copy.deepcopy(self._vars)  # for resetting toolbar

        self._fields = {}
        self._add_frequency_widgets(n)
        self._add_peakwidth_widget()
        self._add_J_button(n)

    @property
    def vars(self):
        return self._vars

    @vars.getter
    def vars(self):
        self._vars = self._create_var_dict()
        return self._vars

    # @vars.setter not needed

    def _create_var_dict(self):
        return {'v': self._v_ppm,
                'j': self._j,
                'w': self._w_array}

    def _add_frequency_widgets(self, n):
        """Add frequency-entry widgets to the toolbar.

        :param n: (int) The number of nuclei being simulated.
        """
        for freq in range(n):
            name = 'V' + str(freq + 1)
            vbox = ArrayBox(self, array=self._v_ppm, coord=(0, freq),
                            name=name,
                            callback=self.callback)
            self._fields[name] = vbox
            vbox.pack(side=LEFT)

    def _add_peakwidth_widget(self):
        """Add peak width-entry widget to the toolbar."""
        wbox = ArrayBox(self, array=self._w_array, coord=(0, 0), name="W",
                        callback=self.callback)
        self._fields['W'] = wbox
        wbox.pack(side=LEFT)

    def _add_J_button(self, n):
        """Add a button to the toolbar that will pop up the J-entry window.

        :param n: (int) The number of nuclei being simulated.
        """
        vj_button = Button(self, text="Enter Js",
                           command=lambda: self._vj_popup(n))
        vj_button.pack(side=LEFT, expand=N, fill=NONE)

    def _vj_popup(self, n):
        """
        Creates a new Toplevel window that provides entries for both
        frequencies and J couplings, and updates self.v and self._j when
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
            v = ArrayBox(datagrid, array=self._v_ppm,
                         coord=(0, row - 1),  # V1 stored in v[0, 0], etc.
                         name=vtext, color='gray90',
                         callback=self.callback)
            v.grid(row=row, column=0, sticky=NSEW, padx=1, pady=1)
            for col in range(1, n + 1):
                if col < row:
                    j = ArrayBox(datagrid, array=self._j,
                                 # J12 stored in _j[0, 1] (and _j[1, 0]) etc
                                 coord=(col - 1, row - 1),
                                 name="J%d%d" % (col, row),
                                 callback=self.callback)
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
        float.
        """
        self._v_ppm = _vars['v']
        self._j = _vars['j']
        self.w = _vars['w']

        for i, freq in enumerate(self._v_ppm[0]):
            name = 'V' + str(i + 1)
            widget = self._fields[name]
            widget.set_value(freq)
            widget.array = self._v_ppm

        width_widget = self._fields['W']
        width = self.w[0][0]
        width_widget.set_value(width)

        self.callback()


# TODO: most recent changes have used SecondOrderBar. If SecondOrderSpinBar
# is still a possible option, make sure that it is updated to be a complete
# swap for SecondOrderBar
class SecondOrderSpinBar(SecondOrderBar):
    """A subclass of SecondOrderBar that uses ArraySpinBox widgets for the
    toolbar.

    Overrides _add_frequency_widgets and _add_peakwidth_widget.

    Extends SecondOrderBar with _spinbox_kwargs for spinbox instantiation.
    """

    def __init__(self, parent=None,
                 from_=-1.0, to=15.0, increment=0.01, realtime=False,
                 **options):
        """Initialize subclass of SecondOrderBar with extra arguments for the
        SpinBox minimum and maximum values, standard increment, and realtime
        behavior.

        :param from_: (float) the minimum value for the spinboxes
        :param to: (float) the maximum value for the spinboxes
        :param increment: (float) the amount to increment/decrement the SpinBox
        contents per arrow click.
        :param realtime: (bool) True if callback should be repeatedly called
        as a SpinBox arrow is being held down.
        """
        self._spinbox_kwargs = {'from_': from_,
                                'to': to,
                                'increment': increment,
                                'realtime': realtime}
        SecondOrderBar.__init__(self, parent, **options)

    def _add_frequency_widgets(self, n):
        """Add frequency-entry widgets to the toolbar.

        :param n: (int) The number of nuclei being simulated.
        """
        for freq in range(n):
            vbox = ArraySpinBox(self, array=self._v_ppm, coord=(0, freq),
                                name='V' + str(freq + 1),
                                callback=self.callback,
                                **self._spinbox_kwargs)
            vbox.pack(side=LEFT)

    def _add_peakwidth_widget(self):
        """
        Currently hard-wired to vary from 0.01 to 100 Hz, with an increment
        of 0.1 Hz.
        """
        wbox = ArraySpinBox(self, array=self._w_array, coord=(0, 0),
                            name="W",
                            callback=self.callback,
                            from_=0.01, to=100, increment=0.1,
                            realtime=self._spinbox_kwargs['realtime'])
        wbox.pack(side=LEFT)


if __name__ == '__main__':

    def dummy_callback(*args, **kwargs):
        print(args)
        print(kwargs)

    root = Tk()
    root.title('test toolbars')

    toolbars = [FirstOrderBar, SecondOrderBar, SecondOrderSpinBar]
    for toolbar in toolbars:
        toolbar(root, callback=dummy_callback).pack(side=TOP)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

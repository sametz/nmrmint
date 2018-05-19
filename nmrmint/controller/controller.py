"""
The controller for the nmrmint app.

Currently, the controller is actually more of an Adapter to connect a View to
the Model. For example, it can potentially allow other Views to be
substituted at some point (PyQt; web interface). Currently, the controller
assumes a tkinter view.

Provides the following class:
* Controller    Class that handles data and requests to/from the model and 
                the view.
"""
# TODO: move GUI.history and functions out of the View and into here
# TODO: simplify toolbar/widget APIs and transfer data management
# responsibilities here.

import tkinter as tk

from nmrmint.GUI.view import View
from nmrmint.model.nmrmath import (nspinspec, first_order)
from nmrmint.model.nmrplot import tkplot


class Controller:
    """Pass data and requests to/from the model and the view.
    
    The controller assumes the view offers the following methods:
    * clear_current
    * plot_current
    *update_current_plot (TODO: bad code smell--only used once, during
    initialization)
    * clear_total
    * plot_total

    The controller assumes the View has the following attribute:
    * spectrometer_frequency (float) The frequency of the simulated
    spectrometer (i.e. the MHz at which TMS protons resonate).

    The controller provides the following methods:
    * update_current_plot: update the current (top) spectrum of the View.
    * lineshape_data: calculate a lineshape for a given model and variables
    """

    def __init__(self, root):
        """Instantiate the view as a child of root, and then initializes it.
        
        Argument:
            root: a tkinter.Tk() object
        """
        self.counter = 0  # for debugging
        self.models = {'first_order': first_order,
                       'nspin': self._call_nspins_model}
        self.view = View(root, self)
        self.view.pack(expand=tk.YES, fill=tk.BOTH)

        self._initialize_view()

    def _initialize_view(self):
        self.view.clear_total()
        self.view.plot_total(*self.blank_total_spectrum())

        self.view.update_current_plot()
        # sys.settrace(self.update_current_plot)

    # Model uses frequencies in Hz, but desired View plots are in ppm.
    # The following methods convert frequency domains for lineshapes (defined
    #  with an x, y tuple of numpy ndarrays) and spectra (defined as lists of
    # (frequency, intensity) tuples).
    def _lineshape_to_ppm(self, plotdata):
        """Convert a lineshape (an x, y tuple of arrays) from x in units of
        Hz to x in units of ppm.

        Assumes access to self.view.spectrometer_frequency.
        :param plotdata: (numpy array, numpy array) the lineshape to be
        converted."""
        x, y = plotdata
        x = x / self.view.spectrometer_frequency
        return x, y

    def _spectrum_from_ppm(self, spectrum):
        """Convert a spectrum (a list of (frequency, intensity) tuples) from
        frequencies in ppm to frequencies in Hz.

        Assumes access to self.view.spectrometer_frequency.
        :param spectrum: [(frequency, intensity)...] A list of frequency,
        intensity tuples with the frequency in ppm."""
        freq, int_ = ([x * self.view.spectrometer_frequency
                       for x, y in spectrum],
                      [y for x, y in spectrum])
        return list(zip(freq, int_))

    @staticmethod
    def _call_nspins_model(v, j, w):
        """Provide an interface between the controller/view data model (use
        of **kwargs) and the functions for second-order calculations (which
        use *args).

        :param v: a 1-D numpy array of frequencies
        :param j: a 2-D numpy array of coupling constants (J values)
        :param w: line width at half height

        :return: a (spectrum, linewidth) tuple, where spectrum is a list of
        (frequency, intensity) tuples
        """
        if not (v.any() and j.any() and w.any()):
            print('invalid kwargs:')
            if not v.any():
                print('v missing')
            if not j.any():
                print('j missing')
            if not w.any():
                print('w missing')
        else:
            return nspinspec(v, j), w

    def _convert_first_order(self, vars_):
        """Convert the dictionary of widget entries from the FirstOrderBar to
        the data (a (signal, couplings) tuple) required by the controller.

        :param vars_: {} where 'JnX', 'Vcentr' and 'width' keys are floats
        (Hz/ppm/Hz respectively), and '#n' keys are ints.
        :return: {'signal': (float, float) of frequency in Hz, intensity;
                  'couplings': [(float, int)...] of J, #nuclei;
                  'w': (float) of peak width}
        """
        _Jax = vars_['JAX']
        _a = vars_['#A']
        _Jbx = vars_['JBX']
        _b = vars_['#B']
        _Jcx = vars_['JCX']
        _c = vars_['#C']
        _Jdx = vars_['JDX']
        _d = vars_['#D']
        _Vcentr = vars_['Vcentr'] * self.view.spectrometer_frequency
        _integration = vars_['# of nuclei']
        singlet = (_Vcentr, _integration)
        allcouplings = [(_Jax, _a), (_Jbx, _b), (_Jcx, _c), (_Jdx, _d)]
        couplings = [coupling for coupling in allcouplings if coupling[1] != 0]
        width = vars_['width']
        return {'signal': singlet, 'couplings': couplings, 'w': width}

    def _convert_second_order(self, vars_):
        """Convert the dictionary of widget entries from the FirstOrderBar to
        the dict of v/j/w data required by the controller.

        :param vars_: {'v': [[float...]] of chemical shifts in ppm;
                       'j': (2d numpy ndarray) of coupling constants in Hz;
                       'w': [[(float)]] for peak width in Hz}
        :return: {'v': [[float...]] of chemical shifts in Hz;
                  'j': (2d numpy ndarray) of coupling constants in Hz;
                  'w': (float) for peak width in Hz}
        """
        v_ppm = vars_['v'][0, :]
        v_Hz = v_ppm * self.view.spectrometer_frequency
        return {
            'v': v_Hz,
            'j': vars_['j'],
            'w': vars_['w'][0, 0]}

    def _first_order_spectrum(self, vars_):
        """Return a (spectrum, line width) tuple for use in calculating a
        lineshape for a first-order model.

        :param vars_: {} where 'JnX' and 'width' keys are floats and '#n'
        keys are ints.
        :return: a spectrum, w tuple where:
            spectrum: [(float, float)...] of frequency (Hz), intensity tuples
        """
        data = self._convert_first_order(vars_)
        signal = data['signal']
        couplings = data['couplings']
        w = data['w']
        spectrum = self.models['first_order'](signal=signal,
                                              couplings=couplings)
        return spectrum, w

    def _second_order_spectrum(self, vars_):
        """Return a (spectrum, line width) tuple for use in calculating a
        lineshape for a second-order model.

        :param vars_: {'v': [[float...]] of chemical shifts in ppm;
                       'j': (2d numpy ndarray) of coupling constants in Hz;
                       'w': [[(float)]] for peak width in Hz}
        :return: a spectrum, w tuple where:
            spectrum: [(float, float)...] of frequency (Hz), intensity tuples
        """
        data = self._convert_second_order(vars_)
        spectrum, w = self.models['nspin'](**data)
        return spectrum, w

    #########################################################################
    # Methods below provide the interface to the view
    #########################################################################

    def update_current_plot(self, model, vars_):
        """
        Pass the View's current (top) plot data to the appropriate
        model; simulate spectral data; and tell the view to plot the data.

        :param model: (str) The type of calculation to be performed.
        :param vars_: kwargs for the requested model.

        :return: None (including when model is not recognized)
        """
        plotdata = self.lineshape_data(model, vars_)
        self.view.clear_current()
        self.view.plot_current(*plotdata)

    def lineshape_data(self, model, vars_):
        """Return simulated lineshape data for a given model and its
        variables.

        :param model: (str) The type of calculation to be performed (
        'first_order' for first-order simulation, 'nspin' for second-order.
        :param vars_: kwargs for the requested model.
        :return: (numpy ndarray, numpy ndarray) tuple of x, y lineshape data.
        """
        if model == 'first_order':
            spectrum, w = self._first_order_spectrum(vars_)
        elif model == 'nspin':
            spectrum, w = self._second_order_spectrum(vars_)
        else:
            print('model not recognized')
            return None

        plotdata = tkplot(
            spectrum, w,
            spectrometer_frequency=self.view.spectrometer_frequency)
        return self._lineshape_to_ppm(plotdata)

    def blank_total_spectrum(self):
        """Return lineshape data for a blank total spectrum with a 0.05H TMS
        peak at 0 ppm.

        :return: (numpy.ndarray, numpy.ndarray) tuple of x, y plot data
        """
        # Initial/blank spectra will have a "TMS" peak at 0 that integrates
        # to 0.05 H.
        self.blank_spectrum = [(0, 0.05)]
        plotdata = tkplot(
            self.blank_spectrum,
            spectrometer_frequency=self.view.spectrometer_frequency)
        plotdata = self._lineshape_to_ppm(plotdata)
        return plotdata


if __name__ == '__main__':
    root = tk.Tk()
    root.title('nmrmint')  # working title only!
    app = Controller(root)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

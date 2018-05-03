"""
The controller for the nmrmint app.

Assumes a tkinter view.

Provides the following class:
* Controller    Class that handles data and requests to/from the model and 
                the view.
"""

import tkinter as tk

from nmrmint.GUI.view import View
from nmrmint.model.nmrmath import (nspinspec, AB, AB2, ABX, ABX3, AABB, AAXX,
                                   first_order, add_spectra)
from nmrmint.model.nmrplot import tkplot_current, tkplot_total


class Controller:
    """Instantiate nmrmint's view, and pass data and requests to/from
    the model and the view.
    
    The controller assumes the view offers the following methods:
    * initialize: Initialize the view (some initialization methods have to
    be moved outside of View.__init__ to avoid circular reference).
    * clear_current: clear the currently-modeled (top) spectral plot
    * plot_current: plot the currently-modeled (top) spectrum
    * clear_total: clear the total (bottom) spectral plot
    * plot_total: plot the total (bottom) spectrum
    * clear: clear all spectral plots and instantiate the total plot with a
    blank spectrum
    * update_total_spectrum: adds the most recent total spectrum data to the
    history.

    The controller assumes the View has the following attribute:
    * spectrometer_frequency (float) The frequency of the simulated
    spectrometer.

    The controller provides the following methods:
    * update_current_plot: update the current (top) spectrum of the View.
    * update_total_plot: update the total (summation, bottom) spectrum of the
    View.
    * add_view_plots: adds the current (top) plot to the total (bottom) plot
    * call_nspins_model: provide an interface that allows the model to be
    called with the view's second-order data.


    """

    # TODO: refactor to reduce code redundancy

    def __init__(self, root):
        """Instantiate the view as a child of root, and then initializes it.
        
        Argument:
            root: a tkinter.Tk() object
        """
        self.counter = 0  # for debugging
        self.models = {'first_order': first_order,
                       'nspin': self.call_nspins_model}

        self.view = View(root, self)
        self.view.pack(expand=tk.YES, fill=tk.BOTH)
        self.view.initialize()
        # sys.settrace(self.update_current_plot)

    # Model uses frequencies in Hz, but desired View plots are in ppm.
    # The following methods convert frequency domains for lineshapes (defined
    #  with an x, y tuple of numpy arrays) and spectra (defined as lists of
    # (frequency, intensity) tuples).
    def lineshape_to_ppm(self, plotdata):
        """Convert a lineshape (an x, y tuple of arrays) from x in units of
        Hz to x in units of ppm.

        Assumes access to self.view.spectrometer_frequency.
        :param plotdata: (numpy array, numpy array) the lineshape to be
        converted."""
        x, y = plotdata
        x = x / self.view.spectrometer_frequency
        return x, y

    def spectrum_from_ppm(self, spectrum):
        """Convert a spectrum (a list of (frequency, intensity) tuples) from
        frequencies in ppm to frequencies in Hz.

        Assumes access to self.view.spectrometer_frequency.
        :param spectrum: [(frequency, intensity)...] A list of frequency,
        intensity tuples with the frequency in ppm."""
        freq, int_ = ([x * self.view.spectrometer_frequency
                       for x, y in spectrum],
                      [y for x, y in spectrum])
        return list(zip(freq, int_))

    def spectrum_to_ppm(self, spectrum):
        """Convert a spectrum (a list of (frequency, intensity) tuples) from
        frequencies in Hz to frequencies in ppm.

        Assumes access to self.view.spectrometer_frequency.
        :param spectrum: [(frequency, intensity)...] A list of frequency,
        intensity tuples with the frequency in Hz."""
        freq, int_ = ([x / self.view.spectrometer_frequency
                       for x, y in spectrum],
                      [y for x, y in spectrum])
        return list(zip(freq, int_))

    # TODO: does this adapter belong here or in View? Controller should
    # define a clear API.
    @staticmethod
    def call_nspins_model(v, j, w, **kwargs):
        """Provide an interface between the controller/view data model (use
        of **kwargs) and the functions for second-order calculations (which
        use *args).

        :param v: a 1-D numpy array of frequencies
        :param j: a 2-D numpy array of coupling constants (J values)
        :param w: line width at half height

        :return: a (spectrum, linewidth) tuple, where spectrum is a list of
        (frequency, intensity) tuples
        """
        # **kwargs to catch unimplemented features
        # The difference between first- and second-order models right now
        # from the controller's perspective is just the added linewidth
        # argument. If more features are added to first- and second-order
        # models, this distinction may be lost, and all requests will have to
        #  be parsed for extra kwargs.
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

    # The methods below provide the interface to the View.

    def update_current_plot(self, model, data):
        """
        Pass the View's current (top) plot data to the appropriate
        model; simulate spectral data; and tell the view to plot the data.

        :param model: (str) The type of calculation to be performed.
        :param data: kwargs for the requested model.

        :return: None (including when model is not recognized)
        """
        # multiplet_models = ['AB', 'AB2', 'ABX', 'ABX3', 'AABB', 'AAXX',
        #                     'first_order']

        # if model in multiplet_models:
        # print('controller received ', model)
        if model == 'first_order':
            spectrum = self.models[model](**data)
            plotdata = tkplot_current(
                spectrum,
                spectrometer_frequency=self.view.spectrometer_frequency)
        elif model == 'nspin':
            spectrum, w = self.models[model](**data)
            plotdata = tkplot_current(
                spectrum, w,
                spectrometer_frequency=self.view.spectrometer_frequency)
        else:
            print('model not recognized')
            return

        plotdata = self.lineshape_to_ppm(plotdata)
        self.view.clear_current()
        self.view.plot_current(*plotdata)

    def lineshape_data(self, model, data):
        if model == 'first_order':
            spectrum = self.models[model](**data)
            plotdata = tkplot_current(
                spectrum,
                spectrometer_frequency=self.view.spectrometer_frequency)
        elif model == 'nspin':
            spectrum, w = self.models[model](**data)
            plotdata = tkplot_current(
                spectrum, w,
                spectrometer_frequency=self.view.spectrometer_frequency)
        else:
            print('model not recognized')
            return None
        return self.lineshape_to_ppm(plotdata)

    def create_lineshape(self, spectrum, *w):
        """Currently used to create blank spectra for history, but in future
        many of the Controller methods will be refactored for reuse and
        clarity.
        """
        # print('controller.create_lineshape received ', spectrum)
        spectrum = self.spectrum_from_ppm(spectrum)
        plotdata = tkplot_total(
            spectrum, *w,
            spectrometer_frequency=self.view.spectrometer_frequency)
        plotdata = self.lineshape_to_ppm(plotdata)
        # print('create_lineshape created plotdata: ', plotdata)

        return plotdata

    def update_total_plot(self, spectrum, *w):
        """Call model to calculate plot data from the provided spectrum,
        then call View to plot the result.

        :param spectrum: [(float, float)...] The spectrum to be plotted as
        the total (bottom) spectrum in the View.
        :param w: optional peak width at half height.
        """
        spectrum = self.spectrum_from_ppm(spectrum)
        plotdata = tkplot_total(
            spectrum,
            *w,
            spectrometer_frequency=self.view.spectrometer_frequency)
        plotdata = self.lineshape_to_ppm(plotdata)
        # self.view.canvas.clear_total()
        self.view.clear_total()
        self.view.plot_total(*plotdata)

    def total_plot(self, spectrum, *w):
        """Call model to calculate lineshape from provided spectrum,
        and return it.

        :param spectrum: [(float, float)...] The lineshape data for a total
        spectrum plot.
        :param w: optional peak width at half height.
        :return: (np.linspace, np.array) of x, y- lineshape data.
        """
        spectrum = self.spectrum_from_ppm(spectrum)
        plotdata = tkplot_total(
            spectrum,
            *w,
            spectrometer_frequency=self.view.spectrometer_frequency)
        plotdata = self.lineshape_to_ppm(plotdata)
        return plotdata

    def add_view_plots(self, model, total_spectrum, **data):
        """Compute a spectrum from model, **data, add it to another spectrum,
        and refresh the View's plots plus total_spectrum/history.

        :param model: (str) The type of calculation to be performed.
        :param total_spectrum: [(float, float)...] The spectrum that the new
        spectral data will be added to.
        :param data: kwargs required by the model.

        :return: None (including when model is not recognized)
        """
        # TODO: The one-line description of add_view_plots indicates that this
        # should not be one function, but several.

        multiplet_models = ['AB', 'AB2', 'ABX', 'ABX3', 'AABB', 'AAXX',
                            'first_order']
        total_spectrum_copy = total_spectrum[:]

        total_spectrum_Hz = self.spectrum_from_ppm(total_spectrum_copy)

        if model in multiplet_models:
            spectrum = self.models[model](**data)
            add_spectra(total_spectrum_Hz, spectrum)
            plotdata = tkplot_total(spectrum)
            total_plotdata = tkplot_total(total_spectrum_Hz)
        elif model == 'nspin':
            spectrum, w = self.models[model](**data)
            add_spectra(total_spectrum_Hz, spectrum)
            plotdata = tkplot_total(spectrum, w)
            total_plotdata = tkplot_total(total_spectrum_Hz, w)
        else:
            print('model not recognized')
            return
        plotdata = self.lineshape_to_ppm(plotdata)
        total_plotdata = self.lineshape_to_ppm(total_plotdata)
        total_spectrum_ppm = self.spectrum_to_ppm(total_spectrum_Hz)
        self.view.clear()
        self.view.update_total_spectrum(total_spectrum_ppm)
        self.view.plot_current(*plotdata)
        self.view.plot_total(*total_plotdata)


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

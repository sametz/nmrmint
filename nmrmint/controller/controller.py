"""
The controller for the UW-DNMR app.

Assumes a tkinter view.

Provides the following class:
* Controller    Class that handles data and requests to/from the model and 
                the view.
"""

import sys
import tkinter as tk

from nmrmint.GUI.view import View
from nmrmint.model.nmrmath import (nspinspec, AB, AB2, ABX, ABX3, AABB, AAXX,
                                   first_order, add_spectra)
from nmrmint.model.nmrplot import tkplot


class Controller:
    """Instantiate nmrmint's view, and pass data and requests to/from
    the model and the view.
    
    The controller assumes the view offers the following methods:
    
    * initialize()--Initializes the view. Currrently, just "OKs" the View 
    to call Controller.update_current_plot after view's instantiation.
    
    * clear_all()--clears the view's plot.
    
    * plot(x, y)--accept a tuple of x, y numpy arrays and plot the data.
    
    The controller provides the following methods:
    
    * update_current_plot: update the current (top) spectrum of the View.

    * update_total_plot: update the total (summation, bottom) spectrum of the
    View.

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
        self.models = {'AB': AB,
                       'AB2': AB2,
                       'ABX': ABX,
                       'ABX3': ABX3,
                       'AABB': AABB,
                       'AAXX': AAXX,
                       'first_order': first_order,
                       'nspin': self.call_nspins_model}

        self.view = View(root, self)
        self.view.pack(expand=tk.YES, fill=tk.BOTH)
        self.view.initialize()
        # sys.settrace(self.update_current_plot)

    def update_current_plot(self, model, **data):
        """
        Pass the View's current (top) plot data to the appropriate
        model; simulate spectral data; and tell the view to plot the data.

        :param model: (str) The type of calculation to be performed.
        :param data: kwargs for the requested model.

        :return: None (including when model is not recognized)
        """
        multiplet_models = ['AB', 'AB2', 'ABX', 'ABX3', 'AABB', 'AAXX',
                            'first_order']

        if model in multiplet_models:
            spectrum = self.models[model](**data)
            plotdata = tkplot(spectrum)
        elif model == 'nspin':
            spectrum, w = self.models[model](**data)
            plotdata = tkplot(spectrum, w)
        else:
            print('model not recognized')
            return

        plotdata = self.convert_to_ppm(plotdata)
        self.view.clear_current()
        self.view.plot_current(*plotdata)

    def convert_to_ppm(self, plotdata):
        x, y = plotdata
        x = x / self.view.spectrometer_frequency
        return x, y

    def update_total_plot(self, spectrum, *w):
        """Call model to calculate plot data from the provided spectrum,
        then call View to plot the result.

        :param spectrum: [(float, float)...] The spectrum to be plotted as
        the total (bottom) spectrum in the View.
        :param w: optional peak width at half height.
        """
        plotdata = tkplot(spectrum, *w)
        self.view.canvas.clear_total()
        self.view.plot_total(*plotdata)

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

        if model in multiplet_models:
            spectrum = self.models[model](**data)
            add_spectra(total_spectrum_copy, spectrum)
            plotdata = tkplot(spectrum)
            total_plotdata = tkplot(total_spectrum_copy)
        elif model == 'nspin':
            spectrum, w = self.models[model](**data)
            add_spectra(total_spectrum_copy, spectrum)
            plotdata = tkplot(spectrum, w)
            total_plotdata = tkplot(total_spectrum_copy, w)
        else:
            print('model not recognized')
            return

        self.view.clear()
        self.view.update_total_spectrum(total_spectrum_copy)
        self.view.plot_current(*plotdata)
        self.view.plot_total(*total_plotdata)

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

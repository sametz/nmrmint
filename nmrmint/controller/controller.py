"""
The controller for the UW-DNMR app.

Assumes a tkinter view.

Provides the following class:
* Controller    Class that handles data and requests to/from the model and 
                the view.
"""

import tkinter as tk

from nmrmint.GUI.view import View
from nmrmint.model.nmrmath import (nspinspec, AB, AB2, ABX, ABX3, AABB, AAXX,
                                   first_order, add_spectra)
from nmrmint.model.nmrplot import tkplot

import sys

class Controller:
    """Instantiate nmrmint's view, and pass data and requests to/from
    the model and the view.
    
    The controller assumes the view offers the following methods:
    
    * initialize()--Initializes the view. Currrently, just "OKs" the View 
    to call Controller.update_view_plot after view's instantiation. 
    
    * clear()--clears the view's plot.
    
    * plot(x, y)--accept a tuple of x, y numpy arrays and plot the data.
    
    The controller provides the following methods:
    
    * update_view_plot: parse the data sent by the view; call the appropriate
    model simulation; and tell the view to plot the model's simulated
    spectral data.

    * call_nspins_model: provide an interface that allows the model to be
    called with the view's second-order data.
    """

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
                       'nspin': self.call_nspins_model}#,
                       # 'DNMR_Two_Singlets': dnmrplot_2spin,
                       # 'DNMR_AB': dnmrplot_AB}

        self.view = View(root, self)
        self.view.pack(expand=tk.YES, fill=tk.BOTH)
        self.view.initialize()
        # sys.settrace(self.update_view_plot)

    def update_view_plot(self, model, total_spectrum, **data):
        """
        Parse the view's request; call the appropriate model for simulated
        spectral data; and tell the view to plot the data.

        :param model: (str) The type of calculation to be performed.
        :param args: DNMR model is called with positional arguments.
        :param data: first-order and second-order simulations are called with
        keyword arguments.

        :return: None (including when model is not recognized)
        """
        self.counter += 1
        multiplet_models = ['AB', 'AB2', 'ABX', 'ABX3', 'AABB', 'AAXX',
                            'first_order']
        print('Controller call #%d' % self.counter)
        print('controller received total spectrum:')
        print(total_spectrum)

        if model in multiplet_models:
            spectrum = self.models[model](**data)
            add_spectra(total_spectrum, spectrum)
            plotdata = tkplot(spectrum)
            total_plotdata = tkplot(total_spectrum)
        elif model == 'nspin':
            spectrum, w = self.models[model](**data)
            add_spectra(total_spectrum, spectrum)
            plotdata = tkplot(spectrum, w)
            total_plotdata = tkplot(total_spectrum, w)
        # elif 'DNMR' in model:
        #     plotdata = self.models[model](*args)
        else:
            print('model not recognized')
            return

        print('controller created new total spectrum:')
        print(total_spectrum)
        # if total_spectrum:
        # add_spectra(total_spectrum, spectrum)
        # total_plotdata = tkplot()
        self.view.clear()
        self.view.update_total_spectrum(total_spectrum)
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

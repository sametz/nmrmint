"""
The controller for the ReichDNMR app. 

Assumes a tkinter view.

Contains:

* Controller    Class that handles data and requests to/from the model and 
                the view.
"""
import tkinter as tk

from ReichDNMR.GUI.view import View
from ReichDNMR.model.nmrmath import (nspinspec, AB, AB2, ABX, ABX3, AABB, AAXX,
                                     first_order)

from ReichDNMR.model.nmrplot import tkplot, dnmrplot_2spin, dnmrplot_AB


class Controller:
    """Instantiates ReichDNMR's view, and passes data and requests to/from 
    the model and the view.
    
    The controller assumes the view offers the following methods:
    
    * initialize()--Initializes the view. Currrently, just "OKs" the View 
    to call Controller.update_view_plot after view's instantiation. 
    
    * clear()--clears the view's plot.
    
    * plot(x, y)--accept a tuple of x, y numpy arrays and plot the data.
    
    The controller provides the following methods:
    
    * update_view_plot: accepts a tuple of simulation name (string) and 
    variables; calls the appropriate model simulation with the variables; 
    and tells the view to plot the data the model returns.
    """
    def __init__(self, root):
        """Instantiates the view as a child of root, and then initializes it.
        
        Argument:
            root: a tkinter.Tk() object
        """
        self.models = {'AB': AB,
                       'AB2': AB2,
                       'ABX': ABX,
                       'ABX3': ABX3,
                       'AABB': AABB,
                       'AAXX': AAXX,
                       'first_order': first_order,
                       'nspin': self.call_nspins_model,  # temporary hack
                       'DNMR_Two_Singlets': dnmrplot_2spin,
                       'DNMR_AB': dnmrplot_AB}

        self.view = View(root, self)
        self.view.pack(expand=tk.YES, fill=tk.BOTH)
        self.view.initialize()

    # def update_view_plot(self, *data):
    #     """Queries the model for a simulation using data, then tells the view
    #     to plot the results.
    #
    #     Arguments:
    #         simulation: 'AB' (non-quantum mechanical AB quartet calculation
    #                     for 2 spins), or
    #                     'QM' (quantum-mechanical treatment for >= 3 spins)
    #         data: for now assumes the View sends data of the exact type and
    #         format required by the model. This may not be proper MVC
    #         separation of concerns, however.
    #     """
    #     v, j, w = data
    #     plotdata = tkplot(nspinspec(v, j), w)
    #     self.view.clear()
    #     self.view.plot(*plotdata)
    #
    def call_nspins_model(self, v, j, w, **kwargs):
        # **kwargs to catch unimplemented features
        """Provide an interface between the controller/view data model (use
        of **kwargs) and the functions for second-order calculations (which
        use *args).

        arguments:
            v: a 1-D numpy array of frequencies
            j: a 2-D numpy array of coupling constants (J values)
            w: line width at half height
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
            # plotdata = tkplot(nspinspec(v, j), w)
            # self.view.clear()
            # self.view.plot(*plotdata)
            return nspinspec(v, j), w

    def update_view_plot(self, model, *args, **data):
        # refactor to update_view_plot and get rid of above two older routines
        multiplet_models = ['AB', 'AB2', 'ABX', 'ABX3', 'AABB', 'AAXX',
                            'first_order']
        if model in multiplet_models:
            print('model: ', model)
            print('data: ', data)
            spectrum = self.models[model](**data)
            print('spectrum: ', spectrum)
            #plotdata = tkplot(self.models[model](**data))
            plotdata = tkplot(spectrum, *args)
            print('plot data begins with: ',
                  plotdata[0][:5], plotdata[1][:5])
        elif model == 'nspin':
            spectrum, w = self.models[model](**data)
            plotdata = tkplot(spectrum, w)
        elif 'DNMR' in model:  # For now DNMR will use args not kwargs to match
            # old
            # interfaces
            plotdata = self.models[model](*args)
        else:
            print('model not recognized')
            return
        self.view.clear()
        self.view.plot(*plotdata)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('ReichDNMR')  # working title only!
    app = Controller(root)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

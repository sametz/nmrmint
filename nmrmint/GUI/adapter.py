"""Tools to convert the data exported from the View to the data format
required by the Controller.

TODO: consider merging this with the Controller. If a MVC design is
maintained, with different views possible, each view could have its own
adapter. At the least, change its location to the Controller directory.

Provides the following class:
* Adapter: provides an API for converting View data according to the type of
simulation required of the Model.
"""


class Adapter:
    """Convert the data exported from the View's toolbars toolbars to the
    data format usable by the Controller.
    Controller (i.e. suitable for passing to the Model)--and vice-versa.
    """

    def __init__(self, view):
        """The view must have a .spectrometer_frequency attribute.
        """
        self.view = view
        # self.controller = view.controller

    def convert_toolbar_data(self, model, vars_):
        """Choose the correct conversion for the given model.

        """
        if model == 'first_order':
            return self.convert_first_order(vars_)
        elif model == 'nspin':
            return self.convert_second_order(vars_)
        else:
            print('model not recognized')

    # coverage
    # def to_toolbar(self):
    #     pass

    def convert_first_order(self, vars_):
        """Convert the dictionary of widget entries from the FirstOrderBar to
        the data required by the controller interface.

        The controller needs to pass a (signal, couplings) tuple to the model.
        - signal is a (frequency, intensity) tuple representing the frequency
        and intensity of the signal in the absence of coupling. Intensity is
        1 by default.
        - couplings is a list of (J, n) tuples, where J is the coupling
        constant and n is the number of nuclei coupled to the nucleus of
        interest with that same J value.
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

    def convert_second_order(self, vars_):

        v_ppm = vars_['v'][0, :]
        v_Hz = v_ppm * self.view.spectrometer_frequency
        return {
            'v': v_Hz,
            'j': vars_['j'],
            'w': vars_['w'][0, 0]}

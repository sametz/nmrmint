"""Take data sent by toolbars, and convert it to the form required by the
Controller (i.e. suitable for passing to the Model)--and vice-versa.
"""

class Adapter:

    def __init__(self, view):
        self.view = view
        self.controller = view.controller

    def from_toolbar(self, model, vars):
        # self.view.request_refresh_current_plot(model, **kwargs)
        if model == 'first_order':
            data = self.convert_first_order(vars)
            self.controller.update_current_plot(model, data)
            # request = (model, self.convert_first_order(vars))
            # for i in range(2):
            #     print(i, request[i])
            # # print(*request)
            # self.controller.update_current_plot(*request)


    def to_toolbar(self):
        pass

    def convert_first_order(self, vars):
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
        _Jax = vars['JAX']
        _a = vars['#A']
        _Jbx = vars['JBX']
        _b = vars['#B']
        _Jcx = vars['JCX']
        _c = vars['#C']
        _Jdx = vars['JDX']
        _d = vars['#D']
        _Vcentr = vars['Vcentr'] * self.view.spectrometer_frequency
        _integration = vars['# of nuclei']
        singlet = (_Vcentr, _integration)
        allcouplings = [(_Jax, _a), (_Jbx, _b), (_Jcx, _c), (_Jdx, _d)]
        couplings = [coupling for coupling in allcouplings if coupling[1] != 0]
        return {'signal': singlet, 'couplings': couplings}

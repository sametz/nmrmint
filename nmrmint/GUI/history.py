"""Provides classes for Subspectrum objects (variables for a lineshape
calculation, and the resulting lineshape data) and History (for providing
undo/redo/add spectrum/subtract spectrum functionality).
"""

class Subspectrum:

    def __init__(self, model=None, vars=None, linshape_current=None,
                 linshape_total=None, active=False):
        self.model = model
        self.vars = vars
        self.linshape_current = linshape_current
        self.linshape_total = linshape_total
        self.active = active

    def activate(self):
        self.active = True
        self.call_model

    def deactivate(self):
        self.active = False

    def call_model(self):
        pass


class History:

    def __init__(self):
        self.subspectra = []
        self.total_spectrum = []  # CHANGE TO NUMPY LINSPACE
        self.current = -1
        self.add_subspectrum()
        print('Initialized history with blank subspectrum')

    def add_subspectrum(self):
        subspectrum = Subspectrum()
        self.subspectra.append(subspectrum)
        self.current += 1
        # self.total_spectrum += subspectrum.linshape

    def update_vars(self, model, vars):
        subspectrum = self.subspectra[self.current]
        subspectrum.model = model
        subspectrum.vars = vars
        print('Subspectrum ', self.current, model, ' updated with vars: ', vars)

    def remove_subspectrum(self, subspectrum):
        self.total_spectrum -= subspectrum_linshape  # NOT FUNCTIONAL
        del subspectra[current]
        self.current -= 1

    def clear_total_spectrum(self):
        self.total_spectrum = []  # CHANGE TO NUMPY LINSPACE

    def update_spectrum(self):
        self.clear_total_spectrum()
        for subspectrum in subspectra:
            if subspectrum.active:
                self.total_spectrum += subspectrum.linshape  # NOT FUNCTIONAL


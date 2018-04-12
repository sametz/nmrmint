"""Provides classes for Subspectrum objects (variables for a lineshape
calculation, and the resulting lineshape data) and History (for providing
undo/redo/add spectrum/subtract spectrum functionality).
"""

class Subspectrum:

    def __init__(self, vars=None, linshape=None, active=True):
        self.vars = vars
        self.linshape = linshape
        self.active = active

    def activate(self):
        self.active = True
        self.call_model

    def deactivate(self):
        self.active = False


class History:

    def __init__(self):
        self.subspectra = []
        self.total_spectrum = []  # CHANGE TO NUMPY LINSPACE
        self.current = 0

    def add_subspectrum(self, subspectrum):
        self.subspectra.append(subspectrum)
        self.current = len(self.subspectra)
        self.total_spectrum += subspectrum.linshape

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


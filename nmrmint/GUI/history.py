"""Provides classes for Subspectrum objects (variables for a lineshape
calculation, and the resulting lineshape data) and History (for providing
undo/redo/add spectrum/subtract spectrum functionality).
"""

class Subspectrum:

    def __init__(self, model=None, vars=None, x=None, y=None,
                 # linshape_total=None,
                 activity=False):
        self.model = model
        self.vars = vars
        self.x = x
        self.y = y
        # self.linshape = linshape
        # self.linshape_total = linshape_total
        self.active = activity

    def activate(self):
        self.active = True
        self.call_model

    def deactivate(self):
        self.active = False

    def toggle_active(self):
        self.active = not self.active
        return self.active

    def call_model(self):
        pass


class History:

    def __init__(self):
        self.subspectra = []
        self.total_x = None
        self.total_y = None
        self.current = -1
        self.add_subspectrum()
        print('Initialized history with blank subspectrum')

    def add_subspectrum(self):
        subspectrum = Subspectrum()
        self.subspectra.append(subspectrum)
        self.current += 1
        # self.total_spectrum += subspectrum.linshape

    def current_subspectrum(self):
        return self.subspectra[self.current]

    def add_current_to_total(self):
        """probably have controller call pre-buld model routine for this"""
        self.total_y += self.current_subspectrum().y

    def remove_current_from_total(self):
        self.total_y -= self.current_subspectrum().y

    def save_current_linshape(self, x, y):
        subspectrum = self.current_subspectrum()
        subspectrum.x, subspectrum.y = x, y
        print('saved current linshape for subspectrum ', self.current,
              ' of size: x ', subspectrum.x.size, ' y ', subspectrum.y.size)

    def save_total_linshape(self, x, y):
        self.total_x, self.total_y = x, y
        print('saved total linshape for subspectrum ', self.current)

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


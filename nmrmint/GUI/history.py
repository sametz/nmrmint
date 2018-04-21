"""Provides classes for Subspectrum objects (variables for a lineshape
calculation, and the resulting lineshape data) and History (for providing
undo/redo/add spectrum/subtract spectrum functionality).
"""

class Subspectrum:
    """A memento for storing the current state of a subspectrum.

    The subspectrum is a simulation of a spin system, plus the
    calculation type, variables used, and the toolbar required in the
    GUI.
    """
    def __init__(self, model=None, vars=None, x=None, y=None,
                 toolbar=None,
                 activity=False):
        """

        :param model: str They type of calculation, either first order
        ("first_order") or second_order ("nspins"), matching strings used by
        toolbar widget. TODO: adopt better name, e.g. latter = "second_order"
        :param vars: {} a dict of toolbar variables used to simulate the
        subspectrum.
        :param x: numpy.linspace of x coordinates for the simulation result
        :param y: numpy.linspace of y coordinates for the simulation result
        :param toolbar: GUI.toolbar.ToolBar subclass
        :param activity: bool Indicates if the subspectrum has been selected
        for addition to the total spectrum. Used as a toggle.
        """
        self.model = model
        self.vars = vars
        self.x = x
        self.y = y
        self.toolbar = toolbar
        self.active = activity

    def toggle_active(self):
        """Toggle the subspectrum between active and inactive states.

        :returns: current subspectrum activity (bool)"""
        self.active = not self.active
        return self.active

    def activate(self):
        """Currently not implemented"""
        self.active = True
        self.call_model

    def deactivate(self):
        """Currently not implemented"""
        self.active = False

    def call_model(self):
        """Currently not implemented"""
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
        if self.current >= 0:
            ss_current = self.current_subspectrum()
            toolbar_current = self.current_toolbar()
            print('Departing a ', ss_current.model,
                  'with vars: ', ss_current.vars)
            print('and with a ', toolbar_current.model,
                  'with vars: ', toolbar_current.vars)

        self.subspectra.append(subspectrum)
        self.current = len(self.subspectra) - 1
        assert subspectrum is self.subspectra[self.current]
        # self.total_spectrum += subspectrum.linshape
        print('added subspectrum to history; counter is: ', self.current)

    def current_subspectrum(self):
        return self.subspectra[self.current]

    def subspectrum_data(self):
        return current.subspectrum().model, current.subspectrum().vars

    def current_toolbar(self):
        return self.current_subspectrum().toolbar

    def change_toolbar(self, toolbar):
        ss_current = self.current_subspectrum()
        print('CHANGING TOOLBAR')
        print('subspectrum was a ', ss_current.model,
              'that had vars: ', ss_current.vars)
        if ss_current.toolbar:
            print('subspectrum toolbar was recorded as a ',
                  ss_current.toolbar.model,
                  ' with vars: ', ss_current.toolbar.vars)
        else:
            print('No toolbar recorded for this subspectrum yet.')
        print('updating subspectrum toolbar to a ', toolbar.model,
              ' with vars:', toolbar.vars)
        model = toolbar.model
        vars = toolbar.vars
        self.current_subspectrum().toolbar = toolbar
        self.update_vars(model, vars)

    def back(self):
        history.dump('BACK')
        if self.current > 0:
            print('back!')
            self.current -= 1
            print('history.current now: ', self.current)
        else:
            print('at beginning')

    def forward(self):
        if self.current_subspectrum() is not self.subspectra[-1]:
            print('forward!')
            self.current += 1
        else:
            print('at end')


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

    def dump(self, txt):
        """for debugging"""
        print('=') * 10
        print('HISTORY DUMP ON: ', txt)
        ss_current = self.current_subspectrum()
        ss_prev = self.subspectra[self.current - 1]
        print('Current subspectrum dump:')
        print('model: ', ss_current.model)
        print('vars: ', ss_current.vars)
        print('toolbar model: ', ss_current.toolbar.model)
        print('toolbar vars: ', ss_current.toolbar.vars)
        print()
        print('Previous subspectrum dump')
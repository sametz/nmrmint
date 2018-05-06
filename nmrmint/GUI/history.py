"""Provides classes for Subspectrum objects (variables for a lineshape
calculation, and the resulting lineshape data) and History (for providing
undo/redo/add spectrum/subtract spectrum functionality).
"""

import copy


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

    # def update_plot_data(self):
    #     """Request new lineshape data and store it.
    #     """
    #     model, _vars = self.toolbar.model, self.toolbar.vars


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
        self.toolbar = None
        self.current = 0
        self.subspectra.append(Subspectrum())
        print('Initialized history with blank subspectrum')

    # TODO: use self.length() instead of len(self.subspectra)

    def add_subspectrum(self):
        """Add a new subspectrum object to the list of stored subspectra."""
        self.save()
        # self.current_toolbar().restore_defaults()
        subspectrum = Subspectrum()
        # if self.current >= 0:
        #     ss_current = self.current_subspectrum()
        #     toolbar_current = self.current_toolbar()
        #     print('Departing a ', ss_current.model,
        #           'with vars: ', ss_current.vars)
        #     print('and with a ', toolbar_current.model,
        #           'with vars: ', toolbar_current.vars)

        self.subspectra.append(subspectrum)
        self.current = len(self.subspectra) - 1
        # assert subspectrum is self.current_subspectrum()  #Remove once confident
        # self.total_spectrum += subspectrum.linshape
        print('added subspectrum to history; counter is: ', self.current)

    def current_subspectrum(self):
        return self.subspectra[self.current]

    def subspectrum_data(self):
        return self.current_subspectrum().model, self.current_subspectrum().vars

    def all_spec_data(self):
        """Yield model, vars for all subspectra."""
        # for subspectrum in self.subspectra:
        #     yield subspectrum.model, subspectrum.vars
        # return ((subspectrum.model, subspectrum.vars)
        #         for subspectrum in self.subspectra)
        return [(subspectrum.model, subspectrum.vars)
                for subspectrum in self.subspectra]

    def current_toolbar(self):
        # if history.toolbar is being set elsewhere--.back(), .forward() etc--
        # then this should not be needed.
        return self.current_subspectrum().toolbar

    def change_toolbar(self, toolbar):
        """schedule for removal? Still used atm"""
        self.toolbar = toolbar
        self.save()

    def delete(self):
        """Deletes the current subspectrum. History will reset to the next
        more recent subspectrum, or the previous subspectrum if it was the
        last subspectrum that was deleted.
        """
        if len(self.subspectra) == 1:
            print("Can't delete subspectrum: only one left!")
            return False
        del self.subspectra[self.current]
        if self.current >= len(self.subspectra):
            self.current = len(self.subspectra) - 1
        self.restore()
        return True

    def at_beginning(self):
        return self.current == 0

    def at_end(self):
        return self.current == len(self.subspectra) - 1

    def length(self):
        return len(self.subspectra)

    def save(self):
        """Saves the current simulation state"""
        try:
            self.current_subspectrum().toolbar = self.toolbar
            self.update_vars(self.toolbar.model, self.toolbar.vars)
        except AttributeError:
            print('HISTORY TOOLBAR ERROR: Tried to save a state for a '
                  'non-existent toolbar!!!')

    def restore(self):
        """restores the history.toolbar to that recorded in the subspectrum"""
        self.toolbar = self.current_subspectrum().toolbar
        self.toolbar.reset(self.current_subspectrum().vars)
        print('toolbar reset with vars: ', self.toolbar.vars)

    def back(self):
        """Point history towards the previous subspectrum and return True if it
        exists, or else return False.

        :return: (bool) whether action was taken or not.
        """
        # self.dump('BACK')
        if self.current > 0:
            print('back!')
            self.save()
            self.current -= 1
            # self.toolbar = self.current_subspectrum().toolbar
            print('history.current now: ', self.current)
            self.restore()
            return True
        else:
            print('at beginning')
            return False

    def forward(self):
        """Point history towards the next subspectrum and return True if it
        exists, or else return False.

        :return: (bool) whether action was taken or not.
        """
        if self.current_subspectrum() is not self.subspectra[-1]:
            print('forward!')
            self.save()
            self.current += 1
            # self.toolbar = self.current_subspectrum().toolbar
            print('history.current is now: ', self.current)
            self.restore()
            return True
        else:
            print('at end')
            return False

    def current_lineshape(self):
        ss = self.current_subspectrum()
        return ss.x, ss.y

    def save_current_linshape(self, x, y):
        subspectrum = self.current_subspectrum()
        subspectrum.x, subspectrum.y = x, y
        # print('saved current linshape for subspectrum ', self.current,
        #       ' of size: x ', subspectrum.x.size, ' y ', subspectrum.y.size)

    def save_total_linshape(self, x, y):
        self.total_x, self.total_y = x, y
        # print('saved total linshape for subspectrum ', self.current)

    def add_current_to_total(self):
        """probably have controller call pre-built model routine for this"""
        # print(type(self.total_y), type(self.current_subspectrum().y))
        self.total_y += self.current_subspectrum().y

    def remove_current_from_total(self):
        self.total_y -= self.current_subspectrum().y

    def update_vars(self, model, vars):
        """Replaces current subpectrum's model and vars, using a deep copy
        of the latter. Deep copy should be required for second order sims."""
        subspectrum = self.subspectra[self.current]
        subspectrum.model = model
        subspectrum.vars = copy.deepcopy(vars)
        print('Subspectrum ', self.current, model, ' updated with vars: ', vars)

    def update_frequency(self, freq):
        """Updates all subspectra to use a different spectrometer frequency;
        updates all subspectra; and updates total plot"""
        for subspectrum in self.subspectra:
            subspectrum.toolbar.spec_freq = freq

    def update_all_spectra(self, lineshapes):
        """Recompute all subspectra lineshape data, and total spectrum."""

        if len(self.subspectra) != len(lineshapes):
            print('MISMATCH IN NUMBER OF SUBSPECTRA AND OF LINESHAPES')
            return
        # rezero total spectrum and then
        for subspectrum, lineshape in zip(self.subspectra, lineshapes):

            # print(type(lineshape))
            x, y = lineshape
            # print(type(x), type(y))
            subspectrum.x, subspectrum.y = x, y
            if subspectrum.active:
                self.total_y += y



    # below are functions that might not be currently called
    # TODO: check for cruft

    def remove_subspectrum(self, subspectrum):
        self.remove_current_from_total()

    def clear_total_spectrum(self):
        self.total_spectrum = []  # CHANGE TO NUMPY LINSPACE

    def dump(self):
        """for debugging"""
        ss_current = self.current_subspectrum()
        if self.current > 0:
            ss_prev = self.subspectra[self.current - 1]
        else:
            ss_prev = None
        print('=' * 10)
        print('HISTORY DUMP ON: ', str(self.current))
        print('Current subspectrum dump:')
        print('model: ', ss_current.model)
        print('vars: ', ss_current.vars)
        toolbar = ss_current.toolbar
        if toolbar:
            print('toolbar model: ', ss_current.toolbar.model)
            print('toolbar vars: ', ss_current.toolbar.vars)
        else:
            print('No current toolbar.')
        print()
        if ss_prev:
            print('Previous subspectrum dump:')
            print('model: ', ss_prev.model)
            print('vars: ', ss_prev.vars)
            print('toolbar model: ', ss_prev.toolbar.model)
            print('toolbar vars: ', ss_prev.toolbar.vars)
            if ss_current == ss_prev:
                print('subspectra are equal???')
            if ss_current is ss_prev:
                print('WARNING: SUBSPECTRA ARE THE SAME OBJECT')
            if ss_current.vars == ss_prev.vars:
                print('subspectra have same vars')
            if ss_current.vars is ss_prev.vars:
                print('WARNING: SUBSPECTRA SHARE THE SAME VARS DICT')
        else:
            print('No previous spectrum')
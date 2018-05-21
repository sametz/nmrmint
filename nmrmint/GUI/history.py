"""Provides tools for storing the states of individual subspectrum
calculations, and adding/removing/switching between them.

Provides the following classes:
    * Subspectrum: Memento object that contain variables for a
lineshape calculation, and the resulting lineshape data.
    * History: provides functionality for adding, deleting, and switching
between subspectra objects.
"""
# TODO Does this belong with the Controller?
# History currently includes toolbar references and methods for resetting
# toolbars with new data. Consider refactoring out references to toolbars and
# serve only as a record of data. View could take on the responsibility of
# selecting toolbars and resetting them with data.
# If this is done, toolbar should be refactored out of Subspectrum as well.

import copy


class Subspectrum:
    """A memento for storing the current state of a subspectrum.

    The subspectrum is a simulation of an NMR signal or spin system, plus the
    calculation type, variables used, and the toolbar required in the
    GUI.

    Since Subspectrum is used to store state, any mutable attributes must be
    deepcopies of their source, e.g. to avoid toolbar changes from corrupting
    the Subspectrum record.

    Provides the following attributes:
        * model: the model type ('first_order' for a first-order multiplet,
    or "nspin" for a second-order spin system). Should match the model
    names used by the toolbars.
        * vars_: the variables used by the Controller for a model
    calculation.
        * x and y: the plot data corresponding to the lineshape matching the
    model, vars_ data.
        * toolbar: the View's toolbar object used for the subspectrum inputs
        * active: Boolean indicating whether the subspectrum is currently
    added to the total spectrum.

    Provides the following method:
        * toggle_active: toggles the activity
    """
    def __init__(self, model=None, vars_=None, x=None, y=None,
                 toolbar=None,
                 activity=False):
        """

        :param model: (str) They type of calculation, either first order
        ("first_order") or second_order ("nspins"), matching strings used by
        toolbar widget. TODO: adopt better name, e.g. latter = "second_order"
        :param vars_: (dict) of toolbar variables used to simulate the
        subspectrum.
        :param x: (numpy.ndarray) of x coordinates for the simulation result
        :param y: (numpy.ndarray) of y coordinates for the simulation result
        :param toolbar: (GUI.toolbar.ToolBar subclass) associated with
        subspectrum calculation
        :param activity: (bool) True if the subspectrum has been selected
        for addition to the total spectrum.
        """
        self.model = model
        self.vars = vars_
        self.x = x
        self.y = y
        self.toolbar = toolbar
        self.active = activity

    def toggle_active(self):
        """Toggle the subspectrum between active and inactive states.

        :return: current subspectrum activity (bool)"""
        self.active = not self.active
        return self.active

    # TODO: if undo/redo functionality is implemented in future, create
    # methods here that will allow undo/redo at the subspectrum level.

    # coverage
    def _activate(self):
        """Currently not implemented"""
        self.active = True

    # coverage
    def _deactivate(self):
        """Currently not implemented"""
        self.active = False

    # coverage
    def _call_model(self):
        """Currently not implemented"""
        pass


class History:
    """Provides functionality for adding, deleting, and switching between
    Subspectrum objects, as well as for recording the current View state.

    History maintains a list of subspectrum objects in the order that they
    were created in. It also maintains the current data for the total
    spectrum plot, adding or removing individual subspectrum plots to it as
    the subspectrum activity is toggled.

    Provides the following attributes:
        * total_x (numpy.ndarray) x coordinates for the total spectrum plot
        * total_y (numpy.ndarray) y coordinates for the total spectrum plot
        * current: index pointing to current subspectrum in _subspectra.
        TODO: bad idea making this attribute public? Use getter/setter?

    Provides the following methods:
    """

    def __init__(self):
        """History is expected to be instantiated without arguments.

        A single, blank Subspectrum object is instantiated as well, becoming
        the current_subspectrum() object.
        """
        self._subspectra = []
        self.total_x = None
        self.total_y = None
        self._toolbar = None
        self.current = 0  # Used by View to change subspectrum label
        self._subspectra.append(Subspectrum())

    #########################################################################
    # Methods below provide the interface to the controller
    #########################################################################

    def add_subspectrum(self):
        """Add a new subspectrum object to the list of stored subspectra.

        History will save the current subspectrum status and then index to
        the newly-created Subspectrum.
        """
        self.save()
        self._subspectra.append(Subspectrum())
        self.current = len(self._subspectra) - 1

    def current_subspectrum(self):
        """Return the current Subspectrum object."""
        return self._subspectra[self.current]

    def subspectrum_data(self):
        """Return the simulation data from the current Subspectrum.

        :return: (str, dict) model name, model variables
        """
        return self.current_subspectrum().model, self.current_subspectrum().vars

    def all_spec_data(self):
        """Return a list of all subspectra (model, vars) data.

        :return: [(str, dict)...] list of (model name, model variables)
        """
        return [(subspectrum.model, subspectrum.vars)
                for subspectrum in self._subspectra]

    # coverage : currently only used by a test
    def current_toolbar(self):
        # if history._toolbar is being set elsewhere--.back(), .forward() etc--
        # then this should not be needed.
        return self.current_subspectrum().toolbar

    # coverage :
    def change_toolbar(self, toolbar):
        """schedule for removal? Still used atm"""
        self._toolbar = toolbar
        self.save()

    def delete(self):
        """Deletes the current subspectrum. History will reset to the next
        more recent subspectrum, or the previous subspectrum if it was the
        last subspectrum that was deleted.

        :return: (bool) True if deletion performed; False if not.
        """
        if len(self._subspectra) == 1:
            print("Can't delete subspectrum: only one left!")
            return False
        if self.current_subspectrum().active:
            self.remove_current_from_total()
        del self._subspectra[self.current]
        if self.current >= len(self._subspectra):
            self.current = len(self._subspectra) - 1
        self.restore()
        return True

    def at_beginning(self):
        return self.current == 0

    def at_end(self):
        return self.current == len(self._subspectra) - 1

    def length(self):
        return len(self._subspectra)

    def save(self):
        """Saves the current simulation state"""
        try:
            self.current_subspectrum().toolbar = self._toolbar
            self.update_vars(self._toolbar.model, self._toolbar.vars)
        except AttributeError:
            print('HISTORY TOOLBAR ERROR: Tried to save a state for a '
                  'non-existent toolbar!!!')

    def restore(self):
        """restores the history._toolbar to that recorded in the subspectrum"""
        self._toolbar = self.current_subspectrum().toolbar
        self._toolbar.reset(self.current_subspectrum().vars)
        print('_toolbar reset with vars: ', self._toolbar.vars)

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
            # self._toolbar = self.current_subspectrum()._toolbar
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
        if self.current_subspectrum() is not self._subspectra[-1]:
            print('forward!')
            self.save()
            self.current += 1
            # self._toolbar = self.current_subspectrum()._toolbar
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

    def update_vars(self, model, vars_):
        """Replaces current subpectrum's model and vars, using a deep copy
        of the latter. Deep copy should be required for second order sims."""
        subspectrum = self._subspectra[self.current]
        subspectrum.model = model
        subspectrum.vars = copy.deepcopy(vars_)

    def update_all_spectra(self, lineshapes):
        """Recompute all subspectra lineshape data, and total spectrum."""

        if len(self._subspectra) != len(lineshapes):
            print('MISMATCH IN NUMBER OF SUBSPECTRA AND OF LINESHAPES')
            return
        # rezero total spectrum and then
        for subspectrum, lineshape in zip(self._subspectra, lineshapes):

            # print(type(lineshape))
            x, y = lineshape
            # print(type(x), type(y))
            subspectrum.x, subspectrum.y = x, y
            if subspectrum.active:
                self.total_y += y

    # Debugging routines below:

    def dump(self):
        """for debugging"""
        ss_current = self.current_subspectrum()
        if self.current > 0:
            ss_prev = self._subspectra[self.current - 1]
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

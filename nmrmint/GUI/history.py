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
        :param toolbar: (GUI.toolbar._ToolBar subclass) associated with
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

    def _update_vars(self, model, vars_):
        """Replace the current subpectrum's model and vars, using a deep copy
        of the latter (Deep copy should be required for second order
        simulations).

        :param model: (str) 'first_order' or 'nspin'
        :param vars_: (dict) of simulation parameters
        """
        self.current_subspectrum().model = model
        self.current_subspectrum().vars = copy.deepcopy(vars_)

    #########################################################################
    # Methods below provide the public API
    #########################################################################

    def current_subspectrum(self):
        """Return the current Subspectrum object."""
        return self._subspectra[self.current]

    def add_subspectrum(self):
        """Add a new subspectrum object to the list of stored subspectra.

        History will save the current subspectrum status and then index to
        the newly-created Subspectrum.
        """
        self.save()
        self._subspectra.append(Subspectrum())
        self.current = len(self._subspectra) - 1

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

    def delete(self):
        """Delete the current subspectrum. History will reset to the next
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

    def save(self):
        """Save the current simulation state"""
        try:
            self.current_subspectrum().toolbar = self._toolbar
            self._update_vars(self._toolbar.model, self._toolbar.vars)
        except AttributeError:
            print('HISTORY TOOLBAR ERROR: Tried to save a state for a '
                  'non-existent toolbar!!!')

    def restore(self):
        """restores the history._toolbar to that recorded in the subspectrum"""
        self._toolbar = self.current_subspectrum().toolbar
        self._toolbar.reset(self.current_subspectrum().vars)

    def back(self):
        """Point history towards the previous subspectrum, if possible.

        :return: (bool) True if moved back; False if already at beginning.
        """
        if self.current > 0:
            self.save()
            self.current -= 1
            self.restore()
            return True
        else:
            return False

    def forward(self):
        """Point history towards the next subspectrum and return True if it
        exists, or else return False.

        :return: (bool) whether action was taken or not.
        """
        if self.current_subspectrum() is self._subspectra[-1]:
            return False
        else:
            self.save()
            self.current += 1
            self.restore()
            return True

    def change_toolbar(self, toolbar):
        """Change the history's current toolbar and save the current state.

        :param toolbar: a subclass of toolbars._ToolBar."""
        self._toolbar = toolbar
        self.save()

    def current_lineshape(self):
        """Return the current subspectrum's lineshape data.

        :return: (numpy.ndarray, numpy.ndarray) tuple of x, y data.
        """
        ss = self.current_subspectrum()
        return ss.x, ss.y

    def save_current_lineshape(self, x, y):
        """Record the x, y lineshape data of the current subspectrum plot to
        the current subspectrum object.

        :param x: (numpy.ndarray)
        :param y: (numpy ndarray)
        """
        subspectrum = self.current_subspectrum()
        subspectrum.x, subspectrum.y = x, y

    def total_lineshape(self):
        """Return the current subspectrum's lineshape data.

        :return: (numpy.ndarray, numpy.ndarray) tuple of x, y data.
        """
        return self.total_x, self.total_y

    def save_total_lineshape(self, x, y):
        """Record the x, y lineshape data for the total plot.

        :param x: (numpy.ndarray)
        :param y: (numpy ndarray)
        """
        self.total_x, self.total_y = x, y

    def add_current_to_total(self):
        """Add the current plot to the total plot.

        Assumes that the x linspaces match between plots.
        """
        self.total_y += self.current_subspectrum().y

    def remove_current_from_total(self):
        """Subtract the current plot from the total plot.

        Assumes that the x linspaces match between plots.
        """
        self.total_y -= self.current_subspectrum().y

    def update_all_spectra(self, blank_spectrum, lineshapes):
        """Recompute all subspectra lineshape data, and the total spectrum.

        :param blank_spectrum: (numpy.ndarray, numpy.ndarray) for blank total
        spectrum plot.
        :param lineshapes: [(numpy.ndarray, numpy.ndarray)...] all the (x,
        y) plot data for all the subspectra.
        """
        self.save()
        self.save_total_lineshape(*blank_spectrum)
        if len(self._subspectra) != len(lineshapes):
            print('MISMATCH IN NUMBER OF SUBSPECTRA AND OF LINESHAPES')
            return
        for subspectrum, lineshape in zip(self._subspectra, lineshapes):
            x, y = lineshape
            subspectrum.x, subspectrum.y = x, y
            if subspectrum.active:
                self.total_y += y

    # Debugging routines below:

    def dump(self):  # pragma: no cover
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

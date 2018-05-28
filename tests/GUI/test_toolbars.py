import tkinter as tk

import numpy as np
import pytest

from nmrmint.GUI.toolbars import SecondOrderBar
from nmrmint.initialize import getWINDNMRdefault


@pytest.fixture()
def dummy_frame():
    """A dummy tk.Frame to pack things into."""
    dummy_frame = tk.Frame()
    return dummy_frame


def dummy_controller(*args):
    """For mocking out Toolbar callback calls."""
    print('Controller was passed: ', *args)
    pass


@pytest.fixture()
def default_nspin_vars():
    """A copy of the default vars that SecondOrderBar should be instantiated
    with.
    """
    v, j = getWINDNMRdefault(2)
    w_array = np.array([[0.5]])
    v_ppm = v / 300.0  # Using default spectrometer frequency of 300 MHz
    return {'v': v_ppm,
            'j': j,
            'w': w_array}


@pytest.fixture()
def testbar(dummy_frame):
    """A default 2-spin SecondOrderBar to be tested."""
    return SecondOrderBar(dummy_frame,
                          callback=dummy_controller,
                          n=2)


class TestSecondOrderBar:
    def test_can_instantiate(self,
                             default_nspin_vars,
                             testbar):
        """Confirm a SecondOrderBar can be instantiated with a default frame
        as parent.
        """
        # GIVEN a default 2-spin SecondOrderBar (testbar)
        # THEN it is instantiated with the expected .vars
        np.testing.assert_equal(testbar.vars, default_nspin_vars)

    def test_reset_v(self, testbar, default_nspin_vars):
        """Confirm test_reset will update chemical shifts."""
        # GIVEN a new set of vars differing in chemical shifts
        new_vars = default_nspin_vars
        new_v = np.array([[1.0, 2.0]])
        new_vars['v'] = new_v
        assert not np.array_equal(new_v, testbar.vars['v'])

        # WHEN the toolbar is reset using the new vars
        testbar.reset(new_vars)

        # THEN the chemical shifts have been updated with the new ones
        assert np.array_equal(new_v, testbar.vars['v'])

    def test_reset_dictionary_not_shared(self, testbar, default_nspin_vars):
        """Confirm that after a reset the toolbar.vars is not the argument
        vars.
        """
        # GIVEN a new set of vars
        new_vars = default_nspin_vars
        new_v = np.array([[1.0, 2.0]])
        new_vars['v'] = new_v
        assert not np.array_equal(new_v, testbar.vars['v'])

        # WHEN the toolbar is reset using the new vars
        testbar.reset(new_vars)

        # THEN the toolbar.vars will be equal to the new_vars, but NOT the same
        np.testing.assert_equal(testbar.vars, new_vars)
        assert testbar.vars is not new_vars

    def test_reset_does_not_replace_v_w_arrays(self, testbar,
                                               default_nspin_vars):
        """Confirm that toolbar reset does not replace the entire
        toolbar._v_ppm refrerence or ._w_array reference.
        """
        # Test written in response to bug in V0.3.0 code: after a refresh,
        # the link between the widget._array s and the toolbar arrays were
        # broken.

        # GIVEN a new set of vars
        new_vars = default_nspin_vars
        new_v = np.array([[1.0, 2.0]])
        new_w = np.array([[1]])
        new_vars['v'] = new_v
        new_vars['w'] = new_w

        original_v_array = testbar._v_ppm
        original_w_array = testbar._w_array
        assert not np.array_equal(new_v, testbar.vars['v'])
        assert not np.array_equal(new_w, testbar.vars['w'])
        assert original_v_array is testbar._v_ppm
        assert original_w_array is testbar._w_array

        # WHEN the toolbar is reset using the new vars
        testbar.reset(new_vars)

        # THEN the ._v_ppm and ._w_array references are unchanged
        assert testbar._v_ppm is original_v_array
        assert testbar._w_array is original_w_array
        np.testing.assert_equal(testbar.vars, new_vars)

# TODO: add tests for SecondOrderSpinBar if you decide to use it

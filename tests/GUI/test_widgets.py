"""Test the core functions of classes in widgets.py.

Note: for BaseEntryFrame to be tested, uncomment the code in its init to let
it set its .initial_value.
"""

import tkinter as tk

import numpy as np
import pytest

# from nmrmint.GUI.toolbars import SecondOrderBar
from nmrmint.GUI.widgets import BaseEntryFrame, ArrayBox


# from nmrmint.initialize import getWINDNMRdefault


@pytest.fixture()
def dummy_toolbar():
    frame = tk.Frame()
    return frame


@pytest.fixture()
def base_entry(dummy_toolbar):
    base_entry = BaseEntryFrame(parent=dummy_toolbar,
                                name='base_entry',
                                controller=dummy_controller)
    # The base class has no initial_value itself (supplied by subclasses), so:
    base_entry.initial_value = 0.00
    return base_entry


@pytest.fixture()
def array_entry_1d(dummy_toolbar):
    """Return an ArrayBox instance with a "1-D" array.

    Note: currently 2D numpy arrays are used everywhere.
    For chemical shifts, a 1 x n matrix is used ( [[a, b, c, ...]] )
    For width, a 1x1 matrix is used. ( [[w]] )

    :return: an ArrayBox instantiated with a 1 x 2 np.array of chemical shifts
    [[1.0, 2.0]]
    """
    chemical_shifts = np.array([[1.0, 2.0]])
    widget = ArrayBox(parent=dummy_toolbar,
                      name='base_entry',
                      controller=dummy_controller,
                      array=chemical_shifts,
                      coord=(0, 1)  # set to second entry (2.0)
                      )
    return widget


# @pytest.fixture()
# def dummy_frame():
#     dummy_frame = tk.Frame()
#     return dummy_frame


def dummy_controller(*args):
    """For mocking out Toolbar controller calls."""
    print('Controller was passed: ', *args)
    pass


# @pytest.fixture()
# def default_nspin_vars():
#     """A copy of the default vars that SecondOrderBar should be instantiated
#     with.
#     """
#     v, j = getWINDNMRdefault(2)
#     w_array = np.array([[0.5]])
#     v_ppm = v / 300.0  # Using default spectrometer frequency of 300 MHz
#     return {'v': v_ppm,
#             'j': j,
#             'w': w_array}
#
#
# @pytest.fixture()
# def testbar(dummy_frame):
#     """A default 2-spin SecondOrderBar to be tested."""
#     return SecondOrderBar(dummy_frame,
#                           controller=dummy_controller,
#                           n=2)


class TestBaseEntryFrame:
    def test_widget_instantiates(self, base_entry):
        """Test that TestBaseEntryFrame instantiates."""
        # GIVEN a BaseEntryFrame widget supplied by the fixture
        # THEN it should be instantiated with these defaults
        assert base_entry.initial_value == 0.00
        assert base_entry.current_value == 0.00
        assert type(base_entry.initial_value) is float
        assert type(base_entry.current_value) is float
        assert base_entry.name == 'base_entry'

    def test_base_entry_get_value(self, base_entry):
        """Test that .get_value() returns the expected value."""
        # GIVEN a BaseEntryFrame widget
        # WHEN it is asked for its current value
        returned_value = base_entry.get_value()

        # THEN it is the expected value of 0.0
        assert returned_value == '0.0'  # note loss of a decimal place
        assert float(returned_value) == base_entry.current_value

    def test_base_entry_set_value(self, base_entry):
        """Test that .set_value() updates the widget properly."""
        # GIVEN a BaseEntryFrame widget and a new value
        new_value = 1.0


class TestArrayBox:
    def test_widget_instantiates(self, array_entry_1d):
        """Test that array_entry_1d instantiates as expected."""
        # GIVEN an instance of ArrayBox with custom chemical shift-like array
        widget = array_entry_1d

        # THEN its initial_value and current_value are instantiated to the
        # expected value
        assert widget.initial_value == 2.0
        assert widget.current_value == 2.0

    def test_set_value(self, array_entry_1d):
        """Test that .set_value(val) makes the expected changes"""
        # GIVEN an instance of ArrayBox with custom chemical shift-like array
        widget = array_entry_1d

        # WHEN told to update its value to val
        val = 3.0
        widget.set_value(val)

        # THEN .current_value, .array are properly set
        assert widget.current_value == val
        assert widget.array[0, 1] == val
        assert float(widget.get_value()) == val

    def test_refresh_on_change(self, array_entry_1d):
        # GIVEN an instance of ArrayBox with custom chemical shift-like array
        widget = array_entry_1d

        # WHEN its value is set to a new valid value
        val = 3.0
        widget.value_var.set(val)
        assert widget.array[0, 1] != val

        # THEN .refresh() will make expected changes
        widget.refresh()
        assert widget.array[0, 1] == val
        assert widget.current_value == val


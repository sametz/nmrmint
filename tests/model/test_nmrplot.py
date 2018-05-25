import numpy as np
from pytest import approx
from nmrmint.model.nmrplot import (lorentz, add_signals)
from . import testdata
from .accepted_data import ADD_SIGNALS_DATASET


def test_lorentz_width():
    """Tests that w corresponds to width at half height"""
    v0 = 100
    I = 1
    w = 0.5

    assert lorentz(v0 - w/2, v0, I, w) == approx(0.5)
    assert lorentz(v0 + w/2, v0, I, w) == approx(0.5)


def test_lorentz_standard_max_height():
    """At a default width of 0.5 Hz, Lorentz max height should be 1
    if I = 1.
    """
    v0 = 100
    I = 1
    w = 0.5

    assert lorentz(v0, v0, I, w) == approx(1.0)


def test_lorentz_broadening():
    """If the width is doubled from the standard 0.5 Hz, then the max height
    should be half of I."""
    v0 = 100
    I = 10
    w = 1.0

    assert lorentz(v0, v0, I, w) == approx(5)


def test_add_signals():
    """
    Tests that current nmrplot.add_signals output agrees with an accepted
    dataset.

    The original dataset was generated before line broadening scaling_factor
    was added to nmrplot.lorentz. Therefore Y has been scaled to half to
    convert this data to work with the new lorentz function.
    """
    x = np.linspace(390, 410, 200)
    doublet = [(399, 1), (401, 1)]
    y = add_signals(x, doublet, 1)
    X = np.array([x for x, _ in ADD_SIGNALS_DATASET])
    Y = np.array([y / 2 for _, y in ADD_SIGNALS_DATASET])  # scale to match
    print(y)
    print(Y)
    assert np.array_equal(x, X)
    assert np.array_equal(y, Y)

import numpy as np
from pytest import approx
from secondorder.model import nmrplot
from .accepted_data import ADD_SIGNALS_DATASET


def test_lorentz_width():
    """Tests that w corresponds to width at half height"""
    v0 = 100
    I = 1
    w = 2

    assert nmrplot.lorentz(v0 - w/2, v0, I, w) == approx(0.5)
    assert nmrplot.lorentz(v0 + w/2, v0, I, w) == approx(0.5)


def test_add_signals():
    """
    Tests that current nmrplot.add_signals output agrees with an accepted
    dataset.
    """
    x = np.linspace(390, 410, 200)
    doublet = [(399, 1), (401, 1)]
    y = nmrplot.add_signals(x, doublet, 1)
    X = np.array([x for x, _ in ADD_SIGNALS_DATASET])
    Y = np.array([y for _, y in ADD_SIGNALS_DATASET])

    assert np.array_equal(x, X)
    assert np.array_equal(y, Y)

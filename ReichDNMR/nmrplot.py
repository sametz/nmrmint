import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from ReichDNMR.nmrmath import dnmr_2spin, dnmr_AB


def lorentz(v, v0, T2):
    """
    Lorentzian line shape function taking the form as in PSB. T2 acts as both
    a scaling factor and a line-width factor. Smaller T2 gives a shorter and
    broader signal.
    :param v: frequency (x coordinate)
    :param v0: the exact frequency of the peak
    :param T2: transverse (spin-spin) relaxation rate constant
    returns: intensity (y coordinate)
    """
    pi = np.pi
    return T2/(pi*(1+(T2**2)*((v-v0)**2)))


def lorentz2(v, v0, I, Q=1):
    """
    Modified Lorentzian function. T2 replaced by separate inputs for intensity
    and line width.
    :param v:  the current frequency being calculated (x coordinate)
    :param v0: the exact frequency of the signal that is
        being converted to a Lorentzian distribution
    :param I:  max intensity
    :param Q:  fudge factor for line width (defaults to 1)
    """
    pi = np.pi
    return I/(pi*(1+(Q**2)*((v-v0)**2)))


def adder(x, plist, Q=2):
    """
    :param x: the x coordinate (relative frequency in Hz)
    :param plist: a list of tuples of peak data (frequency, intensity)
    returns: the sum of the peak Lorentzian functions at x
    """
    total = 0
    for v, i in plist:
        total += lorentz2(x, v, i, Q)
    return total


def nmrplot(spectrum, y=1):
    """
    A no-frills routine that plots spectral simulation data.
    :param spectrum: A list of (frequency, intensity) tuples
    y: max intensity
    """
    spectrum.sort()  # Could become costly with larger spectra
    l_limit = spectrum[0][0] - 50
    r_limit = spectrum[-1][0] + 50
    x = np.linspace(l_limit, r_limit, 800)
    plt.ylim(-0.1, y)
    plt.gca().invert_xaxis()  # reverses the x axis
    # noinspection PyTypeChecker
    plt.plot(x, adder(x, spectrum, Q=4))

    plt.show()
    return


def tkplot(spectrum, y=1):
    spectrum.sort()
    r_limit = spectrum[-1][0] + 50
    l_limit = spectrum[0][0] - 50
    x = np.linspace(l_limit, r_limit, 2400)
    y = adder(x, spectrum, Q=4)
    return x, y


def dnmrplot_2spin(va, vb, ka, pa, T2a, T2b):
    """
    plots the function nmrmath.dnmr_2spin
    Currently assumes va > vb
    """

    l_limit = vb - 50
    r_limit = va + 50
    x = np.linspace(l_limit, r_limit, 800)
    y = dnmr_2spin(x, va, vb, ka, pa, T2a, T2b)
    return x, y


def dnmrplot_AB(v1, v2, J, k, W):
    """
    plots the function nmrmath.dnmr_AB.
    Currently assumes va > vb
    """

    l_limit = v2 - 50
    r_limit = v1 + 50
    x = np.linspace(l_limit, r_limit, 800)
    y = dnmr_AB(x, v1, v2, J, k, W)
    return x, y


if __name__ == '__main__':
    doublet = [(100, 1), (120, 1)]
    nmrplot(doublet)
    plt.show()

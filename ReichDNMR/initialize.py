"""This originated from nspin.py when the secondorder project was created,
and they plus reichdefaults should be merged at some point
"""
"""
This module uses the default WINDNMR spinsystem variables for 3-spin through
8-spin second-order calculations, plus the default AB quartet variables for 
2-spin calculations, and creates a list of (frequency, J couplings) tuples. 
The WINDNMR defaults were chosen because they allow secondorder's output to be 
visually checked against WINDNMR's output.

The frequencies v are in numpy arrays.
The J couplings are in sparse matrices. J[i,j] corresponds to the coupling
between nuclei i and j, using the same ordering of nuclei as the frequencies
in v.
The list of spinsystems begins with empty tuples. This allows intuitive
access to a particular spin system. So, spinsystem[4] is the data for the
4-spin system.
"""

import numpy as np
from scipy.sparse import lil_matrix


def spin2():
    v = np.array([150-7.5, 150+7.5])
    J = lil_matrix((2, 2))
    J[0, 1] = 12
    J = J + J.T
    return v, J


def spin3():
    v = np.array([115, 140, 190])
    J = lil_matrix((3, 3))
    J[0, 1] = 6
    J[0, 2] = 12
    J[1, 2] = 3
    J = J + J.T
    return v, J


def spin4():
    v = np.array([105, 140, 180, 205])
    J = lil_matrix((4, 4))
    J[0, 1] = -12
    J[0, 2] = 6
    J[0, 3] = 8
    J[1, 2] = 3
    J[1, 3] = 3
    # J[2, 3] = 0
    J = J + J.T
    return v, J


def spin5():
    v = np.array([105, 140, 180, 205, 225])
    J = lil_matrix((5, 5))
    J[0, 1] = -12
    J[0, 2] = 6
    # J[0, 3] = 0
    J[0, 4] = 2
    J[1, 2] = 3
    # J[1, 3] = 0
    J[1, 4] = 14
    J[2, 3] = 1
    # J[2, 4] = 0
    J[3, 4] = 1.5
    J = J + J.T
    return v, J


def spin6():
    v = np.array([105, 140, 180, 205, 225, 235])
    J = lil_matrix((6, 6))
    J[0, 1] = -12
    J[0, 2] = 6
    # J[0, 3] = 0
    J[0, 4] = 2
    # J[0, 5] = 0
    J[1, 2] = 3
    # J[1, 3] = 0
    J[1, 4] = 14
    J[1, 5] = 6
    J[2, 3] = 1
    # J[2, 4] = 0
    J[2, 5] = 3
    J[3, 4] = 1.5
    J[3, 5] = 5
    J[4, 5] = 2
    J = J + J.T
    return v, J


def spin7():
    v = np.array([105, 140, 180, 205, 225, 235, 255])
    J = lil_matrix((7, 7))
    J[0, 1] = -12
    J[0, 2] = 6
    # J[0, 3] = 0
    J[0, 4] = 2
    # J[0, 5] = 0
    # J[0, 6] = 0
    J[1, 2] = 3
    # J[1, 3] = 0
    J[1, 4] = 14
    J[1, 5] = 6
    # J[1, 6] = 0
    J[2, 3] = 1
    # J[2, 4] = 0
    J[2, 5] = 3
    # J[2, 6] = 0
    J[3, 4] = 1.5
    J[3, 5] = 5
    # J[3, 6] = 0
    J[4, 5] = 2
    # J[4, 6] = 0
    J[5, 6] = 2
    J = J + J.T
    return v, J


def spin8():
    v = np.array([85, 120, 160, 185, 205, 215, 235, 260])
    J = lil_matrix((8, 8))
    J[0, 1] = -12
    J[0, 2] = 6
    J[0, 3] = 2
    # J[0, 4] = 0
    # J[0, 5] = 0
    # J[0, 6] = 0
    # J[0, 7] = 0
    # J[1, 2] = 0
    # J[1, 3] = 0
    J[1, 4] = 14
    # J[1, 5] = 0
    # J[1, 6] = 0
    J[1, 7] = 3
    # J[2, 3] = 0
    # J[2, 4] = 0
    J[2, 5] = 3
    # J[2, 6] = 0
    # J[2, 7] = 0
    # J[3, 4] = 0
    J[3, 5] = 5
    # J[3, 6] = 0
    # J[3, 7] = 0
    J[4, 5] = 2
    # J[4, 6] = 0
    # J[4, 7] = 0
    # J[5, 6] = 0
    # J[5, 7] = 0
    J[6, 7] = 12
    J = J + J.T
    return v, J


def getWINDNMRdefault(n):
    """
    Fetches the default (frequencies, J) tuple for the n-spin second-order
    simulation.
    Currently returns a frequencies, J tuple where frequencies is a (0,
    n) 2D array (to easily work with main's ArrayBox), and J is a 2D array
    and not a sparse matrix (since sparse matrices are no longer used). Was
    easier to convert the above data this way than to rewrite it all.
    """
    spinsystem = [(), (), spin2(), spin3(), spin4(), spin5(), spin6(), spin7(),
                  spin8()]

    # Changes to modules require frequency to be a (0,n) 2D array, and J to
    # be an array and not a sparse matrix.
    freq, J = spinsystem[n]
    freq2D = np.array([freq])  # converts to 2D array
    J = J.todense()

    return freq2D, J


if __name__ == '__main__':
    from model.nmrmath import nspinspec
    from model.nmrplot import nmrplot as nmrplt

    test_freqs, test_couplings = getWINDNMRdefault(8)
    print(test_freqs)
    print(test_couplings)
    test_spectrum = nspinspec(test_freqs[0], test_couplings)
    nmrplt(test_spectrum, y=25)

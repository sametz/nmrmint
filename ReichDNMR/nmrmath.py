"""
This version of nmrmath features speed-optimized hamiltonian, simsignals,
and transition_matrix functions. Up to at least 8 spins, the new non-sparse
Hamilton code is about 10x faster. The overall performance is dramatically
better than the original code.
"""

import numpy as np
from math import sqrt

from scipy.linalg import eigh
from scipy.sparse import kron, csc_matrix, csr_matrix, lil_matrix, bmat

##############################################################################
# Second-order, Quantum Mechanics routines
##############################################################################


def popcount(n=0):
    """
    Computes the popcount (binary Hamming weight) of integer n
    input:
        :param n: an integer
    returns:
        popcount of integer (binary Hamming weight)

    """
    return bin(n).count('1')


# noinspection PyShadowingNames
def is_allowed(m=0, n=0):
    """
    determines if a transition between two spin states is allowed or forbidden.
    The transition is allowed if one and only one spin (i.e. bit) changes
    input: integers whose binary codes for a spin state
        :param n:
        :param m:
    output: 1 = allowed, 0 = forbidden

    """
    return popcount(m ^ n) == 1


def transition_matrix(n):
    """
    Creates a matrix of allowed transitions.
    The integers 0-n, in their binary form, code for a spin state (alpha/beta).
    The (i,j) cells in the matrix indicate whether a transition from spin state
    i to spin state j is allowed or forbidden.
    See the is_allowed function for more information.

    input:
        :param n: size of the n,n matrix (i.e. number of possible spin states)

    :returns: a transition matrix that can be used to compute the intensity of
    allowed transitions.
    """
    # function was optimized by only calculating upper triangle and then adding
    # the lower.
    T = lil_matrix((n, n))  # sparse matrix created
    for i in range(n - 1):
        for j in range(i + 1, n):
            if is_allowed(i, j):
                T[i, j] = 1
    T = T + T.T
    return T


# noinspection PyShadowingNames
def hamiltonian(freqlist, couplings):
    """
    Computes the spin Hamiltonian for spin-1/2 nuclei.
    inputs for n nuclei:
        :param freqlist: a list of frequencies in Hz of length n
        :param couplings: an n x n array of coupling constants in Hz
    Returns: a Hamiltonian array
    """
    nspins = len(freqlist)

    # Define Pauli matrices
    sigma_x = np.matrix([[0, 1/2], [1/2, 0]])
    sigma_y = np.matrix([[0, -1j/2], [1j/2, 0]])
    sigma_z = np.matrix([[1/2, 0], [0, -1/2]])
    unit = np.matrix([[1, 0], [0, 1]])

    # The following empty arrays will be used to store the
    # Cartesian spin operators.
    Lx = np.empty((1, nspins), dtype='object')
    Ly = np.empty((1, nspins), dtype='object')
    Lz = np.empty((1, nspins), dtype='object')

    for n in range(nspins):
        Lx[0, n] = 1
        Ly[0, n] = 1
        Lz[0, n] = 1
        for k in range(nspins):
            if k == n:                                  # Diagonal element
                Lx[0, n] = np.kron(Lx[0, n], sigma_x)
                Ly[0, n] = np.kron(Ly[0, n], sigma_y)
                Lz[0, n] = np.kron(Lz[0, n], sigma_z)
            else:                                       # Off-diagonal element
                Lx[0, n] = np.kron(Lx[0, n], unit)
                Ly[0, n] = np.kron(Ly[0, n], unit)
                Lz[0, n] = np.kron(Lz[0, n], unit)

    Lcol = np.vstack((Lx, Ly, Lz)).real
    Lrow = Lcol.T  # As opposed to sparse version of code, this works!
    Lproduct = np.dot(Lrow, Lcol)

    # Hamiltonian operator
    H = np.zeros((2**nspins, 2**nspins))

    # Add Zeeman interactions:
    for n in range(nspins):
        H = H + freqlist[n] * Lz[0, n]

    # Scalar couplings

    # Testing with MATLAB discovered J must be /2.
    # Believe it is related to the fact that in the SpinDynamics.org simulation
    # freqs are *2pi, but Js by pi only. Video is supposed to explain why.
    scalars = 0.5 * couplings
    scalars = np.multiply(scalars, Lproduct)
    for n in range(nspins):
        for k in range(nspins):
            H += scalars[n, k].real

    return H


# noinspection PyPep8Naming,PyShadowingNames
def simsignals(H, nspins):
    """
    Solves the spin Hamiltonian H and returns a list of (frequency, intensity)
    tuples. Nuclei must be spin-1/2.
    Inputs:
        :param H: a Hamiltonian array
        :param nspins: number of nuclei
    :return spectrum: a list of (frequency, intensity) tuples.
    """
    # This routine was optimized for speed by vectorizing the intensity
    # calculations, replacing a nested-for signal-by-signal calculation.
    # Considering that hamiltonian was dramatically faster when refactored to
    # use arrays instead of sparse matrices, consider an array refactor to this
    # function as well.

    # The eigensolution calculation apparently must be done on a dense matrix,
    # because eig functions on sparse matrices can't return all answers?!
    # Using eigh so that answers have only real components and no residual small
    # unreal components b/c of rounding errors
    E, V = np.linalg.eigh(H)    # V will be eigenvectors, v will be frequencies

    # Eigh still leaves residual 0j terms, so:
    V = np.asmatrix(V.real)

    # Calculate signal intensities
    Vcol = csc_matrix(V)
    Vrow = csr_matrix(Vcol.T)
    m = 2 ** nspins
    T = transition_matrix(m)
    I = Vrow * T * Vcol
    I = np.square(I.todense())

    spectrum = []
    for i in range(m-1):
        for j in range(i+1, m):
            if I[i, j] > 0.01:  # consider making this minimum intensity
                                # cutoff a function arg, for flexibility
                v = abs(E[i] - E[j])
                spectrum.append((v, I[i, j]))

    return spectrum


# noinspection PyUnreachableCode,PyPep8Naming,PyShadowingNames
def nspinspec(freqs, couplings):
    """
    Function that calculates a spectrum for n spin-half nuclei.
    Inputs:
        :param freqs: a list of n nuclei frequencies in Hz
        :param couplings: an n x n array of couplings in Hz. The order
        of nuclei in the list corresponds to the column and row order in the
        matrix, e.g. couplings[0][1] and [1]0] are the J coupling between
        the nuclei of freqs[0] and freqs [1].
    """
    nspins = len(freqs)
    H = hamiltonian(freqs, couplings)
    return simsignals(H, nspins)


##############################################################################
# Non-QM solutions for specific multiplets
##############################################################################


def AB(Jab, Vab, Vcentr, Wa, RightHz, WdthHz):
    """
    Reich-style inputs for AB quartet.
    Jab is the A-B coupling constant (Hz)
    Vab is the difference in nuclei frequencies in the absence of coupling (Hz)
    Vcentr is the frequency for the center of the AB quartet
    Wa is width of peak at half-height (not implemented yet)
    RightHz is the lower frequency limit for the window
    WdthHz is the width of the window in Hz
    return: peaklist of (frequency, intensity) tuples
    """
    J = Jab
    dv = Vab
    c = ((dv ** 2 + J ** 2) ** 0.5) / 2
    center = Vcentr
    v1 = center - c - (J / 2)
    v2 = v1 + J
    v3 = center + c - (J / 2)
    v4 = v3 + J
    dI = J / (2 * c)
    I1 = 1 - dI
    I2 = 1 + dI
    I3 = I2
    I4 = I1
    vList = [v1, v2, v3, v4]
    IList = [I1, I2, I3, I4]
    return list(zip(vList, IList))


def AB2(J, dV, Vab, Wa, RightHz, WdthHz):
    """
    Reich-style inputs for AB2 spin system.
    Jab is the A-B coupling constant (Hz)
    Vab is the difference in nuclei frequencies in the absence of coupling (Hz)
    Vcentr is the frequency for the center of the AB2 signal
    Wa is width of peak at half-height (not implemented yet)
    RightHz is the lower frequency limit for the window
    WdthHz is the width of the window in Hz
    return: peaklist of (frequency, intensity) tuples
    """
    # for now, old Jupyter code using Pople equations kept hashed out for now
    # Reich vs. Pople variable names are confused, e.g. Vab
    # So, variables being placed by position in the def header--CAUTION
    # From main passed in order of: Jab, Vab, Vcentr, Wa, RightHz, WdthHz
    # Here read in as:              J,   dV,  Vab,    "     "        "
    #dV = va - vb  # Reich: used d = Vb - vA and then mucked with sign of d
    #Vab = (va + vb) / 2  # Reich: ABOff
    dV = - dV
    va = Vab + (dV / 2)
    vb = va - dV
    Jmod = J * (3 / 4)  # This factor used in frequency calculations

    # In Reich's code, the definitions of cp/cm (for C_plus/C_minus) were
    # swapped, and then modifications using sign of d were employed. This
    # code hews closer to Pople definitions
    C_plus = sqrt(dV ** 2 + dV * J + (9 / 4) * (J ** 2)) / 2
    C_minus = sqrt(dV ** 2 - dV * J + (9 / 4) * (J ** 2)) / 2

    sin2theta_plus = J / (sqrt(2) * C_plus)  # Reich: sin2x
    sin2theta_minus = J / (sqrt(2) * C_minus)  # Reich: sin2y
    cos2theta_plus = (dV / 2 + J / 4) / C_plus  # Reich: cos2x
    cos2theta_minus = (dV / 2 - J / 4) / C_minus  # Reich: cos2y

    # This code differs from Reich's in the calculation of
    # the sin/cos x/y values

    sintheta_plus = sqrt((1 - cos2theta_plus) / 2)  # Reich: sinx
    sintheta_minus = sqrt((1 - cos2theta_minus) / 2)  # Reich: siny
    costheta_plus = sqrt((1 + cos2theta_plus) / 2)  # Reich: cosx
    costheta_minus = sqrt((1 + cos2theta_minus) / 2)  # Reich: cosy

    # Intensity formulas use the sin and cos of (theta_plus - theta_minus)
    # sin_dtheta is Reich's qq; cos_dtheta is Reich's rr

    sin_dtheta = sintheta_plus * costheta_minus - costheta_plus * sintheta_minus
    cos_dtheta = costheta_plus * costheta_minus + sintheta_plus * sintheta_minus

    # Calculate the frequencies and intensities.
    # V1-V4 are "Origin: A" (PSB Table 6-8);
    # V5-V8 are "Origin: B";
    # V9-V12 are "Origin: Comb."

    V1 = Vab + Jmod + C_plus
    V2 = vb + C_plus + C_minus
    V3 = va
    V4 = Vab - Jmod + C_minus
    V5 = vb + C_plus - C_minus
    V6 = Vab + Jmod - C_plus
    V7 = vb - C_plus + C_minus
    V8 = Vab - Jmod - C_minus
    V9 = vb - C_plus - C_minus

    I1 = (sqrt(2)*sintheta_plus - costheta_plus) ** 2
    I2 = (sqrt(2)*sin_dtheta + costheta_plus*costheta_minus) ** 2
    I3 = 1
    I4 = (sqrt(2)*sintheta_minus + costheta_minus) ** 2
    I5 = (sqrt(2)*cos_dtheta + costheta_plus*sintheta_minus) ** 2
    I6 = (sqrt(2)*costheta_plus + sintheta_plus) ** 2
    I7 = (sqrt(2)*cos_dtheta - sintheta_plus*costheta_minus) ** 2
    I8 = (sqrt(2)*costheta_minus - sintheta_minus) ** 2
    I9 = (sqrt(2)*sin_dtheta + sintheta_plus*sintheta_minus) ** 2
    vList = [V1, V2, V3, V4, V5, V6, V7, V8, V9]
    IList = [I1, I2, I3, I4, I5, I6, I7, I8, I9]
    return list(zip(vList, IList))


if __name__ == '__main__':
    from nspin import reich_list
    from nmrplot import nmrplot as nmrplt

    test_freqs, test_couplings = reich_list()[8]

    # refactor reich_list to do this!
    #test_couplings = test_couplings.todense()
    #spectrum = nspinspec(test_freqs, test_couplings)
    #nmrplt(nspinspec(test_freqs, test_couplings), y=24)
    ab2test = AB2(7.9, 26.5, 13.25, 0.5, 0, 300)
    nmrplt(ab2test)
    print(ab2test)
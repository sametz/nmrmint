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
    sigma_x = np.matrix([[0, 1 / 2], [1 / 2, 0]])
    sigma_y = np.matrix([[0, -1j / 2], [1j / 2, 0]])
    sigma_z = np.matrix([[1 / 2, 0], [0, -1 / 2]])
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
    # freqs are *2pi, but Js by pi only.
    scalars = 0.5 * couplings
    scalars = np.multiply(scalars, Lproduct)
    for n in range(nspins):
        for k in range(nspins):
            H += scalars[n, k].real

    return H


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
    for i in range(m - 1):
        for j in range(i + 1, m):
            if I[i, j] > 0.01:  # consider making this minimum intensity
                                # cutoff a function arg, for flexibility
                v = abs(E[i] - E[j])
                spectrum.append((v, I[i, j]))

    return spectrum


def nspinspec(freqs, couplings, normalize=True):
    """
    Function that calculates a spectrum for n spin-half nuclei.
    Inputs:
        :param freqs: a list of n nuclei frequencies in Hz
        :param couplings: an n x n array of couplings in Hz. The order
        of nuclei in the list corresponds to the column and row order in the
        matrix, e.g. couplings[0][1] and [1]0] are the J coupling between
        the nuclei of freqs[0] and freqs [1].
        :param normalize: (bool) True if the intensities should be normalized
        so that total intensity equals the total number of nuclei.
    Returns:
    -spectrum: a list of (frequency, intensity) tuples.
    Dependencies: hamiltonian, simsignals
    """
    nspins = len(freqs)
    H = hamiltonian(freqs, couplings)
    spectrum = simsignals(H, nspins)
    if normalize:
        spectrum = normalize_spectrum(spectrum, nspins)
    return spectrum


##############################################################################
# Non-QM solutions for specific multiplets
##############################################################################

# doublet, multiplet, add_peaks, and reduce_peaks are used to generate
# first-order splitting patterns

def doublet(plist, J):
    """
    plist: a list of (frequency{Hz}, intensity) tuples;
    J: a coupling constant {Hz}
    returns: a plist of the result of splitting every peak in plist by J
    """
    res = []
    for v, i in plist:
        res.append((v - J / 2, i / 2))
        res.append((v + J / 2, i / 2))
    return res


def multiplet(plist, couplings):
    """
    plist: a list of (frequency{Hz}, intensity) tuples;
    couplings: one or more (J, # of nuclei) tuples.
    e.g. to split a signal into a dt, J = 8, 5 Hz, use:
        couplings = [(8, 2), (5, 3)]
    Dependency: doublet function
    returns: a plist of the multiplet that results from splitting the plist
    signal(s) by each J.
    The order of the tuples in couplings does not matter
    """
    res = plist
    for coupling in couplings:
        for i in range(coupling[1]):
            res = doublet(res, coupling[0])
    return res


def add_peaks(plist):
    """
    condenses a list of (frequency, intensity) tuples
    input: a list of (v, i) tuples
    output: a tuple of (average v, total i)
    """
    if len(plist) == 1:
        return plist[0]  # nothing to add
    v_total = 0
    i_total = 0
    for v, i in plist:
        v_total += v
        i_total += i
    return v_total / len(plist), i_total


def reduce_peaks(plist, tolerance=0):
    """
    Takes an ordered list of (x, y) tuples and adds together tuples whose first
    values are within a certain tolerance limit.
    Dependency: add_peaks
    Input:
        plist: a *sorted* list of (x, y) tuples (sorted by x)
        tolerance: tuples that differ in x by <= tolerance are combined
        using add_peaks

    Output:
        a list of (x, y) tuples where all x values differ by > tolerance

    """
    res = []
    work = [plist[0]]  # an accumulator of peaks to be processed
    for i in range(1, len(plist)):
        if not work:
            work.append(plist)
            continue
        if plist[i][0] - work[-1][0] <= tolerance:
            work.append(plist[i])  # accumulate close peaks
            continue
        else:
            res.append(add_peaks(work))
            work = [plist[i]]
    if work:
        res.append(add_peaks(work))

    return res


def normalize(intensities, n=1):
    """Scale a list of intensities so that they sum to the total number of
    nuclei.

    :param intensities: [float] A list of intensities.
    :param n: (int) Number of nuclei."""
    factor = n / sum(intensities)
    for index, intensity in enumerate(intensities):
        intensities[index] = intensity * factor


def first_order(signal, couplings):  # Wa, RightHz, WdthHz not implemented yet
    """Uses the above functions to split a signal into a first-order
    multiplet.
    Input:
    -signal: a (frequency, intensity) tuple
    -Couplings: a list of (J, # of nuclei) tuples. See multiplet
    docstring for more info.
    -intensity (optional): the intensity of the signal
    Output:
    a plist-style spectrum (list of (frequency, intensity) tuples)
    Dependencies: doublet, multiplet, reduce_peaks, add_peaks
    """
    # Possible future refactor: if function used a list of signals,
    # may be useful in other situations?
    signallist = [signal]
    return reduce_peaks(sorted(multiplet(signallist, couplings)))


def normalize_spectrum(spectrum, n=1):
    """Normalize the intensities in a spectrum so that total intensity equals
    value n (nominally the number of nuclei giving rise to the signal).

    :param spectrum: [(float, float)...] a list of (frequency, intensity)
    tuples.
    :param n: total intensity to normalize to."""
    freq, int_ = [x for x, y in spectrum], [y for x, y in spectrum]
    normalize(int_, n)
    return list(zip(freq, int_))


def AB(Jab, Vab, Vcentr, **kwargs):  # Wa, RightHz, WdthHz not implemented yet
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

    # nmrmint requires normailization.
    # integration = 1  # hack in hard-coded integration for now
    # I1 *= (integration/2)
    # I2 *= (integration/2)
    I3 = I2
    I4 = I1
    vList = [v1, v2, v3, v4]
    IList = [I1, I2, I3, I4]
    normalize(IList, 2)
    return list(zip(vList, IList))


def AB2(Jab, Vab, Vcentr, **kwargs):  # Wa, RightHz, WdthHz not implemented yet
    """
    Reich-style inputs for AB2 spin system.
    J is the A-B coupling constant (Hz)
    dV is the difference in nuclei frequencies in the absence of coupling (Hz)
    Vab is the frequency for the center of the AB2 signal
    Wa is width of peak at half-height (not implemented yet)
    RightHz is the lower frequency limit for the window (not implemented yet)
    WdthHz is the width of the window in Hz (not implemented yet)
    return: peaklist of (frequency, intensity) tuples
    """
    # Currently, there is a disconnect between the variable names in the GUI
    # and the variable names in this function. The following code provides a
    # temporary interface.

    J, dV, Vab = Jab, Vab, Vcentr

    # for now, old Jupyter code using Pople equations kept hashed out for now
    # Reich vs. Pople variable names are confused, e.g. Vab
    # So, variables being placed by position in the def header--CAUTION
    # From main passed in order of: Jab, Vab, Vcentr, Wa, RightHz, WdthHz
    # Here read in as:              J,   dV,  Vab,    "     "        "
    # dV = va - vb  # Reich: used d = Vb - vA and then mucked with sign of d
    # Vab = (va + vb) / 2  # Reich: ABOff
    dV = - dV
    va = Vab + (dV / 2)
    vb = va - dV
    Jmod = J * (3 / 4)  # This factor used in frequency calculations

    # In Reich's code, the definitions of cp/cm (for C_plus/C_minus) were
    # swapped, and then modifications using sign of d were employed. This
    # code hews closer to Pople definitions
    C_plus = sqrt(dV ** 2 + dV * J + (9 / 4) * (J ** 2)) / 2
    C_minus = sqrt(dV ** 2 - dV * J + (9 / 4) * (J ** 2)) / 2

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

    I1 = (sqrt(2) * sintheta_plus - costheta_plus) ** 2
    I2 = (sqrt(2) * sin_dtheta + costheta_plus * costheta_minus) ** 2
    I3 = 1
    I4 = (sqrt(2) * sintheta_minus + costheta_minus) ** 2
    I5 = (sqrt(2) * cos_dtheta + costheta_plus * sintheta_minus) ** 2
    I6 = (sqrt(2) * costheta_plus + sintheta_plus) ** 2
    I7 = (sqrt(2) * cos_dtheta - sintheta_plus * costheta_minus) ** 2
    I8 = (sqrt(2) * costheta_minus - sintheta_minus) ** 2
    I9 = (sqrt(2) * sin_dtheta + sintheta_plus * sintheta_minus) ** 2
    vList = [V1, V2, V3, V4, V5, V6, V7, V8, V9]
    IList = [I1, I2, I3, I4, I5, I6, I7, I8, I9]
    normalize(IList, 3)
    return list(zip(vList, IList))


def ABX(Jab, Jbx, Jax, Vab, Vcentr, **kwargs):
    # Wa, RightHz, WdthHz not implemented yet
    """
    Reich-style inputs for AB2 spin system.
    Jab is the A-B coupling constant (Hz)
    dV is the difference in nuclei frequencies in the absence of coupling (Hz)
    Vab is the frequency for the center of the AB2 signal
    Wa is width of peak at half-height (not implemented yet)
    RightHz is the lower frequency limit for the window (not implemented yet)
    WdthHz is the width of the window in Hz (not implemented yet)
    return: peaklist of (frequency, intensity) tuples
    """
    # Another function where Reich vs. non-Reich variable names gets confusing
    # See comments in AB2 function
    # So, variables being placed by position in the def header--CAUTION
    # From main passed in order of: Jab, Jax, Jbx, Vab,  Vcentr, ...
    # Here read in as:              Jab, Jbx, Jax, dVab, Vab,    ...

    # CHANGE: with switch to kwargs used in function calls, the following
    # code matches this Reich code to the current view dictionary
    Jbx, Jax = Jax, Jbx
    dVab = Vab
    Vab = Vcentr

    # dVab = va - vb  # Reich: Vab
    # Vab = (va + vb) / 2  # Reich: ABOff

    # Reich's ABX: vx initialized as vb + 100
    vx = Vab - (dVab / 2) + 100

    dJx = Jax - Jbx  # GMS stepping-stone constant for readability

    # Retaining Reich names for next two constants
    cm = dJx / 2
    cp = Jax + Jbx

    # Reich re-defines constants m and l
    # (declaration/garbage-collection efficiency?)
    # GMS: using M and L for the first instance, m and n for second
    # (avoid lower-case l for variables)
    # Reich redefines m a third time for calculating X intensities
    # GMS: uses t

    M = dVab + cm
    L = dVab - cm

    D_plus = sqrt(M ** 2 + Jab ** 2) / 2
    D_minus = sqrt(L ** 2 + Jab ** 2) / 2

    sin2phi_plus = Jab / (2 * D_plus)  # Reich: sin2x
    sin2phi_minus = Jab / (2 * D_minus)  # Reich: sin2y
    cos2phi_plus = M / (2 * D_plus)  # Reich: cos2x
    cos2phi_minus = L / (2 * D_minus)  # Reich: cos2y

    m = (cp + 2 * Jab) / 4
    n = (cp - 2 * Jab) / 4  # Reich: l

    t = cos2phi_plus * cos2phi_minus + sin2phi_plus * sin2phi_minus
    # Calculate the frequencies and intensities.
    # V1-V4 are "Origin: B" (PSB Table 6-15);
    # V5-V8 are "Origin: A";
    # V9-V12 are "Origin: X" and V13-14 are "Origin: Comb. (X)"

    V1 = Vab - m - D_minus
    V2 = Vab + n - D_plus
    V3 = Vab - n - D_minus
    V4 = Vab + m - D_plus
    V5 = Vab - m + D_minus
    V6 = Vab + n + D_plus
    V7 = Vab - n + D_minus
    V8 = Vab + m + D_plus
    V9 = vx - cp / 2
    V10 = vx + D_plus - D_minus
    V11 = vx - D_plus + D_minus
    V12 = vx + cp / 2
    V13 = vx - D_plus - D_minus
    V14 = vx + D_plus + D_minus
    I1 = 1 - sin2phi_minus
    I2 = 1 - sin2phi_plus
    I3 = 1 + sin2phi_minus
    I4 = 1 + sin2phi_plus
    I5 = I3
    I6 = I4
    I7 = I1
    I8 = I2
    I9 = 1
    I10 = (1 + t) / 2
    I11 = I10
    I12 = 1
    I13 = (1 - t) / 2
    I14 = I13
    VList = [V1, V2, V3, V4, V5, V6, V7, V8, V9, V10, V11, V12, V13, V14]
    IList = [I1, I2, I3, I4, I5, I6, I7, I8, I9, I10, I11, I12, I13, I14]
    normalize(IList, 3)
    return list(zip(VList, IList))


def ABX3(Jab, Jax, Jbx, Vab, Vcentr, **kwargs):
    # Wa, RightHz, WdthHz not implemented yet
    """
    Refactoring of Reich's code for simulating the ABX3 system.
    """
    va = Vcentr - Vab / 2
    vb = Vcentr + Vab / 2
    a_quartet = first_order((va, 1), [(Jax, 3)])
    b_quartet = first_order((vb, 1), [(Jbx, 3)])
    res = []
    for i in range(4):
        dv = b_quartet[i][0] - a_quartet[i][0]
        abcenter = (b_quartet[i][0] + a_quartet[i][0]) / 2
        sub_abq = AB(Jab, dv, abcenter)  # Wa, RightHz, WdthHz not implemented
        scale_factor = a_quartet[i][1]
        scaled_sub_abq = [(v, i * scale_factor) for v, i in sub_abq]
        res.extend(scaled_sub_abq)
    return res


def AAXX(Jaa, Jxx, Jax, Jax_prime, Vcentr, **kwargs):
    # Wa, RightHz, WdthHz not implemented yet
    """
    Simulates an AA'XX' spin system. Frequencies and Js in Hz.
    Jaa is the JAA' coupling constant, Jxx the JXX', Jax the JAX,
    and JAX2 the JAX'.
    Vcentr is the frequency for the center of the signal.
    Wa is width of peak at half-height (not implemented yet)
    RightHz is the lower frequency limit for the window
    WdthHz is the width of the window in Hz
    return: peaklist of (frequency, intensity) tuples
    """
    # Define the constants required to calculate frequencies and intensities

    # K, L, M, N are as defined in PSB
    K = Jaa + Jxx  # Reich: K
    M = Jaa - Jxx  # Reich: l
    L = Jax - Jax_prime  # Reich: m
    N = Jax + Jax_prime  # Reich: n

    # Retaining Reich names for next two constants
    # Suggested refactoring: don't divide by 2 here; can simplify later formulas

    p = sqrt((K ** 2 + L ** 2)) / 2
    r = sqrt((M ** 2 + L ** 2)) / 2

    sin2theta_s = (1 - K / (2 * p)) / 2
    sin2theta_a = (1 - M / (2 * r)) / 2
    cos2theta_s = (1 + K / (2 * p)) / 2
    cos2theta_a = (1 + M / (2 * r)) / 2

    # Calculate the frequencies and intensities.
    # See PSB Table 6-18. Transitions 1-4 are condensed into V1 and V2.

    V1 = Vcentr + N / 2
    V2 = Vcentr - N / 2
    V3 = Vcentr + K / 2 + p
    V4 = Vcentr - K / 2 + p
    V5 = Vcentr + K / 2 - p
    V6 = Vcentr - K / 2 - p
    V7 = Vcentr + M / 2 + r
    V8 = Vcentr - M / 2 + r
    V9 = Vcentr + M / 2 - r
    V10 = Vcentr - M / 2 - r

    I1 = 2
    I2 = I1
    I3 = sin2theta_s
    I4 = cos2theta_s
    I5 = I4
    I6 = I3
    I7 = sin2theta_a
    I8 = cos2theta_a
    I9 = I8
    I10 = I7

    VList = [V1, V2, V3, V4, V5, V6, V7, V8, V9, V10]
    IList = [I1, I2, I3, I4, I5, I6, I7, I8, I9, I10]
    normalize(IList, 4)
    return list(zip(VList, IList))


def AABB(Vab, Jaa, Jbb, Jab, Jab_prime, Vcentr, **kwargs):
    # Wa, RightHz, WdthHz not implemented yet
    """
    A wrapper for a second-order AA'BB' calculation, but using the
    values taken from the WINDNMR-style AA'BB' bar selected by the Multiplet
    menu.
    """
    va = Vcentr - Vab / 2
    vb = Vcentr + Vab / 2
    freqlist = [va, va, vb, vb]
    J = np.zeros((4, 4))
    J[0, 1] = Jaa
    J[0, 2] = Jab
    J[0, 3] = Jab_prime
    J[1, 2] = Jab_prime
    J[1, 3] = Jab
    J[2, 3] = Jbb
    J = J + J.T
    return normalize_spectrum(nspinspec(freqlist, J), 4)


def add_spectra(original, additional):
    original.extend(additional)


if __name__ == '__main__':
    from nspin import reich_list
    from nmrplot import nmrplot as nmrplt

    test_freqs, test_couplings = reich_list()[8]

    # refactor reich_list to do this!
    # test_couplings = test_couplings.todense()
    # spectrum = nspinspec(test_freqs, test_couplings)
    # nmrplt(nspinspec(test_freqs, test_couplings), y=24)
    # ab2test = AB2(7.9, 26.5, 13.25, 0.5, 0, 300)
    # abxtest = ABX(12.0, 2.0, 8.0, 15.0, 7.5, 0.5, 0, 300)
    # nmrplt(abxtest)
    # print(abxtest)

    # v1 = (1200, 2)
    # v2 = (450, 2)
    # v3 = (300, 3)
    # J12 = 7
    # J23 = 7
    # m1 = first_order(v1, [(J12, 2)])
    # m2 = first_order(v2, [(J12, 2), (J23, 3)])
    # m3 = first_order(v3, [(J23, 2)])
    # testspec = reduce_peaks(sorted(m1 + m2 + m3))
    # print(testspec)
    # nmrplt(testspec)
    # nmrplt(m1)
    # # print(m2)
    # nmrplt(m2)
    # nmrplt(m3)

    # m1 = multiplet(v1, [(J12, 2)])
    # m2 = multiplet(v2, [(J12, 2), (J23, 3)])
    # m3 = multiplet(v3, [(J23, 2)])
    #
    # testspec = sorted(m1 + m2 + m3)
    # print(testspec)
    # nmrplt(testspec)
    # nmrplt(m1)
    # nmrplt(m2)
    # nmrplt(m3)
    # abx3spec = ABX3(-12.0, 7.0, 7.0, 14.0, 150.0, 0.5, 0.0, 300.0)
    # nmrplt(abx3spec)
    # aaxxspec = AAXX(15, -10, 40, 6, 150, 0.5, 0, 300)
    # print(sorted(aaxxspec))
    # nmrplt(aaxxspec)
    aabbspec = AABB(40, 15, -10, 40, 6, 150, 0.5, 0, 300)
    print(sorted(aabbspec))
    nmrplt(aabbspec)

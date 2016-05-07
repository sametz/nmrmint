from nmrmath import *
import numpy as np
from scipy.sparse import lil_matrix
from scipy.linalg import eigh

# The attempt to put pytest code in a class failed. For whatever reason,
# pytest could not detect the tests within the class. Reserved for potential
# future use.
# class TestSecOrder:
#     """
#     Tests the functions required for second order calculation of systems of
#     n spin-1/2 nuclei. The 3-spin system used in the Frank Rioux PDF is
#     simulated and checked against his numbers.
#     """
#
#     def __init__(self):
#         """
#         Initializing test routine with the Rioux data and results.
#         """
#         freqlist = [430, 265, 300]  # nuclei frequencies (Hz)
#
#         J = lil_matrix((3, 3))      # J couplings
#         J[0, 1] = 7
#         J[0, 2] = 15
#         J[1, 2] = 1.5
#         J = J + J.T
#
#         # Frequencies (eigenvalues) of simulation result
#         v = [-491.625, -230.963, -200.306, -72.106, 61.883, 195.524, 234.217,
#              503.375]
#
#         # Transition probability matrix
#         T = np.array([
#             [0, 1, 1, 0, 1, 0, 0, 0],
#             [1, 0, 0, 1, 0, 1, 0, 0],
#             [1, 0, 0, 1, 0, 0, 1, 0],
#             [0, 1, 1, 0, 0, 0, 0, 1],
#             [1, 0, 0, 0, 0, 1, 1, 0],
#             [0, 1, 0, 0, 1, 0, 0, 1],
#             [0, 0, 1, 0, 1, 0, 0, 1],
#             [0, 0, 0, 1, 0, 1, 1, 0]
#         ])
#         # Final spectrum as list of (frequency, intensity) tuples
#         refspec = [(260.66152857482973, 0.92044386594717353),
#                    (262.18930344673686, 0.99503587544800565),
#                    (267.62991550888137, 0.99421657034922251),
#                    (269.15769038078849, 1.0902494458059944),
#                    (291.31911366903159, 0.91527406734942929),
#                    (292.84688854093866, 0.85524357901564929),
#                    (306.32295186307283, 1.1700594579603014),
#                    (307.85072673497996, 1.0594650613364776),
#                    (419.51935775613867, 1.1642820667033968),
#                    (426.48774469019031, 1.0651876493998582),
#                    (434.52319595017991, 0.92017735031402692),
#                    (441.49158288423155, 0.85028549285752886)]
#
#     def test_nlist(self):
#         assert nlist(3) == [[], [], []]
#         assert nlist(1) == [[]]
#         assert nlist(0) == []
#
#     def test_popcount(self):
#         assert popcount(0) == 0
#         for n in range(1, 10):
#             assert popcount(2 ** n) == 1
#
#     def test_is_allowed(self):
#         assert is_allowed(0, 0) == False
#         assert is_allowed(0, 3) == False
#         assert is_allowed(0, 1) == True
#         assert is_allowed(255, 254) == True
#
#     def test_transition_matrix(self):
#         np.testing.assert_array_equal(T, transition_matrix(8).toarray())
#
#     def test_hamiltonian(self):
#         H = hamiltonian(freqlist, J)
#         eigvals = eigh(H.todense(), eigvals_only=True)
#         np.testing.assert_array_equal(eigvals, sorted(eigvals))
#         np.testing.assert_array_almost_equal(eigvals, v, decimal=3)
#
#     def test_simsignals(self):
#         testspec = sorted(simsignals(hamiltonian(freqlist, J), 3))
#         np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_popcount():
    assert popcount(0) == 0
    for n in range(1, 10):
        assert popcount(2 ** n) == 1


def test_is_allowed():
    assert is_allowed(0, 0) == False
    assert is_allowed(0, 3) == False
    assert is_allowed(0, 1) == True
    assert is_allowed(255, 254) == True


def test_transition_matrix():
    T = np.array([
        [0, 1, 1, 0, 1, 0, 0, 0],
        [1, 0, 0, 1, 0, 1, 0, 0],
        [1, 0, 0, 1, 0, 0, 1, 0],
        [0, 1, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 0, 1],
        [0, 0, 1, 0, 1, 0, 0, 1],
        [0, 0, 0, 1, 0, 1, 1, 0]
    ])
    np.testing.assert_array_equal(T, transition_matrix(8).toarray())


def test_hamiltonian():
    freqlist = [430, 265, 300]
    freqarray = np.array(freqlist)
    J = np.zeros((3, 3))
    J[0, 1] = 7
    J[0, 2] = 15
    J[1, 2] = 1.5
    J = J + J.T
    # print(freqlist)
    # print(J.todense())
    v = [-491.625, -230.963, -200.306, -72.106, 61.883, 195.524, 234.217,
         503.375]
    H = hamiltonian(freqarray, J)
    # print(H).real
    eigvals = np.linalg.eigvals(H)
    eigvals.sort()
    np.testing.assert_array_equal(eigvals, sorted(eigvals))
    np.testing.assert_array_almost_equal(eigvals, v, decimal=3)


def test_simsignals():
    refspec = [(260.66152857482973, 0.92044386594717353),
               (262.18930344673686, 0.99503587544800565),
               (267.62991550888137, 0.99421657034922251),
               (269.15769038078849, 1.0902494458059944),
               (291.31911366903159, 0.91527406734942929),
               (292.84688854093866, 0.85524357901564929),
               (306.32295186307283, 1.1700594579603014),
               (307.85072673497996, 1.0594650613364776),
               (419.51935775613867, 1.1642820667033968),
               (426.48774469019031, 1.0651876493998582),
               (434.52319595017991, 0.92017735031402692),
               (441.49158288423155, 0.85028549285752886)]
    freqlist = [430, 265, 300]
    freqarray = np.array(freqlist)
    J = np.zeros((3, 3))
    J[0, 1] = 7
    J[0, 2] = 15
    J[1, 2] = 1.5
    J = J + J.T
    H = hamiltonian(freqarray, J)
    testspec = sorted(simsignals(H, 3))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_doublet():
    refspec = [(95, 0.5), (105, 0.5)]
    testspec = sorted(doublet([(100, 1)], 10))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_multiplet():
    # Inputs: simulate n-propanol
    refspec = sorted([
        (1193.0, 0.5), (1200.0, 0.5), (1200.0, 0.5), (1207.0, 0.5),
        (432.5, 0.0625), (439.5, 0.0625), (439.5, 0.0625),
        (446.5, 0.0625), (439.5, 0.0625), (446.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (439.5, 0.0625),
        (446.5, 0.0625), (446.5, 0.0625), (453.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (453.5, 0.0625),
        (460.5, 0.0625), (439.5, 0.0625), (446.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (446.5, 0.0625),
        (453.5, 0.0625), (453.5, 0.0625), (460.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (453.5, 0.0625),
        (460.5, 0.0625), (453.5, 0.0625), (460.5, 0.0625),
        (460.5, 0.0625), (467.5, 0.0625),
        (293.0, 0.75), (300.0, 0.75), (300.0, 0.75), (307.0, 0.75)])
    v1 = [(1200, 2)]
    v2 = [(450, 2)]
    v3 = [(300, 3)]
    J12 = 7
    J23 = 7
    m1 = multiplet(v1, [(J12, 2)])
    m2 = multiplet(v2, [(J12, 2), (J23, 3)])
    m3 = multiplet(v3, [(J23, 2)])

    testspec = sorted(m1 + m2 + m3)
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_reduce_peaks():
    refspec = [(293.0, 0.75), (300.0, 1.5), (307.0, 0.75),
               (432.5, 0.0625), (439.5, 0.3125), (446.5, 0.625),
               (453.5, 0.625), (460.5, 0.3125), (467.5, 0.0625),
               (1193.0, 0.5), (1200.0, 1.0), (1207.0, 0.5)]
    tobereduced = sorted([
        (1193.0, 0.5), (1200.0, 0.5), (1200.0, 0.5), (1207.0, 0.5),
        (432.5, 0.0625), (439.5, 0.0625), (439.5, 0.0625),
        (446.5, 0.0625), (439.5, 0.0625), (446.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (439.5, 0.0625),
        (446.5, 0.0625), (446.5, 0.0625), (453.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (453.5, 0.0625),
        (460.5, 0.0625), (439.5, 0.0625), (446.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (446.5, 0.0625),
        (453.5, 0.0625), (453.5, 0.0625), (460.5, 0.0625),
        (446.5, 0.0625), (453.5, 0.0625), (453.5, 0.0625),
        (460.5, 0.0625), (453.5, 0.0625), (460.5, 0.0625),
        (460.5, 0.0625), (467.5, 0.0625),
        (293.0, 0.75), (300.0, 0.75), (300.0, 0.75), (307.0, 0.75)
    ])
    testspec = sorted(reduce_peaks(tobereduced))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_first_order():
    refspec = [(293.0, 0.75), (300.0, 1.5), (307.0, 0.75),
               (432.5, 0.0625), (439.5, 0.3125), (446.5, 0.625),
               (453.5, 0.625), (460.5, 0.3125), (467.5, 0.0625),
               (1193.0, 0.5), (1200.0, 1.0), (1207.0, 0.5)]
    v1 = (1200, 2)
    v2 = (450, 2)
    v3 = (300, 3)
    J12 = 7
    J23 = 7
    m1 = first_order(v1, [(J12, 2)])
    m2 = first_order(v2, [(J12, 2), (J23, 3)])
    m3 = first_order(v3, [(J23, 2)])
    testspec = reduce_peaks(sorted(m1 + m2 + m3))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_AB():
    from reichdefaults import ABdict
    refspec = [(134.39531364385073, 0.3753049524455757),
               (146.39531364385073, 1.6246950475544244),
               (153.60468635614927, 1.6246950475544244),
               (165.60468635614927, 0.3753049524455757)]
    Jab = ABdict['Jab']
    Vab = ABdict['Vab']
    Vcentr = ABdict['Vcentr']
    Wa = ABdict['Wa']
    RightHz = ABdict['Right-Hz']
    WdthHz = ABdict['WdthHz']
    testspec = AB(Jab, Vab, Vcentr, Wa, RightHz, WdthHz)
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_AB2():
    from reichdefaults import dcp
    refspec = [(-8.892448165479056, 0.5434685012269458),
               (-2.300397938882746, 0.7780710767178313),
               (0.0, 1),
               (6.59205022659631, 1.6798068052995172),
               (22.865501607924635, 2.6784604220552235),
               (23.542448165479055, 2.4565314987730544),
               (30.134498392075365, 1.5421221179826525),
               (31.75794977340369, 1.3201931947004837),
               (55.300397938882746, 0.001346383244293953)]

    Jab = dcp['Jab']
    Vab = dcp['Vab']
    Vcentr = dcp['Vcentr']
    Wa = dcp['Wa']
    RightHz = dcp['Right-Hz']
    WdthHz = dcp['WdthHz']
    testspec = AB2(Jab, Vab, Vcentr, Wa, RightHz, WdthHz)
    np.testing.assert_array_almost_equal(sorted(testspec), refspec, decimal=2)


def test_ABX():
    from reichdefaults import ABXdict
    refspec = sorted([(-9.48528137423857, 0.2928932188134524),
                      (-6.816653826391969, 0.44529980377477096),
                      (2.5147186257614305, 1.7071067811865475),
                      (5.183346173608031, 1.554700196225229),
                      (7.4852813742385695, 1.7071067811865475),
                      (14.816653826391969, 1.554700196225229),
                      (19.485281374238568, 0.2928932188134524),
                      (26.81665382639197, 0.44529980377477096),
                      (95.0, 1),
                      (102.3313724521534, 0.9902903378454601),
                      (97.6686275478466, 0.9902903378454601),
                      (105.0, 1),
                      (80.69806479936946, 0.009709662154539944),
                      (119.30193520063054, 0.009709662154539944)])
    Jab = ABXdict['Jab']
    Jax = ABXdict['Jax']
    Jbx = ABXdict['Jbx']
    Vab = ABXdict['Vab']
    Vcentr = ABXdict['Vcentr']
    Wa = ABXdict['Wa']
    RightHz = ABXdict['Right-Hz']
    WdthHz = ABXdict['WdthHz']
    testspec = sorted(ABX(Jab, Jax, Jbx, Vab, Vcentr, Wa, RightHz, WdthHz))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_AMX3():
    from reichdefaults import AMX3dict
    refspec = sorted(
        [(136.2804555427071, 0.20634892168199606),
         (143.2804555427071, 0.6190467650459882),
         (150.2804555427071, 0.6190467650459882),
         (157.2804555427071, 0.20634892168199606),
         (124.2804555427071, 0.04365107831800394),
         (131.2804555427071, 0.13095323495401182),
         (138.2804555427071, 0.13095323495401182),
         (145.2804555427071, 0.04365107831800394),
         (154.7195444572929, 0.04365107831800394),
         (161.7195444572929, 0.13095323495401182),
         (168.7195444572929, 0.13095323495401182),
         (175.7195444572929, 0.04365107831800394),
         (142.7195444572929, 0.20634892168199606),
         (149.7195444572929, 0.6190467650459882),
         (156.7195444572929, 0.6190467650459882),
         (163.7195444572929, 0.20634892168199606)]

    )
    Jab = AMX3dict['Jab']
    Jax = AMX3dict['Jax']
    Jbx = AMX3dict['Jbx']
    Vab = AMX3dict['Vab']
    Vcentr = AMX3dict['Vcentr']
    Wa = AMX3dict['Wa']
    RightHz = AMX3dict['Right-Hz']
    WdthHz = AMX3dict['WdthHz']

    testspec = sorted(AMX3(Jab, Jax, Jbx, Vab, Vcentr, Wa, RightHz, WdthHz))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_ABX3():
    from reichdefaults import ABX3dict
    refspec = (
        [(124.2804555427071, 0.04365107831800394),
         (131.2804555427071, 0.13095323495401182),
         (136.2804555427071, 0.20634892168199606),
         (138.2804555427071, 0.13095323495401182),
         (142.7195444572929, 0.20634892168199606),
         (143.2804555427071, 0.6190467650459882),
         (145.2804555427071, 0.04365107831800394),
         (149.7195444572929, 0.6190467650459882),
         (150.2804555427071, 0.6190467650459882),
         (154.7195444572929, 0.04365107831800394),
         (156.7195444572929, 0.6190467650459882),
         (157.2804555427071, 0.20634892168199606),
         (161.7195444572929, 0.13095323495401182),
         (163.7195444572929, 0.20634892168199606),
         (168.7195444572929, 0.13095323495401182),
         (175.7195444572929, 0.04365107831800394)]
    )
    Jab = ABX3dict['Jab']
    Jax = ABX3dict['Jax']
    Jbx = ABX3dict['Jbx']
    Vab = ABX3dict['Vab']
    Vcentr = ABX3dict['Vcentr']
    Wa = ABX3dict['Wa']
    RightHz = ABX3dict['Right-Hz']
    WdthHz = ABX3dict['WdthHz']

    testspec = sorted(ABX3(Jab, Jax, Jbx, Vab, Vcentr, Wa, RightHz, WdthHz))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_AAXX():
    from reichdefaults import AAXXdict
    refspec = sorted(
        [(173.0, 2), (127.0, 2), (169.6828402774396, 0.4272530047525843),
         (164.6828402774396, 0.5727469952474157),
         (135.3171597225604, 0.5727469952474157),
         (130.3171597225604, 0.4272530047525843),
         (183.6009478460092, 0.20380477476124093),
         (158.6009478460092, 0.7961952252387591),
         (141.3990521539908, 0.7961952252387591),
         (116.39905215399081, 0.20380477476124093)]
    )
    Jaa = AAXXdict["Jaa'"]
    Jxx = AAXXdict["Jxx'"]
    Jax = AAXXdict["Jax"]
    Jax_prime = AAXXdict["Jax'"]
    Vcentr = AAXXdict['Vcentr']
    Wa = AAXXdict['Wa']
    RightHz = AAXXdict['Right-Hz']
    WdthHz = AAXXdict['WdthHz']

    testspec = sorted(AAXX(Jaa, Jxx, Jax, Jax_prime, Vcentr,
                           Wa, RightHz, WdthHz))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


def test_AABB():
    from reichdefaults import AABBdict
    refspec = (
        [(92.22140228380421, 0.10166662880050205),
         (96.52049869174374, 0.49078895567299158),
         (98.198417381432606, 0.24246823712843479),
         (101.65157834035199, 0.60221210650067936),
         (106.27391102440463, 0.32609441972096737),
         (110.31814797792887, 0.50200815047635172),
         (132.76708635908275, 0.7056360644549744),
         (134.42329797582249, 1.8983333711994956),
         (140.8425800020548, 1.5528911909909029),
         (142.5204986917436, 3.5092110443270066),
         (144.57608469738022, 4.560944163972513),
         (147.47995633005294, 1.4979918495236497),
         (152.52004366994717, 1.4979918495236475),
         (155.42391530261983, 4.5609441639725166),
         (157.47950130825635, 3.5092110443270097),
         (159.1574199979452, 1.5528911909909029),
         (165.57670202417737, 1.8983333711994945),
         (167.2329136409173, 0.70563606445497351),
         (189.68185202207124, 0.50200815047635128),
         (193.72608897559536, 0.32609441972096725),
         (198.34842165964801, 0.6022121065006798),
         (201.80158261856747, 0.24246823712843413),
         (203.47950130825626, 0.49078895567299208),
         (207.77859771619566, 0.10166662880050205)]
    )
    Vab = AABBdict["Vab"]
    Jaa = AABBdict["Jaa'"]
    Jbb = AABBdict["Jbb'"]
    Jab = AABBdict["Jab"]
    Jab_prime = AABBdict["Jab'"]
    Vcentr = AABBdict["Vcentr"]
    Wa = AABBdict['Wa']
    RightHz = AABBdict['Right-Hz']
    WdthHz = AABBdict['WdthHz']
    testspec = sorted(AABB(Vab, Jaa, Jbb, Jab, Jab_prime, Vcentr,
                           Wa, RightHz, WdthHz))
    np.testing.assert_array_almost_equal(testspec, refspec, decimal=2)


# def test_derp():
#     assert 1 + 1 == 3

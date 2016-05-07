"""
Reich default values for multiplet calculations. Consider merging with nspin.py
"""

ABdict = {'Jab': 12.0,
          'Vab': 15.0,
          'Vcentr': 150.0,
          'Wa': 0.5, 'Right-Hz': 0, 'WdthHz': 300}

AB2dict = {'Jab': 12.0,
           'Vab': 15.0,
           'Vcentr': 150.0,
           'Wa': 0.5, 'Right-Hz': 0, 'WdthHz': 300}

# for expediency, including the 2,6-dichlorophenol AB2 for test_nmrmath
dcp = {'Jab': 7.9,
        'Vab': 26.5,
        'Vcentr': 13.25,
        'Wa': 0.5, 'Right-Hz': 0, 'WdthHz': 300}

ABXdict = {'Jab': 12.0,
           'Jax': 2.0,
           'Jbx': 8.0,
           'Vab': 15.0,
           'Vcentr': 7.5,
           'Wa': 0.5, 'Right-Hz': 0, 'WdthHz': 300}

AMX3dict = {'Jab': -12.0,
            'Jax': 7.0,
            'Jbx': 7.0,
            'Vab': 14.0,
            'Vcentr': 150,
            'Wa': 0.5, 'Right-Hz': 0, 'WdthHz': 300}

ABX3dict = {'Jab': -12.0,
            'Jax': 7.0,
            'Jbx': 7.0,
            'Vab': 14.0,
            'Vcentr': 150,
            'Wa': 0.5, 'Right-Hz': 0, 'WdthHz': 300}

AAXXdict = {"Jaa'": 15.0,
            "Jxx'": -10.0,
            "Jax": 40.0,
            "Jax'": 6.0,
            'Vcentr': 150,
            'Wa': 0.5, 'Right-Hz': 0, 'WdthHz': 300}

AABBdict = {"Vab": 40,
            "Jaa'": 15.0,
            "Jbb'": -10.0,
            "Jab": 40.0,
            "Jab'": 6.0,
            'Vcentr': 150,
            'Wa': 0.5, 'Right-Hz': 0, 'WdthHz': 300}

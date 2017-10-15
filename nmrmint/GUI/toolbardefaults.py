"""
Passing defaults as ordereddict might allow for a concise refactoring of
toolbars, because widgets could be added in the same order as in the
ordereddict. However, Wa, Right-Hz and WdthHz are not implemented yet. This
file is being retained for now, just in case.
"""
from collections import OrderedDict

ABdict = OrderedDict([('Jab', 12.0),
                      ('Vab', 15.0),
                      ('Vcentr', 150.0),
                      ('Wa', 0.5), ('Right-Hz', 0), ('WdthHz', 300)])

AB2dict = OrderedDict([('Jab', 12.0),
                       ('Vab', 15.0),
                       ('Vcentr', 150.0),
                       ('Wa', 0.5), ('Right-Hz', 0), ('WdthHz', 300)])

# for expediency, including the 2,6-dichlorophenol AB2 for test_nmrmath
dcp = OrderedDict[('Jab', 7.9),
                  ('Vab', 26.5),
                  ('Vcentr', 13.25),
                  ('Wa', 0.5),
                  ('Right-Hz', 0),
                  ('WdthHz', 300)]

ABXdict = OrderedDict[('Jab', 12.0),
                      ('Jax', 2.0),
                      ('Jbx', 8.0),
                      ('Vab', 15.0),
                      ('Vcentr', 7.5),
                      ('Wa', 0.5),
                      ('Right-Hz', 0),
                      ('WdthHz', 300)]

AMX3dict = OrderedDict[('Jab', -12.0),
                       ('Jax', 7.0),
                       ('Jbx', 7.0),
                       ('Vab', 14.0),
                       ('Vcentr', 150),
                       ('Wa', 0.5),
                       ('Right-Hz', 0),
                       ('WdthHz', 300)]

ABX3dict = OrderedDict[('Jab', -12.0),
                       ('Jax', 7.0),
                       ('Jbx', 7.0),
                       ('Vab', 14.0),
                       ('Vcentr', 150),
                       ('Wa', 0.5),
                       ('Right-Hz', 0),
                       ('WdthHz', 300)]

AAXXdict = OrderedDict[("Jaa", 15.0),
                       ("Jxx", -10.0),
                       ("Jax", 40.0),
                       ("Jax_prime", 6.0),
                       ('Vcentr', 150),
                       ('Wa', 0.5),
                       ('Right-Hz', 0),
                       ('WdthHz', 300)]

AABBdict = OrderedDict[("Vab", 40),
                       ("Jaa", 15.0),
                       ("Jbb", -10.0),
                       ("Jab", 40.0),
                       ("Jab_prime", 6.0),
                       ('Vcentr', 150),
                       ('Wa', 0.5),
                       ('Right-Hz', 0),
                       ('WdthHz', 300)]

# Potential refactor idea: toolbars.MultipletBar takes kwargs of:
# model: (str) The calculation type
# vars: (OrderedDict): key, val = name (str), number (int or float)
ab_kwargs = {'model': 'AB', 'vars': ABdict}

if __name__ == '__main__':
    print(ab_kwargs)

"""Provide components required for tests.

For now this is a hack that involves instantiating the app so that Controller
can create data. Should instead save test data in some form for later
retrieval.
"""

import tkinter as tk

from nmrmint.controller.controller import Controller

first_order_defaults = {'JAX': 7.00,
                        '#A': 2,
                        'JBX': 3.00,
                        '#B': 1,
                        'JCX': 2.00,
                        '#C': 0,
                        'JDX': 7,
                        '#D': 0,
                        'Vcentr': 0.5,
                        '# of nuclei': 1,
                        'width': 0.5}

root = tk.Tk()
controller = Controller(root)


def blank_spectrum():
    return controller.blank_total_spectrum()


def first_order_default_spec():
    return controller.lineshape_data('first_order',
                                     first_order_defaults)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    plt.plot(*first_order_default_spec())
    plt.show()

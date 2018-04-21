import pytest

from nmrmint.GUI.history import Subspectrum, History
from nmrmint.GUI.toolbars import FirstOrderBar

VARS_DEFAULT = {'JAX': 7.0,
              '#A': 2,
              'JBX': 3.0,
              '#B': 1,
              'JCX': 2.0,
              '#C': 0,
              'JDX': 7,
              '#D': 0,
              'Vcentr': 0.5,
              '# of nuclei': 1,
              'width': 0.5}

VARS_1 = VARS_DEFAULT.copy()
assert VARS_1 == VARS_DEFAULT
assert VARS_1 is not VARS_DEFAULT
VARS_1['#C'] = 2
assert VARS_1 != VARS_DEFAULT

VARS_2 = VARS_DEFAULT.copy()
VARS_2['#B'] = 0
VARS_2['Vcentr'] = 1.0
print('1: ', VARS_1)
print('2: ', VARS_2)


def fake_controller(*args):
    """For mocking out Toolbar controller calls."""
    print('Controller was passed: ', *args)
    pass


def create_ss(bar):
    """Given a toolbar, instantiate a subspectrum with that toolbar.

    :param bar: a GUI.ToolBar subclass
    :return: Subspectrum
    """
    ss = Subspectrum()
    ss.toolbar = bar
    ss.model = bar.model
    ss.vars = bar.vars
    return ss


def create_ss1():
    bar1 = FirstOrderBar(controller=fake_controller)
    bar1.reset(VARS_1)
    ss1 = create_ss(bar1)
    return ss1


def test_initialization():
    assert VARS_1 != VARS_2
    assert VARS_1['#C'] == 2
    assert VARS_2['#B'] == 0
    assert VARS_2['Vcentr'] == 1.0


def test_create_ss1():
    ss = create_ss1()
    assert ss.model == ss.toolbar.model
    assert ss.vars == ss.toolbar.vars
    assert ss.vars['#C'] == 2


def test_history_instantiates_with_blank_subspectrum():
    history = History()
    assert not history.current_subspectrum().active


def test_current_bar():
    history = History()
    bar = FirstOrderBar()
    history.subspectra[history.current].toolbar = bar
    assert history.current_toolbar() is bar


def test_history_refreshed_between_tests():
    history = History()
    assert not history.current_toolbar()

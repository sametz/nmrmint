import numpy as np
import pytest

from nmrmint.GUI.history import Subspectrum, History
from nmrmint.GUI.toolbars import FirstOrderBar, SecondOrderBar

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

# Before writing this test, the program was being manually debugged by first
# changing #C to 2, adding the current to the total plot, then creating a new
# plot with #B changed to 0 and Vcentr changed to 1.0. The test suites adopt
# this arbitrary approach.

VARS_1 = VARS_DEFAULT.copy()
assert VARS_1 == VARS_DEFAULT  # sanity check that .copy() works as expected
assert VARS_1 is not VARS_DEFAULT  # sanity check that they don't refer to same
VARS_1['#C'] = 2
assert VARS_1 != VARS_DEFAULT  # another sanity check

VARS_2 = VARS_DEFAULT.copy()
VARS_2['#B'] = 0
VARS_2['Vcentr'] = 1.0

x1 = np.linspace(1.0, 10.0, 10)
y1 = np.linspace(0.1, 1.0, 10)
x2 = np.linspace(1.0, 10.0, 10)
y2 = np.linspace(100.0, 1000.0, 10)
y_total = np.array([100.1, 200.2, 300.3, 400.4, 500.5, 600.6, 700.7, 800.8,
                    900.9, 1001.0])


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
    """Create a subspectrum for our first test case.
    :return: Subspectrum,
        with .toolbar FirstorderBar,
        with .vars VARS_1
    """
    bar1 = FirstOrderBar(controller=fake_controller)
    bar1.reset(VARS_1)
    ss1 = create_ss(bar1)
    return ss1


def create_ss2():
    """Create a subspectrum for our first test case.
    :return: Subspectrum,
        with .toolbar FirstorderBar,
        with .vars VARS_2
    """
    bar2 = FirstOrderBar(controller=fake_controller)
    bar2.reset(VARS_2)
    ss2 = create_ss(bar2)
    return ss2


def test_initialization():
    """A sanity test to check that the test vars were set up correctly."""
    assert VARS_1 != VARS_2
    assert VARS_1['#C'] == 2
    assert VARS_2['#B'] == 0
    assert VARS_2['Vcentr'] == 1.0


def test_create_ss1():
    """A sanity test to check that ss1 is working correctly."""
    ss = create_ss1()
    assert ss.model == ss.toolbar.model
    assert ss.vars == ss.toolbar.vars
    assert ss.vars['#C'] == 2


def test_create_ss2():
    """A sanity test to check that ss2 is working correctly."""
    ss = create_ss2()
    assert ss.model == ss.toolbar.model
    assert ss.vars == ss.toolbar.vars
    assert ss.vars['#B'] == 0
    assert ss.vars['#C'] == 0
    assert ss.vars['Vcentr'] == 1.0


def test_history_instantiates_with_blank_subspectrum():
    """Tests that when history instantiates it has no assigned subspectra."""
    history = History()
    assert not history.current_subspectrum().active


def test_add_subspectrum():
    """Tests that a new, different subspectrum is added to the
    history.subspectra list."""
    history = History()
    initial_counter = history.current
    history.add_subspectrum()
    final_counter = history.current
    assert final_counter - initial_counter == 1
    assert history.subspectra[final_counter] is not history.subspectra[
        initial_counter]


def test_current_subspectrum():
    """Tests that history.current_subspectrum returns
    history.subspectra[self.current].
    This is a bad test, since it's testing basic functionality like "check a
    + b == a + b", but is here for now as a sanity check.
    """
    history = History()
    history.add_subspectrum()
    assert history.current_subspectrum is not history.subspectra[
        history.current - 1]


def test_subspectrum_data():
    """Tests that subspectrum_data returns a tuple of the current
    subspectrum's (model, vars)
    """
    history = History()
    history.subspectra[0] = create_ss1()
    assert history.subspectrum_data() == ('first_order', VARS_1)
    history.add_subspectrum()
    history.subspectra[1] = create_ss2()
    assert history.subspectrum_data() == ('first_order', VARS_2)


def test_current_toolbar():
    """Tests that current_bar returns the bar for the current subspectrum."""
    history = History()
    bar = FirstOrderBar()
    history.subspectra[history.current].toolbar = bar
    assert history.current_toolbar() is bar


def test_change_toolbar():
    """Tests to see if the current subspectrum's toolbar can be replaced."""
    history = History()
    bar_1 = FirstOrderBar(controller=fake_controller)
    history.current_subspectrum().toolbar = bar_1
    _, vars = history.subspectrum_data()
    assert bar_1.vars == VARS_DEFAULT
    bar_2 = FirstOrderBar(controller=fake_controller)
    bar_2.reset(VARS_1)
    history.change_toolbar(bar_2)
    assert history.current_toolbar() is bar_2
    assert history.current_subspectrum().vars == VARS_1


def test_change_toolbar_to_second_order_bar():
    """Tests to see if change_toolbar works with SecondOrderBar."""
    history = History()
    bar_1 = FirstOrderBar(controller=fake_controller)
    history.current_subspectrum().toolbar = bar_1
    bar_2 = SecondOrderBar(controller=fake_controller)
    assert bar_2.model == 'nspin'
    history.change_toolbar(bar_2)
    _, vars = history.subspectrum_data()
    assert _ == 'nspin'
    assert vars['w'][0][0] == 0.5


def test_back():
    """Tests to see if history.back moves back 1 subspectrum in subspectra
    list.
    """
    history = History()
    ss1 = history.current_subspectrum()
    history.add_subspectrum()
    ss2 = history.current_subspectrum()
    assert ss1 is not ss2
    history.back()
    ss3 = history.current_subspectrum()
    assert ss1 is ss3


def test_back_stops_at_beginning():
    """Tests that if at beginning of history, don't keep moving backwards."""
    history = History()
    subspectra = [history.current_subspectrum()]
    for i in range(2):
        history.add_subspectrum()
        assert history.current == i + 1
        subspectra.append(history.current_subspectrum())
        assert history.current_subspectrum() is not history.subspectra[i]
    history.back()
    assert history.current == 1
    assert history.current_subspectrum() is subspectra[1]
    history.back()
    assert history.current == 0
    assert history.current_subspectrum() is subspectra[0]
    history.back()
    assert history.current == 0
    assert history.current_subspectrum() is subspectra[0]


def test_forward():
    """Tests to see if history.forward moves forward 1 subspectrum in subspectra
    list.
    """
    history = History()
    history.add_subspectrum()
    ss_1 = history.current_subspectrum()
    history.back()
    history.forward()
    assert history.current_subspectrum() is ss_1
    assert history.current == 1


def test_forward_stops_at_end():
    """Tests that if at end of history, don't keep moving forwards."""

    history = History()
    subspectra = [history.current_subspectrum()]
    for i in range(2):
        history.add_subspectrum()
        subspectra.append(history.current_subspectrum())
    for i in range(2):
        history.back()
    assert history.current_subspectrum() is subspectra[0]
    for i in range(2):
        history.forward()
        assert history.current_subspectrum() is subspectra[i + 1]
    assert history.current == 2
    ss_2 = history.current_subspectrum()
    history.forward()
    assert history.current == 2
    assert history.current_subspectrum() is ss_2


def test_save_current_linshape():
    """Tests that two linespaces are saved as subspectrum.x, subspectrum.y"""

    history = History()
    history.save_current_linshape(x1, y1)
    x, y = history.current_subspectrum().x, history.current_subspectrum().y
    np.testing.assert_array_equal(x, x1)
    np.testing.assert_array_equal(y, y1)


def test_save_total_linshape():
    """Tests that two linspaces are saved as history.total_x, history.total_y.
    """

    history = History()
    history.save_total_linshape(x2, y2)
    x, y = history.total_x, history.total_y
    np.testing.assert_array_equal(x, x2)
    np.testing.assert_array_equal(y, y2)


def test_add_current_to_total():
    """Tests that history.current_subspectrum().y is correctly added to
    history.total_y.
    """
    history = History()
    history.save_current_linshape(x1, y1)
    history.save_total_linshape(x2, y2)
    old_y2 = np.copy(history.total_y)
    print('old_y2 ', old_y2)
    assert old_y2 is not history.total_y
    # np.testing.assert_raises(np.testing.assert_array_equal,
    #                          y_total, history.total_y)
    # print(np.allclose(old_y2, history.total_y))
    assert np.allclose(y_total, history.total_y) is not True
    # np.testing.assert_array_equal(old_y2, history.total_y)
    # assert np.not_equal(old_y2, history.total_y)
    # np.testing.assert_array_equal(y_total, history.total_y)
    history.add_current_to_total()
    print('after adding:')
    print('old_y2: ', old_y2)
    print('history.total_y', history.total_y)
    # np.testing.assert_array_equal(history.total_y, y2)
    # np.testing.assert_array_equal(history.total_y, old_y2)
    # np.testing.assert_array_equal(history.total_x, x2)


def test_mutables_not_mutated():
    """Tests to make sure that arrays not changed by previous tests."""
    _x1 = np.linspace(1.0, 10.0, 10)
    _y1 = np.linspace(0.1, 1.0, 10)
    _x2 = np.linspace(1.0, 10.0, 10)
    _y2 = np.linspace(100.0, 1000.0, 10)
    _y_total = np.array([100.1, 200.2, 300.3, 400.4, 500.5, 600.6, 700.7, 800.8,
                        900.9, 1001.0])
    for old, new in zip([_x1, _x2, _y1, _y2, _y_total],
                        [x1, x2, y1, y2, y_total]):
        print(old)
        print(new)
        np.testing.assert_array_equal(old, new)
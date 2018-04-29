import numpy as np
import pytest

from nmrmint.GUI.history import Subspectrum, History
from nmrmint.GUI.toolbars import FirstOrderBar, SecondOrderBar

# Before writing these tests, the program was being manually debugged (with
# first-order simulations) .
# First #C was changed to 2, and the current plot was added to the total.
# Then, a new plot was created with #B changed to 0 and Vcentr changed to 1.0.
# The test suites adopt this arbitrary approach.


@pytest.fixture()
def vars_default():
    """Return the default vars for a first-order bar."""
    return {'JAX': 7.0,
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


@ pytest.fixture()
def vars_1():
    """Return the modified vars for the first custom subspectrum, where
    #C has been changed to 2."""
    _vars = vars_default()
    _vars['#C'] = 2
    return _vars


@pytest.fixture()
def vars_2():
    """Return the modified vars for the first custom subspectrum, where
    #B has been changed to 0, and Vcentr to 1.0."""
    _vars = vars_default()
    _vars['#B'] = 0
    _vars['Vcentr'] = 1.0
    return _vars


@pytest.fixture()
def x1():
    """Return a np.linspace to represent the x coordinates for a lineshape."""
    return np.linspace(1.0, 10.0, 10)


@pytest.fixture()
def y1():
    """Return an array, with length matching x1, suitable for testing
    history/subspectra lineshapes.
    """
    # If this is refactored, y_total() must also be refactored!
    return np.linspace(0.1, 1.0, 10)


@pytest.fixture()
def x2():
    """Return a np.linspace to represent the x coordinates for a lineshape.

    Currently redundant with x1(). nmrmint currently uses the same
    np.linspace for all lineshapes.
    """
    return np.linspace(1.0, 10.0, 10)


@pytest.fixture()
def y2():
    """Return an array, with length matching x1, and differing from y1()
    suitable for testing history/subspectra lineshapes.
    """
    # If this is refactored, y_total() must also be refactored!
    return np.linspace(100.0, 1000.0, 10)


@pytest.fixture()
def y_total():
    """Return the hard-coded sum of y1() and y2().

    Used to check math used in lineshape additions/subtractions.
    """
    # If this is refactored, y1() and y2() must be as well!
    return np.array([100.1, 200.2, 300.3, 400.4, 500.5, 600.6, 700.7, 800.8,
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


@pytest.fixture()
def ss1(vars_1):
    """Create a subspectrum for our first test case.
    :return: Subspectrum,
        with .toolbar FirstorderBar,
        with .vars VARS_1
    """
    bar1 = FirstOrderBar(controller=fake_controller)
    bar1.reset(vars_1)
    ss1 = create_ss(bar1)
    return ss1


@pytest.fixture()
def ss2(vars_2):
    """Create a subspectrum for our first test case.
    :return: Subspectrum,
        with .toolbar FirstorderBar,
        with .vars VARS_2
    """
    bar2 = FirstOrderBar(controller=fake_controller)
    bar2.reset(vars_2)
    ss2 = create_ss(bar2)
    return ss2


def test_vars_default_matches_FirstOrderBar_default(vars_default):
    """Check that the test's default toolbar data matches FirstOrderBar's
    default data.
    """
    # GIVEN an instance of FirstOrderBar
    testbar = FirstOrderBar()

    # THEN its default data matches test_history.vars_default
    assert testbar.model == 'first_order'  # assumed in tests below
    assert testbar.vars == vars_default


def test_initialization(vars_default, vars_1, vars_2):
    """A sanity test to check that the test vars were set up correctly."""
    assert vars_1 is not vars_default
    assert vars_1 is not vars_2
    assert vars_1['#C'] == 2
    assert vars_2['#B'] == 0
    assert vars_2['Vcentr'] == 1.0


def test_xy(x1, y1, x2, y2, y_total):
    """A sanity test to check that routines returning x/y lineshape data
    are set up correctly."""
    assert np.array_equal(x1, x2)
    assert not np.array_equal(y1, y2)
    y_sum = y1 + y2
    assert np.allclose(y_sum, y_total)


def test_create_ss1(ss1):
    """A sanity test to check that ss1 is working correctly."""
    assert ss1.model == ss1.toolbar.model
    assert ss1.vars == ss1.toolbar.vars
    assert ss1.vars['#C'] == 2


def test_create_ss2(ss2):
    """A sanity test to check that ss2 is working correctly."""
    assert ss2.model == ss2.toolbar.model
    assert ss2.vars == ss2.toolbar.vars
    assert ss2.vars['#B'] == 0
    assert ss2.vars['#C'] == 0
    assert ss2.vars['Vcentr'] == 1.0


def test_history_instantiates_with_blank_subspectrum():
    """Test that when history instantiates it has no assigned subspectra."""
    # WHEN a History object is newly instantiated
    history = History()

    # THEN its subspectrum is instantiated as inactive
    assert not history.current_subspectrum().active


def test_add_subspectrum():
    """Test that a new, different subspectrum is added to the
    history.subspectra list."""
    # GIVEN a newly instantiated History object
    history = History()

    # WHEN a new subspectrum is added to it
    initial_counter = history.current
    history.add_subspectrum()
    final_counter = history.current
    assert history.subspectra[final_counter] is not history.subspectra[
        initial_counter]

    # THEN its counter is incremented by 1
    assert final_counter - initial_counter == 1


def test_current_subspectrum_returns_Subspectrum_object():
    """Test whether history.current_subspectrum returns a Subspectrum instance.

    Whether it returns the *correct* subspectrum is determined by other tests,
    such as test_back and test_forward.
    """
    # GIVEN a history object
    history = History()

    # WHEN asked for the current subspectrum
    # THEN a Subspectrum object is returned
    assert isinstance(history.current_subspectrum(), Subspectrum)


def test_subspectrum_data(ss1, vars_1):
    """Test that subspectrum_data returns a tuple of the current
    subspectrum's (model, vars)
    """
    # GIVEN a history with a non-default subspectrum
    history = History()
    history.subspectra[0] = ss1

    # WHEN history is asked for subspectrum model data
    # THEN the subspectrum's (model, vars) data are returned as a tuple
    assert history.subspectrum_data() == ('first_order', vars_1)


def test_all_spec_data(ss1, ss2, vars_1, vars_2):
    """Test that all_spec_data is iterable and yields spec data for each
    subspectrum in order.
    """
    # Given a history with two subspectra, each with references to toolbars
    # and lineshape data
    # toolbar = FirstOrderBar(controller=fake_controller)
    history = History()
    # history.toolbar = toolbar
    history.subspectra[history.current] = ss1
    history.restore()
    history.subspectra.append(ss2)
    assert history.toolbar is history.current_subspectrum().toolbar
    assert history.current_subspectrum() is ss1
    assert history.subspectra[history.current + 1] is ss2
    assert ss1 is not ss2

    # WHEN asked for subspectra data
    all_spec_data = [data for data in history.all_spec_data()]
    expected_data = [('first_order', vars_1),
                     ('first_order', vars_2)]

    # THEN the correct data is yielded
    assert all_spec_data == expected_data


def test_current_toolbar():
    """Test that current_bar returns the bar for the current subspectrum."""
    # GIVEN a history with a toolbar assigned to its subspectrum
    history = History()
    bar = FirstOrderBar()
    history.subspectra[history.current].toolbar = bar

    # WHEN history is asked for its current toolbar
    # THEN the current subspectrum's bar is returned
    assert history.current_toolbar() is bar


# def test_change_toolbar(vars_2):
#     """Test to see if the current subspectrum's toolbar can be replaced."""
#     # GIVEN an initialized history with default toolbar
#     history = History()
#     bar_1 = FirstOrderBar(controller=fake_controller)
#     history.current_subspectrum().toolbar = bar_1
#
#     # WHEN a new toolbar is added
#     bar_2 = FirstOrderBar(controller=fake_controller)
#     bar_2.reset(vars_2)
#     history.change_toolbar(bar_2)
#
#     # THEN the current_toolbar is updated
#     assert history.current_toolbar() is bar_2


def test_change_toolbar():
    """Test that history.toolbar can be changed via method call.

    This may not be necessary, unless at some point a setter method is
    actually required instead of direct access to the attribute.
    """
    # Given a history instance and a toolbar instance
    history = History()
    toolbar = FirstOrderBar(controller=fake_controller)

    # WHEN given a toolbar and told to change to it
    history.change_toolbar(toolbar)

    # THEN history.toolbar now points to that toolbar
    assert history.toolbar is toolbar

# def test_change_toolbar_to_second_order_bar():
#     """Test to see if change_toolbar works with SecondOrderBar."""
#     # GIVEN an initialized history with default first-order toolbar
#     history = History()
#     bar_1 = FirstOrderBar(controller=fake_controller)
#     history.current_subspectrum().toolbar = bar_1
#
#     # WHEN a SecondOrderBar is added
#     bar_2 = SecondOrderBar(controller=fake_controller)
#     history.change_toolbar(bar_2)
#
#     # THEN the current_toolbar is updated
#     _, _vars = history.subspectrum_data()
#     assert _ == 'nspin'
#     assert _vars['w'][0][0] == 0.5


def test_delete(ss1, ss2):
    """Test that, when a non-last subspectrum is deleted, it is removed from
    history.subspectra."""
    # GIVEN a history instance with two complete subspectra objects and
    # pointing to the first subspectrum
    toolbar = FirstOrderBar(controller=fake_controller)
    history = History()
    history.toolbar = toolbar
    history.subspectra[history.current] = ss1
    # history.current = 1
    history.subspectra.append(ss2)
    assert history.current_subspectrum() is ss1

    # WHEN history is told to delete the subspectrum
    history.delete()

    # THEN current subspectrum set to next subspectrum
    assert history.subspectra == [ss2]
    assert history.current_subspectrum() is ss2


def test_delete_last_subspectrum(ss1, ss2):
    """Test that, when a last subspectrum is deleted, it is removed from
    history.subspectra and history is reset to the previous subspectrum.
    """
    # GIVEN a history instance with two complete subspectra objects and
    # pointing to the second subspectrum
    toolbar = FirstOrderBar(controller=fake_controller)
    history = History()
    history.toolbar = toolbar
    history.subspectra[history.current] = ss1
    history.current = 1
    history.subspectra.append(ss2)
    assert history.current_subspectrum() is ss2

    # WHEN history is told to delete the subspectrum
    history.delete()

    # THEN current subspectrum set to previous subspectrum
    assert history.subspectra == [ss1]
    assert history.current_subspectrum() is ss1


def test_save(vars_default):
    """Test that a current subspectrum input state is recorded to the current
    subspectrum.
    """
    # GIVEN a history with a toolbar reference and a blank subspectrum
    history = History()
    history.toolbar = FirstOrderBar(controller=fake_controller)

    # WHEN told to save state
    history.save()

    # THEN the subspectrum's model, vars and toolbar are updated
    ss = history.current_subspectrum()
    assert ss.model == 'first_order'
    assert ss.vars == vars_default
    assert ss.vars is not history.toolbar.vars  # must be a copy to save state
    assert ss.toolbar is history.toolbar


def test_save_alerts_if_no_toolbar(capsys):
    """Test that history.save gracefully handles having no history.toolbar.

    Only expect this scenario to occur during tests, not in working code.
    """
    # GIVEN a History instance with no toolbar recorded
    history = History()
    out, err = capsys.readouterr()  # capture any print statements before save

    # WHEN told to save toolbar state
    history.save()

    # THEN a helpful error message is printed
    out, err = capsys.readouterr()
    assert out.startswith("HISTORY TOOLBAR ERROR")


def test_restore(ss1):
    """Test that history.toolbar can be restored from the current
    subspectrum.
    """
    # GIVEN a history instance with a toolbar attribute,
    # and with a subspectrum containing a toolbar attribute
    history = History()
    history.toolbar = FirstOrderBar(controller=fake_controller)
    history.subspectra[0] = ss1
    assert ss1.toolbar is not history.toolbar
    assert isinstance(ss1.toolbar, FirstOrderBar)

    # WHEN history restored
    history.restore()

    # THEN history.toolbar is updated to point to the current subspectrum
    # toolbar
    assert history.toolbar is ss1.toolbar



def test_back():
    """Test to see if history.back moves back 1 subspectrum in subspectra
    list.
    """
    # GIVEN a history with two subspectra, set to the more recent subspectrum
    history = History()
    ss1 = history.current_subspectrum()
    history.add_subspectrum()
    ss2 = history.current_subspectrum()
    assert ss1 is not ss2

    # WHEN the history is told to move back one step
    action = history.back()

    # THEN the current_subspectrum now points to the previous subspectrum
    ss3 = history.current_subspectrum()
    assert ss1 is ss3
    assert action


def test_back_stops_at_beginning():
    """Test that if at beginning of history, don't keep moving backwards."""

    # GIVEN a history that is currently on the last of three subspectra
    history = History()
    subspectra = [history.current_subspectrum()]
    for i in range(2):
        history.add_subspectrum()
        assert history.current == i + 1
        subspectra.append(history.current_subspectrum())
        assert history.current_subspectrum() is not history.subspectra[i]

    # WHILE the history is told to move backwards
    history.back()

    # THEN the current history points to the previous subspectrum
    assert history.current == 1
    assert history.current_subspectrum() is subspectra[1]
    history.back()
    assert history.current == 0
    assert history.current_subspectrum() is subspectra[0]

    # UNTIL it reaches the beginning of the history, in which case there
    # is no change.
    action = history.back()
    assert history.current == 0
    assert history.current_subspectrum() is subspectra[0]
    assert not action


def test_back_restores_toolbar_state(ss1, vars_1, ss2):
    """Test that the previous subspectrum is restored."""
    # GIVEN a history instance with two complete subspectra objects and
    # pointing to the more recent subspectrum
    toolbar = FirstOrderBar(controller=fake_controller)
    history = History()
    history.toolbar = toolbar
    history.subspectra[history.current] = ss1
    history.current = 1
    history.subspectra.append(ss2)
    assert history.current_subspectrum() is ss2
    assert history.subspectra[history.current - 1] is not ss2

    # WHEN history is told to go back
    history.back()

    # THEN the subspectrum is restored
    ss = history.current_subspectrum()
    assert ss is ss1
    assert ss.vars == vars_1


def test_back_saves_toolbar_first(ss1, ss2, vars_2, vars_default):
    """Test that the current toolbar info is saved to the current subspectrum
    before moving back.
    """
    # GIVEN a history instance with two complete subspectra objects and
    # pointing to the more recent subspectrum
    toolbar = FirstOrderBar(controller=fake_controller)
    history = History()
    history.toolbar = toolbar
    history.subspectra[history.current] = ss1
    history.current = 1
    history.subspectra.append(ss2)
    assert history.current_subspectrum().toolbar is not history.toolbar
    assert history.current_subspectrum().vars == vars_2
    assert history.toolbar.vars == vars_default

    # WHEN history is told to go back
    history.back()

    # THEN the subspectrum was updated
    ss = history.subspectra[history.current + 1]
    assert ss is ss2
    assert ss.vars == vars_default


def test_back_updates_history_toolbar(ss1, ss2):
    """Test that, after going back one subspectrum, the history's toolbar
    reference is updated."""
    # GIVEN a history instance with two complete subspectra objects and
    # pointing to the more recent subspectrum
    toolbar = FirstOrderBar(controller=fake_controller)
    history = History()
    history.toolbar = toolbar
    history.subspectra[history.current] = ss1
    history.current = 1
    history.subspectra.append(ss2)

    previous_ss = history.subspectra[history.current - 1]
    assert previous_ss.toolbar is not history.toolbar

    # WHEN history is told to go back
    history.back()

    # THEN history.toolbar was updated
    assert history.toolbar is history.current_subspectrum().toolbar


def test_forward():
    """Test to see if history.forward moves forward 1 subspectrum in subspectra
    list.
    """
    # GIVEN a history with two subspectra, set to the first subspectrum
    history = History()
    history.add_subspectrum()
    ss_1 = history.current_subspectrum()
    history.back()

    # WHEN the history is advanced forward
    action = history.forward()

    # THEN the history points to the second subspectrum
    assert history.current_subspectrum() is ss_1
    assert history.current == 1
    assert action


def test_forward_stops_at_end():
    """Test that if at end of history, don't keep moving forwards."""
    # GIVEN a history containing three subspectra, set at the first subspectrum
    history = History()
    subspectra = [history.current_subspectrum()]
    for i in range(2):
        history.add_subspectrum()
        subspectra.append(history.current_subspectrum())
    for i in range(2):
        history.back()
    assert history.current_subspectrum() is subspectra[0]

    # WHILE the history is told to advance
    for i in range(2):
        history.forward()
        # THEN the history points to the next subspectrum
        assert history.current_subspectrum() is subspectra[i + 1]
    assert history.current == 2

    # UNTIL it reaches the end of the history, in which case there is no change
    ss_2 = history.current_subspectrum()
    action = history.forward()
    assert history.current == 2
    assert history.current_subspectrum() is ss_2
    assert not action


def test_forward_updates_history_toolbar(ss1, ss2):
    """Test that, after going forward one subspectrum, the history's toolbar
    reference is updated."""
    # GIVEN a history instance with two complete subspectra objects and
    # pointing to the first subspectrum
    toolbar = FirstOrderBar(controller=fake_controller)
    history = History()
    history.toolbar = toolbar
    history.subspectra[history.current] = ss1
    # history.current = 1
    history.subspectra.append(ss2)

    next_ss = history.subspectra[history.current + 1]
    assert next_ss.toolbar is not history.toolbar

    # WHEN history is told to go forward
    history.forward()

    # THEN history.toolbar was updated
    assert history.toolbar is history.current_subspectrum().toolbar


def test_current_lineshape(ss1, x1, y1):
    """Test that history returns a tuple of the current subspectrum's
    lineshape data.
    """
    # GIVEN a history instance, with a subspectrum having lineshape data
    history = History()
    history.subspectra[0] = ss1
    ss1.x, ss1.y = x1, y1
    assert np.array_equal(history.current_subspectrum().x, x1)
    assert np.array_equal(history.current_subspectrum().y, y1)

    # WHEN asked for the current lineshape
    # THEN a tuple of the subspectrum's lineshape data is returned
    x, y = history.current_lineshape()
    assert np.array_equal(x, x1)
    assert np.array_equal(y, y1)




def test_save_current_linshape(x1, y1):
    """Test that two linespaces are saved as subspectrum.x, subspectrum.y"""
    # GIVEN a history with a single subspectrum
    history = History()

    # WHEN history is told to save lineshape data
    history.save_current_linshape(x1, y1)

    # THEN this data is added to the subspectrum object
    x, y = history.current_subspectrum().x, history.current_subspectrum().y
    assert np.array_equal(x, x1)
    assert np.array_equal(y, y1)


def test_save_total_linshape():
    """Test that two linspaces are saved as history.total_x, history.total_y.
    """
    # GIVEN a history with a single subspectrum
    history = History()

    # WHEN history is told to save lineshape data for the total spectrum
    history.save_total_linshape(x2, y2)

    # THEN the lineshape x and y data are stored by the history object
    x, y = history.total_x, history.total_y
    assert np.array_equal(x, x2)
    assert np.array_equal(y, y2)


def test_add_current_to_total(x1, x2, y1, y2, y_total):
    """Test that history.current_subspectrum().y is correctly added to
    history.total_y.
    """
    # GIVEN a history with total spectrum lineshape data, and a subspectrum
    # with current lineshape data
    history = History()
    history.save_current_linshape(x1, y1)
    history.save_total_linshape(x2, y2)
    old_y1 = np.copy(history.current_subspectrum().y)
    old_y2 = np.copy(history.total_y)
    print('old_y1', old_y1)
    print('old_y2 ', old_y2)

    # WHEN history told to add the current subspectrum to the total
    history.add_current_to_total()

    # THEN the subspectrum's y data is added to history's total y data, but
    # x data and subspectrum data is unchanged.
    print('after adding:')
    print('old_y2: ', old_y2)
    print('history.total_y', history.total_y)
    assert np.array_equal(history.total_y, y_total)
    assert not np.array_equal(history.total_y, old_y2)
    assert np.array_equal(history.current_subspectrum().y, old_y1)
    assert np.array_equal(history.total_x, x2)
    assert np.array_equal(history.current_subspectrum().x, x1)


def test_remove_current_from_total(x1, y1, x2, y2, y_total):
    """Test that history.current_subspectrum().y is correctly subtracted from
    history.total_y.
    """
    # GIVEN a history with total spectrum lineshape data,
    # and a subspectrum with current lineshape data
    history = History()
    history.save_current_linshape(x1, y1)
    history.save_total_linshape(x2, y_total)
    old_y1 = np.copy(history.current_subspectrum().y)
    old_total_y = np.copy(history.total_y)
    print('old_y1', old_y1)
    print('old_total_y ', old_total_y)

    # WHEN history told to remove the current subspectrum to the total
    history.remove_current_from_total()

    # THEN the subspectrum's y data is subtracted from history's total y data,
    #  but x data and subspectrum data is unchanged.
    print('after removing:')
    print('old_y1: ', old_y1)
    print('history.total_y', history.total_y)
    assert np.array_equal(history.total_y, y2)
    assert not np.array_equal(history.total_y, old_total_y)
    assert np.array_equal(history.current_subspectrum().y, old_y1)
    assert np.array_equal(history.total_x, x2)
    assert np.array_equal(history.current_subspectrum().x, x1)


def test_update_vars(vars_1):
    """Test that the current subspectrum is correctly updated with supplied
    model and vars.
    """
    # GIVEN a history object with a blank subspectrum
    history = History()
    assert history.current_subspectrum().model is None
    assert history.current_subspectrum().vars is None

    # WHEN history asked to update data with supplied model and vars
    history.update_vars('first_order', vars_1)

    # THEN the history object has its .model and .vars correctly updated
    assert history.current_subspectrum().model == 'first_order'
    assert history.current_subspectrum().vars == vars_1

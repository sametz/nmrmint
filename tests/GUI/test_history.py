import numpy as np
import pytest

from nmrmint.GUI.history import Subspectrum, History
from nmrmint.GUI.toolbars import FirstOrderBar

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


@pytest.fixture()
def vars_1():
    """Return the modified vars for the first custom subspectrum, where
    #C has been changed to 2."""
    _vars = vars_default()
    _vars['#C'] = 2
    return _vars


@pytest.fixture()
def vars_2():
    """Return the modified vars for the second custom subspectrum, where
    #B has been changed to 0, and Vcentr to 1.0."""
    _vars = vars_default()
    _vars['#B'] = 0
    _vars['Vcentr'] = 1.0
    return _vars


@pytest.fixture()
def vars_3():
    """Return modified vars for the third custom subspectrum, where #D has
    been changed to 3.

    Created for ss3 and update_all_spectra testing."""
    _vars = vars_default()
    _vars['#D'] = 3
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
def y3():
    """Return an array of same length as y1 and y2 but with different values.

    Used to test update_all_spectra as the data for an inactive subspectrum
    that should be skipped over when creating the total spectrum."""
    return np.linspace(5, 50, 10)


@pytest.fixture()
def y_total():
    """Return the hard-coded sum of y1() and y2().

    Used to check math used in lineshape additions/subtractions.
    """
    # If this is refactored, y1() and y2() must be as well!
    return np.array([100.1, 200.2, 300.3, 400.4, 500.5, 600.6, 700.7, 800.8,
                     900.9, 1001.0])


def fake_callback(*args):
    """For mocking out Toolbar callback calls."""
    print('Controller was passed: ', *args)
    pass


def create_ss(bar):
    """Given a toolbar, instantiate a subspectrum with that toolbar.

    :param bar: a GUI._ToolBar subclass
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
    bar1 = FirstOrderBar(callback=fake_callback)
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
    bar2 = FirstOrderBar(callback=fake_callback)
    bar2.reset(vars_2)
    ss2 = create_ss(bar2)
    return ss2


@pytest.fixture()
def ss3(vars_3):
    """Create a third subspectrum for testing update_all_spectra."""
    bar3 = FirstOrderBar(callback=fake_callback)
    bar3.reset(vars_3)
    ss3 = create_ss(bar3)
    return ss3


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


def test_history_instantiates_with_inactive_subspectrum():
    # WHEN a History object is newly instantiated
    history = History()

    # THEN its subspectrum is instantiated as inactive
    assert not history.current_subspectrum().active


def test_add_subspectrum():
    """Test that a new, different subspectrum is added to the
    history._subspectra list."""
    # TODO need multiple tests
    # GIVEN a newly instantiated History object
    history = History()
    history._toolbar = FirstOrderBar(callback=fake_callback)

    # WHEN a new subspectrum is added to it
    initial_counter = history.current
    history.add_subspectrum()
    final_counter = history.current
    assert history._subspectra[final_counter] is not history._subspectra[
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
    history._subspectra[0] = ss1

    # WHEN history is asked for subspectrum model data
    # THEN the subspectrum's (model, vars) data are returned as a tuple
    assert history.subspectrum_data() == ('first_order', vars_1)


def test_all_spec_data(ss1, ss2, vars_1, vars_2):
    """Test that all_spec_data is iterable and yields spec data for each
    subspectrum in order.
    """
    # Given a history with two subspectra, each with references to toolbars
    # and lineshape data
    history = History()
    history._subspectra[history.current] = ss1
    history.restore()
    history._subspectra.append(ss2)
    assert history._toolbar is history.current_subspectrum().toolbar
    assert history.current_subspectrum() is ss1
    assert history._subspectra[history.current + 1] is ss2
    assert ss1 is not ss2

    # WHEN asked for subspectra data
    all_spec_data = [data for data in history.all_spec_data()]
    expected_data = [('first_order', vars_1),
                     ('first_order', vars_2)]

    # THEN the correct data is yielded
    assert all_spec_data == expected_data


def test_change_toolbar():
    """Test that history.toolbar can be changed via method call.

    This may not be necessary, unless at some point a setter method is
    actually required instead of direct access to the attribute.
    """
    # Given a history instance and a toolbar instance
    history = History()
    toolbar = FirstOrderBar(callback=fake_callback)

    # WHEN given a toolbar and told to change to it
    history.change_toolbar(toolbar)

    # THEN history._toolbar now points to that _toolbar
    assert history._toolbar is toolbar


def test_delete(ss1, ss2):
    """Test that, when a non-last subspectrum is deleted, it is removed from
    history._subspectra."""
    # GIVEN a history instance with two complete subspectra objects and
    # pointing to the first subspectrum
    toolbar = FirstOrderBar(callback=fake_callback)
    history = History()
    history._toolbar = toolbar
    history._subspectra[history.current] = ss1
    history._subspectra.append(ss2)
    assert history.current_subspectrum() is ss1

    # WHEN history is told to delete the subspectrum
    action = history.delete()

    # THEN current subspectrum set to next subspectrum
    assert history._subspectra == [ss2]
    assert history.current_subspectrum() is ss2
    assert action


def test_delete_updates_total(ss1, ss2, x1, x2, y1, y2, y_total):
    """Test that deleting an active subspectrum also deletes its contribution
    from the total spectrum.
    """
    # GIVEN a history instance with two active subspectra objects  pointing
    # to the second subspectrum, and with .total_y of their sum:
    ss1.x, ss1.y = x1, y1
    ss1.active = True
    ss2.x, ss2.y = x2, y2
    ss2.active = True
    history = History()
    history._subspectra = [ss1, ss2]
    history.total_y = y_total
    history.current = 1
    assert np.array_equal(history.current_subspectrum().y, y2)

    # WHEN told to delete the current spectrum
    history.delete()

    # THEN history.total_y has had the deleted spectrum's y subtracted from it
    assert np.allclose(history.total_y, y1)


def test_delete_inactive_does_not_change_total(ss1, ss2, x1, x2, y1, y2):
    """Test that deleting an inactive subspectrum does not change
    history.total_y.
    """
    # GIVEN a history instance with two subspectra objects (the first active,
    # the second inactive) pointing to the second subspectrum, and with
    # .total_y only equal to the first subspectrum's y
    ss1.x, ss1.y = x1, y1
    ss1.active = True
    ss2.x, ss2.y = x2, y2
    ss2.active = False
    history = History()
    history._subspectra = [ss1, ss2]
    history.total_y = y1
    history.current = 1

    # IF told to delete the current spectrum
    history.delete()

    # THEN history.total_y has not changed
    assert np.allclose(history.total_y, y1)


def test_delete_stops_at_one_subspectrum():
    """Test that no delete occurs if there is only one subspectrum left."""
    # GIVEN a history instance with only one subspectrum
    history = History()
    current_ss = history.current_subspectrum()
    # WHEN asked to delete the current subspectrum
    action = history.delete()

    # THEN no change occurs
    assert len(history._subspectra) == 1
    assert history.current == 0
    assert history.current_subspectrum() is current_ss
    assert not action


def test_delete_last_subspectrum(ss1, ss2):
    """Test that, when a last subspectrum is deleted, it is removed from
    history._subspectra and history is reset to the previous subspectrum.
    """
    # GIVEN a history instance with two complete subspectra objects and
    # pointing to the second subspectrum
    toolbar = FirstOrderBar(callback=fake_callback)
    history = History()
    history._toolbar = toolbar
    history._subspectra[history.current] = ss1
    history.current = 1
    history._subspectra.append(ss2)
    assert history.current_subspectrum() is ss2

    # WHEN history is told to delete the subspectrum
    history.delete()

    # THEN current subspectrum set to previous subspectrum
    assert history._subspectra == [ss1]
    assert history.current_subspectrum() is ss1


def test_save(vars_default):
    """Test that a current subspectrum input state is recorded to the current
    subspectrum.
    """
    # GIVEN a history with a toolbar reference and a blank subspectrum
    history = History()
    history._toolbar = FirstOrderBar(callback=fake_callback)

    # WHEN told to save state
    history.save()

    # THEN the subspectrum's model, vars and toolbar are updated
    ss = history.current_subspectrum()
    assert ss.model == 'first_order'
    assert ss.vars == vars_default
    assert ss.vars is not history._toolbar.vars  # must be a copy to save state
    assert ss.toolbar is history._toolbar


def test_save_alerts_if_no_toolbar(capsys):
    """Test that history.save gracefully handles having no history.toolbar.

    Only expect this scenario to occur during tests, not in working code.
    """
    # GIVEN a History instance with no toolbar recorded
    history = History()
    # noinspection PyUnusedLocal
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
    history._toolbar = FirstOrderBar(callback=fake_callback)
    history._subspectra[0] = ss1
    assert ss1.toolbar is not history._toolbar
    assert isinstance(ss1.toolbar, FirstOrderBar)

    # WHEN history restored
    history.restore()

    # THEN history._toolbar is updated to point to the current subspectrum
    # toolbar
    assert history._toolbar is ss1.toolbar


def test_back():
    """Test to see if history.back moves back 1 subspectrum in _subspectra
    list.
    """
    # GIVEN a history with two subspectra, set to the more recent subspectrum
    history = History()
    testbar = FirstOrderBar()
    history.change_toolbar(testbar)
    ss1 = history.current_subspectrum()
    assert ss1.toolbar is history._toolbar
    history.add_subspectrum()
    ss2 = history.current_subspectrum()
    history.save()
    assert ss2.toolbar is history._toolbar
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
    testbar = FirstOrderBar()
    history.change_toolbar(testbar)
    subspectra = [history.current_subspectrum()]
    for i in range(2):
        history.add_subspectrum()
        history.save()
        assert history.current == i + 1
        subspectra.append(history.current_subspectrum())
        assert history.current_subspectrum() is not history._subspectra[i]

    # WHILE the history is told to move backwards
    action = history.back()

    # THEN the current history points to the previous subspectrum
    assert history.current == 1
    assert history.current_subspectrum() is subspectra[1]
    assert action

    action = history.back()
    assert history.current == 0
    assert history.current_subspectrum() is subspectra[0]
    assert action

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
    toolbar = FirstOrderBar(callback=fake_callback)
    history = History()
    history._toolbar = toolbar
    history._subspectra[history.current] = ss1
    history.current = 1
    history._subspectra.append(ss2)
    assert history.current_subspectrum() is ss2
    assert history._subspectra[history.current - 1] is not ss2

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
    toolbar = FirstOrderBar(callback=fake_callback)
    history = History()
    history._toolbar = toolbar
    history._subspectra[history.current] = ss1
    history.current = 1
    history._subspectra.append(ss2)
    assert history.current_subspectrum().toolbar is not history._toolbar
    assert history.current_subspectrum().vars == vars_2
    assert history._toolbar.vars == vars_default

    # WHEN history is told to go back
    history.back()

    # THEN the subspectrum was updated
    ss = history._subspectra[history.current + 1]
    assert ss is ss2
    assert ss.vars == vars_default


def test_back_updates_history_toolbar(ss1, ss2):
    """Test that, after going back one subspectrum, the history's toolbar
    reference is updated."""
    # GIVEN a history instance with two complete subspectra objects and
    # pointing to the more recent subspectrum
    toolbar = FirstOrderBar(callback=fake_callback)
    history = History()
    history._toolbar = toolbar
    history._subspectra[history.current] = ss1
    history.current = 1
    history._subspectra.append(ss2)

    previous_ss = history._subspectra[history.current - 1]
    assert previous_ss.toolbar is not history._toolbar

    # WHEN history is told to go back
    history.back()

    # THEN history._toolbar was updated
    assert history._toolbar is history.current_subspectrum().toolbar


def test_forward():
    """Test to see if history.forward moves forward 1 subspectrum in _subspectra
    list.
    """
    # GIVEN a history with two subspectra, set to the first subspectrum
    history = History()
    testbar = FirstOrderBar()
    history.change_toolbar(testbar)
    history.add_subspectrum()
    history.save()
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
    testbar = FirstOrderBar()
    history.change_toolbar(testbar)
    subspectra = [history.current_subspectrum()]
    for i in range(2):
        history.add_subspectrum()
        history.save()
        subspectra.append(history.current_subspectrum())
    for i in range(2):
        history.back()
    assert history.current_subspectrum() is subspectra[0]

    # WHILE the history is told to advance
    for i in range(2):
        action = history.forward()
        # THEN the history points to the next subspectrum
        assert history.current_subspectrum() is subspectra[i + 1]
        assert action
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
    toolbar = FirstOrderBar(callback=fake_callback)
    history = History()
    history._toolbar = toolbar
    history._subspectra[history.current] = ss1
    # history.current = 1
    history._subspectra.append(ss2)

    next_ss = history._subspectra[history.current + 1]
    assert next_ss.toolbar is not history._toolbar

    # WHEN history is told to go forward
    history.forward()

    # THEN history._toolbar was updated
    assert history._toolbar is history.current_subspectrum().toolbar


def test_current_lineshape(ss1, x1, y1):
    """Test that history returns a tuple of the current subspectrum's
    lineshape data.
    """
    # GIVEN a history instance, with a subspectrum having lineshape data
    history = History()
    history._subspectra[0] = ss1
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
    history.save_current_lineshape(x1, y1)

    # THEN this data is added to the subspectrum object
    x, y = history.current_subspectrum().x, history.current_subspectrum().y
    assert np.array_equal(x, x1)
    assert np.array_equal(y, y1)


def test_total_lineshape(x1, y_total):
    """Finish the test!"""
    # GIVEN a history instance with total lineshape data
    history = History()
    history.total_x, history.total_y = x1, y_total

    # WHEN asked for the total lineshape
    x, y = history.total_lineshape()

    # THEN the correct data is returned
    assert np.array_equal(x, x1)
    assert np.array_equal(y, y_total)


def test_save_total_linshape():
    """Test that two linspaces are saved as history.total_x, history.total_y.
    """
    # GIVEN a history with a single subspectrum
    history = History()

    # WHEN history is told to save lineshape data for the total spectrum
    history.save_total_lineshape(x2, y2)

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
    history.save_current_lineshape(x1, y1)
    history.save_total_lineshape(x2, y2)
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
    history.save_current_lineshape(x1, y1)
    history.save_total_lineshape(x2, y_total)
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
    history._update_vars('first_order', vars_1)

    # THEN the history object has its .model and .vars correctly updated
    assert history.current_subspectrum().model == 'first_order'
    assert history.current_subspectrum().vars == vars_1


def test_update_all_spectra(ss1, ss2, ss3, x1, x2, y1, y2, y3, y_total):
    """Test that subspectra and total spectrum are correctly replaced."""
    # GIVEN a history object with three subspectra, the second of which is
    # inactive
    history = History()
    ss1.active = True
    ss2.active = True
    history._subspectra = [ss1, ss3, ss2]
    history._toolbar = FirstOrderBar(callback=fake_callback)

    # WHEN told to update all spectra using a blank spectrum and a list of
    # lineshape data
    blank_spectrum = (x1, [0] * 10)
    lineshapes = [(x1, y1), (x1, y3), (x2, y2)]
    history.update_all_spectra(blank_spectrum, lineshapes)

    # THEN all stored lineshapes are updated appropriately
    new_lineshapes = [(ss1.x, ss1.y), (ss3.x, ss3.y), (ss2.x, ss2.y)]
    assert np.allclose(lineshapes, new_lineshapes)
    assert np.allclose(history.total_y, y_total)

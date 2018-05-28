"""Custom widgets composed from standard tkinter widgets.

Provides the following classes:
* _BaseEntryFrame: a base class for a Frame that contains a Label and an Entry
widget, has custom behavior, and calls back when a change to the entry has
been committed.

* ArrayBox: a subclass of _BaseEntryFrame that reads/writes its value from/to a
2-D numpy array.

* ArraySpinBox: a subclass of ArrayBox that uses a SpinBox widget instead of
an Entry widget.

* VarBox: Similar to _BaseEntryFrame, but is not provided a data structure or
callback in its arguments. Instead, it assumes the parent has the
necessary attribute and method. TODO: refactor this out of the first-order
toolbars and use ArrayBox instead.

* IntBox: Similar to VarBox, but with the Entry restricted to integers
instead of floats. TODO: refactor so that it either subclasses ArrayBox or so
that the widgets in this module use subclasses of Entry specific to
float-only or int-only entries.

* VarButtonBox: emulates the WINDNMR-style entry boxes, like a deluxe
SpinBox. TODO: refactor so that up/down arrow behavior, methods etc are
identical to those in ArraySpinBox.

* SimpleVariableBox: A subclass of _BaseEntryFrame that takes initial and
minimum-value argument, instantiates the Entry with the initial value,
and defaults to the custom minimum value when empty.
"""
# TODO: keep implementing composition over inheritance for customizing widgets
# TODO: better names, e.g. VarBox, SimpleVariableBox

from tkinter import *

up_arrow = u"\u21e7"
down_arrow = u"\u21e9"
left_arrow = u"\u21e6"
right_arrow = u"\u21e8"


class _BaseEntryFrame(Frame):
    """A tkinter Frame that holds a labeled entry widget, and a callback for
    when a change is committed to the Entry's value.

    _BaseEntryFrame is intended as a new base class that will be inherited from.

    Methods:
        * get_value: return the contents of the Entry as a str.
        * set_value: set the contents of the entry to a supplied argument

    Attributes:
        * current_value: the current value stored in the entry-like widget.
    """

    def __init__(self, parent=None, name='', color='white',
                 callback=None,
                 **options):
        """
        __init__ is broken into multiple method references, to allow
        subclasses/mixins to modify as needed.

        Keyword arguments:
        :param parent: The parent tkinter object
        :param name: (str) Optional name. Used as Label text as well as
        widget identification.
        :param color: (str) Default color for widget and contents.
        :param callback: function to be called when change in Entry contents
        committed.
        :param options: (dict) Standard kwargs for a tkinter Frame
        """
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=0,
                       background=color, **options)
        self._name = name
        self._color = color
        self._callback = callback

        # The initial value type for the widget depends on subclass, so:
        # Uncomment the code below to test _BaseEntryFrame
        try:
            assert self._initial_value is not None
        except AttributeError:
            self._initial_value = 0.00  # Should be overridden by subclass

        self._initialize()
        self._add_label()
        self._add_entry()
        self._bind_entry()
        self._validate_entry()

    def _initialize(self):
        """
        Create a StringVar object; _initialize self.value with the initial
        number, and _initialize StringVar with that same value.

        Subclasses of BasentryFrame should overwrite this function to
        accomodate
        however initial values are passed into them.
        """
        self._value_var = StringVar()
        self.current_value = self._initial_value
        self._value_var.set(self.current_value)

    def _add_label(self):
        """Add self._name to a Label at the top of the frame."""
        Label(self, text=self._name, bg=self._color, bd=0).pack(side=TOP)

    def _add_entry(self):
        """Add an Entry widget to the _BaseEntryFrame.

        Subclasses of EntryBox that use a different entry widget (e.g. SpinBox)
        should overwrite this function.
        """
        self._entry = Entry(self, width=7,
                            validate='key')  # check for number on keypress)
        self._entry.pack(side=TOP, fill=X)
        self._entry.config(textvariable=self._value_var)

    def _bind_entry(self):
        """Define behavior when the Entry widget loses focus.

        _BaseEntryFrame assumes action should only be taken when a change in the
        Entry widget is "committed" by hitting Return, Tab, or clicking
        outside the widget.
        Subclasses may overwrite/extend _bind_entry to tailor behavior.
        """
        self._entry.bind('<Return>', lambda event: self._on_return(event))
        self._entry.bind('<Tab>', lambda event: self._on_tab(event))
        self._entry.bind('<FocusOut>', lambda event: self._refresh())
        self._entry.bind('<FocusIn>',
                         lambda event: self._entry.select_range(0, END))

    # noinspection PyUnusedLocal
    def _on_return(self, event):
        """Refresh the view and shift focus when Return key is hit."""

        # Previously self._refresh() had to be called here, but since
        # <FocusOut> triggers refresh, omitting it here avoids double calls
        # to _callback
        self._find_next_entry(self._entry).focus()

    def _refresh(self):
        """Save the Entry value to the data structure then request a view
        refresh.
        """
        if self._entry_is_changed():
            self._save_entry()
            self._callback()

    def _entry_is_changed(self):
        """Check if the current Entry value differs from the last saved
        value.

        :return: True if changed, False if not.
        """
        get_value = self._value_var.get()  # for debugging
        return str(self.current_value) != get_value

    def _save_entry(self):
        """Saves widget's entry as self.stored_value , filling the entry with
        0.00 if it was empty.
        Subclasses should overwrite _save_entry to suit needs of their data
        type and call to _callback.
        """
        if not self._value_var.get():  # if entry left blank,
            self._value_var.set(0.00)  # fill it with zero
        value = float(self._value_var.get())
        self.current_value = value

    def _find_next_entry(self, current_widget):
        """Return the next Entry-like widget in tkinter's widget traversal.

        Used to ignore the other widgets in the GUI such as Buttons,
        RadioButtons, and matplotlib widgets.
        Subclasses can modify this behavior if other widget types are to be
        acknowledged.
        :param current_widget: the widget that needs to lose focus
        :return: the next entry-like widget
        """
        next_entry = current_widget.tk_focusNext()
        if next_entry.widgetName in ['entry', 'spinbox']:
            return next_entry
        else:
            return self._find_next_entry(next_entry)

    def _on_tab(self, *event):
        """Refresh the view and shift focus when Tab key is hit."""
        self._on_return(event)
        return 'break'  # override default tkinter tab behavior

    def _validate_entry(self):
        """Restrict Entry inputs to a valid type"""
        # check on each keypress if new result will be valid
        self._entry['validatecommand'] = (self.register(self._is_valid), '%P')
        # sound 'bell' if bad keypress
        self._entry['invalidcommand'] = 'bell'

    @staticmethod
    def _is_valid(entry):
        """Test to see if entry is acceptable (either empty, or able to be
        converted to the desired type.)
        The _BaseEntryFrame class assumes the entry contents should be
        a float, and that a blank entry should be filled with 0.00.  A subclass
        that wants non-float entries must override this method.
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        if entry == '-':
            return True  # OK to start entering a negative value
        try:
            float(entry)
            return True
        except ValueError:
            return False

    # TODO: consider using @property here
    def get_value(self):
        """Returns the contents of the Entry widget as a str.
        Known issue: loss of decimal places if contents a decimal number.
        e.g. if set with 0.00, becomes '0.0'.
        :return: (str)
        """
        return self._value_var.get()

    def set_value(self, val):
        """Sets the contents of the Entry widget to val, and updates
        self.current_val.
        """
        self._value_var.set(val)

        # Tentatively, the fix to issues with toolbars detecting refreshes when
        # subspectra are reloaded is to not update current_val directly here,
        # but call _save_entry:
        self._save_entry()
        # self.current_value = val


class ArrayBox(_BaseEntryFrame):
    """
    Overrides _BaseEntryFrame to accept a numpy 2D-array, and a coordinate to a
    specific cell in the array to read to/write from.

    Methods overridden: (public)
        * set_value
    """

    def __init__(self, parent=None,
                 array=None, coord=(0, 0),
                 **options):
        """Extend _BaseEntryFrame with references to a 2-D array and the
        coordinate to a specific cell in the array.

        :param array: a 2-D numpy array.
        :param coord: (int, int) tuple for the (row, column) of the array to
        associate the Entry with."""
        self._array = array
        self._row, self._col = coord
        self._initial_value = self._array[self._row, self._col]
        _BaseEntryFrame.__init__(self, parent, **options)

    def _save_entry(self):
        """Record widget's current value to the array, filling the entry with
        0.00 if it was empty.

        Currently assumes, if the array has more than one row, that it is meant
        to be a symmetric matrix, and updates the cross-diagonal element
        as well.
        """
        if not self._value_var.get():
            self._value_var.set(0.00)
        self.current_value = float(self._value_var.get())
        self._array[self._row, self._col] = self.current_value
        # if more than one row, assume J matrix and fill cross-diagonal element
        if self._array.shape[0] > 1:
            self._array[self._col, self._row] = self.current_value

    def set_value(self, val):
        """Set the Entry contents to val, and save it to the associated
        array.
        """
        self._value_var.set(val)
        self._save_entry()


class ArraySpinBox(ArrayBox):
    """A subclass of ArrayBox using a SpinBox instead of an Entry widget."""

    def __init__(self, parent=None, from_=0.00, to=100.00, increment=1,
                 realtime=False,
                 **options):
        """Extend super.__init__ with kwargs for the SpinBox
        initialization, and a boolean flag for desired spinbox behavior.

        :param from_: (float) Minimum value for the SpinBox entry.
        :param to: (float) Maximum value for the SpinBox entry.
        :param increment: (float) size of increment/decrement to SpinBox
        entry when a SpinBox arrow is clicked.
        :param realtime: (boolean) True if view should be constantly updated
        while the mouse button is held down (e.g. as an up/down widget arrow
        is depressed).
        """
        self._realtime = realtime
        self._spinbox_kwargs = {'from_': from_,
                                'to': to,
                                'increment': increment}
        ArrayBox.__init__(self, parent, **options)

    def _add_entry(self):
        """Override ArrayEntry method to add a SpinBox widget rather than an
        Entry widget."""
        self._add_spinbox(**self._spinbox_kwargs)

    def _add_spinbox(self, **kwargs):
        """Add a SpinBox widget to the ArraySpinBox frame."""
        self._entry = Spinbox(self, width=7,
                              validate='key',  # check for number on keypress
                              **kwargs)
        self._entry.pack(side=TOP, fill=X)
        self._entry.config(textvariable=self._value_var)

    def _bind_entry(self):
        """Extend the ArrayFrame method to include bindings for mouse button
        press/release.
        """
        self._entry.bind('<Return>', lambda event: self._on_return(event))
        self._entry.bind('<Tab>', lambda event: self._on_tab(event))
        self._entry.bind('<FocusOut>', lambda event: self._refresh())
        self._entry.bind('<FocusIn>',
                         lambda event: self._entry.selection('range', 0, END))
        self._entry.bind('<ButtonPress-1>', lambda event: self._on_press())
        self._entry.bind('<ButtonRelease-1>', lambda event: self._on_release())

    def _on_press(self):
        """Trigger the 'update view' loop if 'realtime' behavior was
        specified."""
        if self._realtime:
            self._loop_refresh()

    def _loop_refresh(self):
        """Refresh the view every 50 ms until cancelled by the _on_release
        method.
        """
        self._refresh()
        self.button_held_job = self._root().after(50, self._loop_refresh)

    def _on_release(self):
        """Cancel _loop_refresh if 'realtime' behavior was specified."""
        if self._realtime:
            self._root().after_cancel(self.button_held_job)

        # A 1-ms delay allows the StringVar to be updated prior to the
        # _entry_is_changed check. See related StackOverflow question:
        # https://stackoverflow.com/questions/46504930/
        self.after(1, self._refresh)


class VarBox(_BaseEntryFrame):
    """
    A subclass of _BaseEntryFrame that takes a dict as an argument,
    and reads/writes from/to that dict.

    Requirements:
        The dict must use the 'name' kwarg as the key, and have a val of the
        same type as the Entry widget.
    """

    def __init__(self, parent=None, name='', dict_=None, **options):
        """Initialize, with the initial Entry value as dict_[name].

        :param parent: the parent tkinter object
        :param name: used as text for the Label widget, plus used as a dict key
        and as a name for identifying the widget.
        :param **options: the standard optional kwargs for a Frame object
        """
        self._dict = dict_
        self._initial_value = self._dict[name]
        _BaseEntryFrame.__init__(self, parent, name, **options)

    def _save_entry(self):
        """Saves widget's entry in the parent's dict, filling the entry with
        0.00 if it was empty.
        """
        if not self._value_var.get():
            self._value_var.set(0.00)
        self.current_value = float(self._value_var.get())
        self._dict[self._name] = self.current_value


class IntBox(VarBox):
    """Subclass of VarBox where Entry is restricted to integers only."""

    def __init__(self, parent=None, **options):
        VarBox.__init__(self, parent, **options)

    # The only thing keeping Intbox from just using MixinInt is that
    # _save_entry needs to save to a dict. TODO: refactor for composition
    def _save_entry(self):
        """Saves widget's entry in the parent's dict, filling the entry with
        0.00 if it was empty.
        """
        if not self._value_var.get():  # if entry left blank,
            self._value_var.set(0)  # fill it with zero
        value = int(self._value_var.get())
        self.current_value = value
        # Add the widget's status to the container's dictionary
        self._dict[self._name] = value

    @staticmethod
    def _is_valid(entry):
        """Test to see if entry is acceptable (either empty, or able to be
        converted to the desired type.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        if entry == '-':
            return True  # OK to try and enter a negative value
        try:
            int(entry)
            return True
        except ValueError:
            return False


# TODO: decide if VarButtonBox will be useful in this project; delete if not
class VarButtonBox(VarBox):
    """
    A deluxe VarBox that is closer to WINDNMR-style entry boxes.
    ent = entry that holds the value used for calculations
    increment = the amount added to or subtracted from ent by the buttons
    minus and plus buttons subtract/add once;
    up and down buttons repeat as long as button held down.
    Arguments:
    -text: appears above the entry box
    -default: default value in entry
    """

    # To do: use inheritance to avoid repeating code for different widgets
    def __init__(self, from_=0.00, to=100.00, increment=1, realtime=False,
                 **options):
        VarBox.__init__(self, **options)

        # Following attributes/arguments are for consistency with SpinBox API
        # from_ and to not implemented yet here
        self.min = from_
        self.max = to
        self.increment = increment
        self.realtime = realtime

        self.add_increment_widgets()

    def add_increment_widgets(self):
        increment_frame = Frame(self)
        increment_frame.rowconfigure(0,
                                     minsize=30)  # make 2 rows ~same height
        increment_frame.columnconfigure(2,
                                        weight=1)  # lets arrow buttons fill
        increment_frame.pack(side=TOP, expand=Y, fill=X)

        minus = Button(increment_frame, text='-',
                       command=lambda: self.decrease())
        plus = Button(increment_frame, text='+',
                      command=lambda: self.increase())
        up = Button(increment_frame, text=up_arrow, command=lambda: None)
        up.bind('<Button-1>', lambda event: self.zoom_up())
        up.bind('<ButtonRelease-1>', lambda event: self.stop_action())
        minus.grid(row=0, column=0, sticky=NSEW)
        plus.grid(row=0, column=1, sticky=NSEW)
        up.grid(row=0, column=2, sticky=NSEW)

        # Increment is also limited to numerical entry
        increment_entry = Entry(increment_frame, width=4, validate='key')
        increment_entry.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        self.increment_var = StringVar()
        increment_entry.config(textvariable=self.increment_var)
        self.increment_var.set(str(1))  # 1 replaced by argument later?
        increment_entry['validatecommand'] = (self.register(self._is_valid),
                                              '%P')
        increment_entry['invalidcommand'] = 'bell'
        down = Button(increment_frame, text=down_arrow, command=lambda: None)
        down.grid(row=1, column=2, sticky=NSEW)
        down.bind('<Button-1>', lambda event: self.zoom_down())
        down.bind('<ButtonRelease-1>', lambda event: self.stop_action())

        self.mouse1 = False  # Flag used to check if left button held down

    def stop_action(self):
        """ButtonRelease resets self.mouse1 flag to False"""
        self.mouse1 = False

    def increase(self):
        """Increases ent by inc"""
        current = float(self._value_var.get())
        increment = float(self.increment_var.get())
        self._value_var.set(str(current + increment))
        self._on_tab()

    def decrease(self):
        """Decreases ent by inc"""
        current = float(self._value_var.get())
        decrement = float(self.increment_var.get())
        self._value_var.set(str(current - decrement))
        self._on_tab()

    def zoom_up(self):
        """Increases ent by int as long as button-1 held down"""
        self.mouse1 = True
        self.change_value(float(self.increment_var.get()))

    def zoom_down(self):
        """Decreases ent by int as long as button-1 held down"""
        decrement = - float(self.increment_var.get())
        self.mouse1 = True
        self.change_value(decrement)

    def change_value(self, increment):
        """Adds increment to the value in ent

        :param increment: (float) the change to be made to the float value of
        the current Entry contents."""
        if self.mouse1:
            current_float = float(self._value_var.get())
            new_float = current_float + increment
            self._value_var.set(str(new_float))
            self._on_tab()  # store value, call _callback

            # Delay was originally set to 10, but after MVC refactor this
            #  caused an infinite loop (apparently a race condition where
            #  stop action never fired. Testing with the two singlet DNMR
            #  _callback: still loops at 30 ms; 40 works but uneven; 50 works
            #  fine.
            # May want to refactor how up/down arrows work
            self.after(50, lambda: self.change_value(increment))


class SimpleVariableBox(_BaseEntryFrame):
    """Subclass of _BaseEntryFrame that stores the entry value as its
    current_value argument and has a minimum value limit.
    """

    def __init__(self, parent=None, value=0.5, min_=0, **options):
        """Extend _BaseEntryFrame by implementing initial value and minimum
        value parameters.

        :param value: (float) Value to instantiate Entry with.
        :param min_: (float) Minimum value the Entry is allowed to hold.
        """
        self._initial_value = value
        self._min_value = min_
        _BaseEntryFrame.__init__(self, parent, **options)

    def _save_entry(self):
        """Overrides parent method so that an empty Entry field is filled
        with min value.
        """
        if not self._value_var.get():  # if entry left blank,
            self._value_var.set(self._min_value)
        self.current_value = float(self._value_var.get())


class MixinHorizontal:
    """Override _add_label and _add_entry methods to provide a horizontal
    arrangement instead of vertical.
    """

    def _add_label(self):
        """Add self._name to a Label at the left of the frame."""
        Label(self, text=self._name, bg=self._color, bd=0).pack(side=LEFT)

    def _add_entry(self):
        """Add an Entry widget."""
        self._entry = Entry(self, width=7,
                            validate='key')  # check for number on keypress)
        self._entry.pack(side=LEFT, fill=X)
        self._entry.config(textvariable=self._value_var)


class MixinInt:
    """Override _save_entry and _is_valid methods to restrict Entry values to
    integers."""

    def _save_entry(self):
        """Saves widget's entry as current_value, filling the entry with
        0 if it was empty.
        """
        if not self._value_var.get():  # if entry left blank,
            self._value_var.set(0)  # fill it with zero
        value = int(self._value_var.get())
        self.current_value = value

    @staticmethod
    def _is_valid(entry):
        """Test to see if entry is acceptable (either empty, or able to be
        converted to the desired type.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        if entry == '-':
            return True  # OK to try and enter a negative value
        try:
            int(entry)
            return True
        except ValueError:
            return False


class MixinIntRange:
    """Similar to MixinIntRange, but restricts integer range to specified
    min/max values.

    Currently hardcoded to 2-8 range."""
    # TODO: make general, with min_ and max_ args

    def _save_entry(self):
        """Saves widget's entry in the parent's dict, filling the entry with
        0.00 if it was empty.
        """
        if not self._value_var.get():  # if entry left blank,
            self._value_var.set(0)  # fill it with zero
        value = int(self._value_var.get())
        self.current_value = value

    @staticmethod
    def _is_valid(entry):
        """Test to see if entry is acceptable (either empty, or able to be
        converted to the desired type.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            int(entry)
            return 2 <= int(entry) <= 8
        except ValueError:
            return False


class HorizontalIntBox(MixinHorizontal, IntBox):
    """An IntBox with a horizontal layout."""

    def __init__(self, **kwargs):
        super(HorizontalIntBox, self).__init__(**kwargs)


class HorizontalEntryFrame(MixinHorizontal, SimpleVariableBox):
    """A SimpleVariableBox with a horizontal layout."""

    def __init__(self, **kwargs):
        super(HorizontalEntryFrame, self).__init__(**kwargs)


class HorizontalIntEntryFrame(MixinHorizontal, MixinInt, SimpleVariableBox):
    """A SimpleVariableBox with a horizontal layout, and with Entry values
    limited to integers."""

    def __init__(self, **kwargs):
        super(HorizontalIntEntryFrame, self).__init__(**kwargs)


class HorizontalRangeEntryFrame(MixinHorizontal, MixinIntRange,
                                SimpleVariableBox):
    """A SimpleVariableBox with a horizontal layout, and with Entry values
    limited to integers in the 2-8 range (currently hardcoded in
    MixinIntRange).
    """

    def __init__(self, **kwargs):
        super(HorizontalRangeEntryFrame, self).__init__(**kwargs)


if __name__ == '__main__':
    import numpy as np


    class DummyFrame(Frame):
        def __init__(self, parent, **options):
            Frame.__init__(self, parent, **options)
            self.vars = {}


    def dummy_callback():
        print('callback called')


    dummy_array = np.array([[1, 42, 99]])
    dummy_dict = {'VarBox example': 11.00,
                  'IntBox example': 12,
                  'VarButtonBox example': 42.0}

    root = Tk()
    root.title('test widgets')
    mainwindow = DummyFrame(root)
    mainwindow.pack()

    widgets = {'Array Box': ArrayBox,
               'ArraySpinBox': ArraySpinBox,
               'VarBox': VarBox,
               'IntBox': IntBox}
    widget_list = [val(parent=mainwindow, name=key, array=dummy_array,
                       callback=dummy_callback) if 'Array' in key
                   else val(parent=mainwindow, name=key + ' example',
                            dict_=dummy_dict, callback=dummy_callback)
                   for key, val in widgets.items()]
    simple_variable_box = SimpleVariableBox(parent=mainwindow,
                                            name='SimpleVariableBox example',
                                            value=20.0)
    widget_list.append(simple_variable_box)
    horizontal_test = HorizontalRangeEntryFrame(parent=mainwindow,
                                                name='horizontal test',
                                                value=18)
    widget_list.append(horizontal_test)

    for widget in widget_list:
        widget.pack(side=LEFT)

    demo_varbuttonbox = VarButtonBox(
        parent=mainwindow, name='VarButtonBox example',
        dict_=dummy_dict, callback=dummy_callback, realtime=True,
        from_=0.00, to=100.00, increment=1)
    demo_varbuttonbox.pack(side=LEFT)

    # TODO: add code to test behavior as well as instantiation

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

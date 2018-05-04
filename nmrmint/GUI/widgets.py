"""Custom widgets composed from standard tkinter widgets.

Provides the following classes:
* BaseEntryFrame: a base class for a Frame that contains a Label and an Entry
widget, has custom behavior, and calls back when a change to the entry has
been committed.

* ArrayBox: a subclass of BaseEntryFrame that reads/writes its value from/to a
2-D numpy array.

* ArraySpinBox: a subclass of ArrayBox that uses a SpinBox widget instead of
an Entry widget.

* VarBox: Similar to BaseEntryFrame, but is not provided a data structure or
controller callback in its arguments. Instead, it assumes the parent has the
necessary attribute and method. TODO: refactor this out of the first-order
toolbars and use ArrayBox instead.

* IntBox: Similar to VarBox, but with the Entry restricted to integers
instead of floats. TODO: refactor so that it either subclasses ArrayBox or so
that the widgets in this module use subclasses of Entry specific to
float-only or int-only entries.

* VarButtonBox: emulates the WINDNMR-style entry boxes, like a deluxe
SpinBox. TODO: refactor so that up/down arrow behavior, methods etc are
identical to those in ArraySpinBox.

* SimpleVariableBox: A subclass of BaseEntryFrame that takes initial and
minimum-value argument, instantiates the Entry with the initial value,
and defaults to the custom minimum value when empty.
"""
from tkinter import *

up_arrow = u"\u21e7"
down_arrow = u"\u21e9"
left_arrow = u"\u21e6"
right_arrow = u"\u21e8"


class BaseEntryFrame(Frame):
    """A tkinter Frame that holds a labeled entry widget, takes a function
    ('controller') as an argument, and calls that function when a change is
    committed to the Entry's value.

    BaseEntryFrame is intended as a new base class that will be inherited from.

    Methods:
        initialize, add_label, add_entry, bind_entry, and validate_entry: are
        called by __init__ to initialize BaseEntryFrame. TODO: review all code
        and learn appropriate use of private methods to refactor.

        on_return: binding for <Return>

        on_tab: binding for <Tab>

        refresh: requests view plot update using the latest data

        entry_is_changed: determines if the Entry value has been changed
        since the variable was last saved.

        find_next_entry: cycles throught the tkinter widget traversal until
        another Entry-like object found, then returns that object.

        is_valid: checks that the current Entry value is acceptable
        (default: either blank, or a number).

        save_entry: saves the Entry value to the relevant data structure.
        Intended to be overwritten by subclasses of BaseEntryFrame.

    TODO:
        * 'model' is a misleading argument name when a MVC design is used.
        Refactor, e.g. to 'callback'
    """

    def __init__(self, parent=None, name='', color='white',
                 controller=None,
                 **options):
        """
        __init__ is broken into multiple method references, to allow
        subclasses/mixins to modify as needed.

        Keyword arguments:
        :param parent: The parent tkinter object
        :param name: (str) Optional name. Used as Label text as well as
        widget identification.
        :param color: (str) Default color for widget and contents.
        :param controller: function to be called when change in Entry contents
        committed.
        :param options: (dict) Standard kwargs for a tkinter Frame
        """
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=0,
                       background=color, **options)
        self.name = name
        self.color = color
        self.controller = controller

        # How the initial value for the widget depends on subclass, so:
        # if not self.initial_value:
        #     self.initial_value = 0.00  # Should be overridden by subclass

        self.initialize()
        self.add_label()
        self.add_entry()
        self.bind_entry()
        self.validate_entry()

    def initialize(self):
        """
        Create a StringVar object; initialize self.value with the initial
        number, and initialize StringVar with that same value.

        Subclasses of BasentryFrame should overwrite this function to
        accomodate
        however initial values are passed into them.
        """
        self.value_var = StringVar()
        self.current_value = self.initial_value
        self.value_var.set(self.current_value)

    def add_label(self):
        """Add self.name to a Label at the top of the frame."""
        Label(self, text=self.name, bg=self.color, bd=0).pack(side=TOP)

    def add_entry(self):
        """Add an Entry widget to the BaseEntryFrame.

        Subclasses of EntryBox that use a different entry widget (e.g. SpinBox)
        should overwrite this function.
        """
        self.entry = Entry(self, width=7,
                           validate='key')  # check for number on keypress)
        self.entry.pack(side=TOP, fill=X)
        self.entry.config(textvariable=self.value_var)

    def bind_entry(self):
        """Define behavior when the Entry widget loses focus.

        BaseEntryFrame assumes action should only be taken when a change in the
        Entry widget is "committed" by hitting Return, Tab, or clicking
        outside the widget.
        Subclasses may overwrite/extend bind_entry to tailor behavior.
        """
        self.entry.bind('<Return>', lambda event: self.on_return(event))
        self.entry.bind('<Tab>', lambda event: self.on_tab(event))
        # self.entry.bind('<FocusOut>', lambda event: self.refresh())
        self.entry.bind('<FocusIn>',
                        lambda event: self.entry.select_range(0, END))

    def on_return(self, event):
        """Refresh the view and shift focus when Return key is hit."""
        self.refresh()
        self.find_next_entry(self.entry).focus()

    def refresh(self):
        """Save the Entry value to the data structure then request a view
        refresh."""
        if self.entry_is_changed():
            self.save_entry()
            self.controller()

    def entry_is_changed(self):
        """Check if the current Entry value differs from the last saved
        value.

        :return: True if changed, False if not.
        """
        return str(self.current_value) != self.value_var.get()

    def save_entry(self):
        """Saves widget's entry as self.stored_value , filling the entry with
        0.00 if it was empty.
        Subclasses should overwrite save_entry to suit needs of their data
        type and call to controller
        """
        if not self.value_var.get():  # if entry left blank,
            self.value_var.set(0.00)  # fill it with zero
        value = float(self.value_var.get())
        self.current_value = value

    def find_next_entry(self, current_widget):
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
            return self.find_next_entry(next_entry)

    def on_tab(self, *event):
        """Refresh the view and shift focus when Tab key is hit."""
        self.on_return(event)
        return 'break'  # override default tkinter tab behavior

    def validate_entry(self):
        """Restrict Entry inputs to a valid type"""
        # check on each keypress if new result will be valid
        self.entry['validatecommand'] = (self.register(self.is_valid), '%P')
        # sound 'bell' if bad keypress
        self.entry['invalidcommand'] = 'bell'

    @staticmethod
    def is_valid(entry):
        """Test to see if entry is acceptable (either empty, or able to be
        converted to the desired type.)
        The BaseEntryFrame class assumes the entry contents should be
        a float, and that a blank entry should be filled with 0.00.  A subclass
        that wants non-float entries must override this method.
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def get_value(self):
        return self.value_var.get()

    def set_value(self, val):
        self.value_var.set(val)
        # self.refresh()


class ArrayBox(BaseEntryFrame):
    """
    Overrides BaseEntryFrame to accept a numpy 2D-array, and a coordinate to a
    specific cell in the array to read to/write from.

    Methods overridden:
        __init__
        save_entry

    Attributes:
        array: the 2D array to read/write from/to.
        row, col: the row and column of the array to read/write the Entry
        value from/to.
        initial_value: used to instantiate the Entry value

    """
    def __init__(self, parent=None,
                 array=None, coord=(0, 0),
                 **options):
        """Extend BaseEntryFrame with references to a 2-D array and the
        coordinate to a specific cell in the array.

        :param array: a 2-D numpy array.
        :param coord: (int, int) tuple for the (row, column) of the array to
        associate the Entry with."""
        self.array = array
        self.row, self.col = coord
        self.initial_value = self.array[self.row, self.col]
        BaseEntryFrame.__init__(self, parent, **options)

    def save_entry(self):
        """Record widget's current value to the array, filling the entry with
        0.00 if it was empty.

        Currently assumes, if the array has more than one row, that it is meant
        to be a symmetric matrix, and updates the cross-diagonal element
        as well.
        """
        if not self.value_var.get():
            self.value_var.set(0.00)
        self.value = float(self.value_var.get())
        self.array[self.row, self.col] = self.value
        # if more than one row, assume J matrix and fill cross-diagonal element
        if self.array.shape[0] > 1:
            self.array[self.col, self.row] = self.value


class ArraySpinBox(ArrayBox):
    """
    A subclass of ArrayBox using a SpinBox instead of an Entry widget.

    Methods:
        add_spinbox: Adds a SpinBox widget to the ArraySpinBox frame.
        on_press: Callback for <ButtonPress-1>
        loop_refresh: Constantly update the view until cancelled
        on_release: Callback for <ButtonRelease-1>

    Methods overridden:
        __init__
        add_entry
        bind_entry

    Attributes:
        realtime: (bool) Determines if view should be constantly updated
        while the mouse button is held down (e.g. as an up/down widget arrow
        is depressed)

    Arguments (in addition to standard ArrayBox options):
        from_, to, increment: SpinBox arguments (minimum and maximum values,
        and incremental change on each arrow click)

        realtime: True if data/controller should be refreshed as the SpinBox
        arrow button is held down.
    """
    def __init__(self, parent=None, from_=0.00, to=100.00, increment=1,
                 realtime=False,
                 **options):
        """Extend super.__init__ with kwargs for the SpinBox
        initialization, and a boolean flag for desired spinbox behavior.

        :param from_: (float) Minimum value for the SpinBox entry.
        :param to: (float) Maximum value for the SpinBox entry.
        :param increment: (float) size of increment/decrement to SpinBox
        entry when a SpinBox arrow is clicked.
        :param realtime: (boolean) True if data/controller should be refreshed
        as the SpinBox arrow button is held down."""
        self.realtime = realtime
        self.spinbox_kwargs = {'from_': from_,
                               'to': to,
                               'increment': increment}
        ArrayBox.__init__(self, parent, **options)

    def add_entry(self):
        """Override ArrayEntry method to add a SpinBox widget rather than an
        Entry widget."""
        self.add_spinbox(**self.spinbox_kwargs)

    def add_spinbox(self, **kwargs):
        """Add a SpinBox widget to the ArraySpinBox frame."""
        self.entry = Spinbox(self, width=7,
                             validate='key',  # check for number on keypress
                             **kwargs)
        self.entry.pack(side=TOP, fill=X)
        self.entry.config(textvariable=self.value_var)

    def bind_entry(self):
        """Extend the ArrayFrame method to include bindings for mouse button
        press/release.
        """
        self.entry.bind('<Return>', lambda event: self.on_return(event))
        self.entry.bind('<Tab>', lambda event: self.on_tab(event))
        # self.entry.bind('<FocusOut>', lambda event: self.refresh())
        self.entry.bind('<FocusIn>',
                        lambda event: self.entry.selection('range', 0, END))
        self.entry.bind('<ButtonPress-1>', lambda event: self.on_press())
        self.entry.bind('<ButtonRelease-1>', lambda event: self.on_release())

    def on_press(self):
        """Trigger the 'update view' loop if 'realtime' behavior was
        specified."""
        if self.realtime:
            self.loop_refresh()

    def loop_refresh(self):
        """Refresh the view every 50 ms until cancelled by the on_release
        method.
        """
        self.refresh()
        self.button_held_job = self._root().after(50, self.loop_refresh)

    def on_release(self):
        """Cancel the loop_refresh loop if 'realtime' behavior was specified."""
        if self.realtime:
            self._root().after_cancel(self.button_held_job)

        # A 1-ms delay allows the StringVar to be updated prior to the
        # entry_is_changed check. See related StackOverflow question:
        # https://stackoverflow.com/questions/46504930/
        self.after(1, self.refresh)


class VarBox(BaseEntryFrame):
    """
    A subclass of BaseEntryFrame that takes a dict as an argument,
    and reads/writes from/to that dict.

    Requirements:
        The dict must use the 'name' kwarg as the key, and have a val of the
        same type as the Entry widget.

    Overrides:
        save_entry

    Attributes:
        dict: (dict) Reference to 'dict' kwarg
        initial_value: the initial val of dict[name]
    TODO:
        * refactor code so that this class (which is largely redundant with
        EntryBox and its subclasses) can be eliminated.
        * review all code and learn appropriate use of private
        methods to refactor.
    """
    def __init__(self, parent=None, name='', dict_=None, **options):
        """Associate a name with the VarBox widget, and read the default
        value for its Entry.

        Keyword arguments:
            parent: the parent tkinter object
            name: used as text for the Label widget, plus used as a dict key
            and as a name for identifying the widget.
            default: The default value to initiate the Entry widget with
            **options: the standard optional kwargs for a Frame object
        """
        self.dict = dict_
        self.initial_value = self.dict[name]
        BaseEntryFrame.__init__(self, parent, name, **options)

    def save_entry(self):
        """Saves widget's entry in the parent's dict, filling the entry with
        0.00 if it was empty.
        """
        if not self.value_var.get():  # if entry left blank,
            self.value_var.set(0.00)  # fill it with zero
        value = float(self.value_var.get())
        self.current_value = value
        # Add the widget's status to the container's dictionary
        self.dict[self.name] = value


class IntBox(VarBox):
    """Overrides VarBox so that the Entry is restricted to integers only.

    Method overwritten:
        is_valid
    """
    # Future refactor options: either create a base class for an input box
    # that varies in its input restriction (float, int, str etc), and/or
    # look into tkinter built-in entry boxes as component.
    def __init__(self, parent=None, **options):
        VarBox.__init__(self, parent, **options)

    def save_entry(self):
        """Saves widget's entry in the parent's dict, filling the entry with
        0.00 if it was empty.
        """
        if not self.value_var.get():  # if entry left blank,
            self.value_var.set(0)  # fill it with zero
        value = int(self.value_var.get())
        self.current_value = value
        # Add the widget's status to the container's dictionary
        self.dict[self.name] = value

    @staticmethod
    def is_valid(entry):
        """Test to see if entry is acceptable (either empty, or able to be
        converted to the desired type.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            int(entry)
            return True
        except ValueError:
            return False


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
        increment_entry['validatecommand'] = (self.register(self.is_valid),
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
        current = float(self.value_var.get())
        increment = float(self.increment_var.get())
        self.value_var.set(str(current + increment))
        self.on_tab()

    def decrease(self):
        """Decreases ent by inc"""
        current = float(self.value_var.get())
        decrement = float(self.increment_var.get())
        self.value_var.set(str(current - decrement))
        self.on_tab()

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
            current_float = float(self.value_var.get())
            new_float = current_float + increment
            self.value_var.set(str(new_float))
            self.on_tab()  # store value, call controller

            # Delay was originally set to 10, but after MVC refactor this
            #  caused an infinite loop (apparently a race condition where
            #  stop action never fired. Testing with the two singlet DNMR
            #  controller: still loops at 30 ms; 40 works but uneven; 50 works
            #  fine.
            # May want to refactor how up/down arrows work
            self.after(50, lambda: self.change_value(increment))


class SimpleVariableBox(BaseEntryFrame):
    """Subclass of BaseEntryFrame that takes a variable as an argument and
    rewrites it with the Entry's contents when changes are committed.

    Method overwritten:
    save_entry: If entry left blank, it is filled with the minimum value
    specified by new kwarg 'min'.
    """

    def __init__(self, parent=None, value=0.5, min=0, **options):
        """Extend BaseEntryFrame by implementing initial value and minimum
        value parameters.

        :param value: (float) Value to instantiate Entry with.
        :param min: (float) Minimum value the Entry is allowed to hold.
        """
        self.initial_value = value
        self.minimum_value = min
        BaseEntryFrame.__init__(self, parent, **options)

    def save_entry(self):
        """Overrides parent method so that an empty Entry field is filled
        with min value.
        """
        if not self.value_var.get():  # if entry left blank,
            self.value_var.set(self.minimum_value)
        value = float(self.value_var.get())
        self.current_value = value


class MixinHorizontal:
    """Override add_label and add_entry methods to provide a horizontal
    arrangement instead of vertical.
    """
    def add_label(self):
        """Add self.name to a Label at the left of the frame."""
        Label(self, text=self.name, bg=self.color, bd=0).pack(side=LEFT)

    def add_entry(self):
        """Add an Entry widget."""
        self.entry = Entry(self, width=7,
                           validate='key')  # check for number on keypress)
        self.entry.pack(side=LEFT, fill=X)
        self.entry.config(textvariable=self.value_var)


class MixinInt:
    """Override save_entry and is_valid methods to restrict Entry values to
    integers."""
    def save_entry(self):
        """Saves widget's entry in the parent's dict, filling the entry with
        0.00 if it was empty.
        """
        if not self.value_var.get():  # if entry left blank,
            self.value_var.set(0)  # fill it with zero
        value = int(self.value_var.get())
        self.current_value = value

    @staticmethod
    def is_valid(entry):
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
    def save_entry(self):
        """Saves widget's entry in the parent's dict, filling the entry with
        0.00 if it was empty.
        """
        if not self.value_var.get():  # if entry left blank,
            self.value_var.set(0)  # fill it with zero
        value = int(self.value_var.get())
        self.current_value = value

    @staticmethod
    def is_valid(entry):
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

        @staticmethod
        def request_plot():
            print('plot requested')

    def dummy_controller():
        print('controller called')

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
                       controller=dummy_controller) if 'Array' in key
                   else val(parent=mainwindow, name=key+' example',
                            dict_=dummy_dict, controller=dummy_controller)
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
        dict_=dummy_dict, controller=dummy_controller, realtime=True,
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

"""Custom widgets composed from standard tkinter widgets.

Provides the following classes:
* EntryFrame: a base class for a Frame that contains a Label and an Entry
widget, has custom behavior, and calls back when a change to the entry has
been committed.

* ArrayBox: a subclass of EntryFrame that reads/writes its value from/to a
2-D numpy array.

* ArraySpinBox: a subclass of ArrayBox that uses a SpinBox widget instead of
an Entry widget.

* VarBox: Similar to EntryFrame, but is not provided a data structure or
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
"""
from tkinter import *

up_arrow = u"\u21e7"
down_arrow = u"\u21e9"
left_arrow = u"\u21e6"
right_arrow = u"\u21e8"


class EntryFrame(Frame):
    """
    A tkinter Frame that holds a labeled entry widget, takes a function as an
    argument, and calls that function when a change is committed to the Entry's
    value.

    EntryFrame will call the function (provided as 'model' in the arguments)
    when a change in the entry's value is committed.

    EntryFrame is intended as a new base class that will be inherited from.
    For example, the initialize() method needs to be overwritten to change
    the default initial entry of 0.00.

    Methods:
        initialize, add_label, add_entry, bind_entry, and validate_entry: are
        called by __init__ to initialize EntryFrame. TODO: review all code
        and learn appropriate use of private methods to refactor.

        on_return: binding for <Return>

        on_tab: binding for <Tab>

        refresh: requests view plot update using the latest data

        entry_is_changed: determines if the Entry value has been changed
        since the variable was last saved.

        find_next_entry: cycles throught the tkinter widget traversal until
        another Entry-like object found, then returns that object.

        validate_entry: checks that the current Entry value is acceptable
        (either blank, or a number).

        is_number: tests to see if a value is either a number or None.

        save_entry: saves the Entry value to the relevant data structure.
        Intended to be overwritten by subclasses of EntryFrame.

    TODO:
        * 'model' is a misleading argument name when a MVC design is used.
        Refactor, e.g. to 'callback'
    """

    def __init__(self, parent=None, name='', color='white',
                 model=None,
                 **options):
        """
        __init__ is broken into multiple method references, to allow
        subclasses to modify as needed.

        Keyword arguments:
        :param parent: The parent tkinter object
        :param name: (str) Optional name. Used as Label text as well as
        widget identification.
        :param color: (str) Default color for widget and contents.
        :param model: function to be called when change in Entry contents
        committed.
        :param options: (dict) Standard kwargs for a tkinter Frame
        """
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=0,
                       background=color, **options)
        self.name = name
        self.color = color
        self.model = model

        self.initialize()
        self.add_label()
        self.add_entry()
        self.bind_entry()
        self.validate_entry()

    def initialize(self):
        """
        Create a StringVar object; initialize self.value with the initial
        number, and initialize StringVar with that same value.

        Subclasses of EntryFrame should overwrite this function to accomodate
        however initial values are passed into them.
        """
        self.value_var = StringVar()
        self.value = 0.0
        self.value_var.set(self.value)

    def add_label(self):
        """Add self.name to a Label at the top of the frame."""
        Label(self, text=self.name, bg=self.color, bd=0).pack(side=TOP)

    def add_entry(self):
        """Add an Entry widget to the EntryFrame.

        Subclasses of EntryBox that use a different entry widget (e.g. SpinBox)
        should overwrite this function.
        """
        self.entry = Entry(self, width=7,
                           validate='key')  # check for number on keypress)
        self.entry.pack(side=TOP, fill=X)
        self.entry.config(textvariable=self.value_var)

    def bind_entry(self):
        """Define behavior when the Entry widget loses focus.

        EntryFrame assumes action should only be taken when a change in the
        Entry widget is "committed" by hitting Return, Tab, or clicking
        outside the widget.
        Subclasses may overwrite/extend bind_entry to tailor behavior.
        """
        self.entry.bind('<Return>', lambda event: self.on_return(event))
        self.entry.bind('<Tab>', lambda event: self.on_tab(event))
        self.entry.bind('<FocusOut>', lambda event: self.refresh())

    def on_return(self, event):
        """Refresh the view and shift focus when Return key is hit."""
        self.refresh()
        self.find_next_entry(self.entry).focus()

    def refresh(self):
        """Save the Entry value to the data structure then request a view
        refresh."""
        if self.entry_is_changed():
            self.save_entry()
            self.model()

    def entry_is_changed(self):
        """Check if the current Entry value differs from the last saved
        value.

        :return: True if changed, False if not.
        """
        return self.value != float(self.value_var.get())

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

    def validate_entry(self):
        """Restrict Entry inputs to numerical (or blank)

        The base EntryFrame class assumes the entry contents should be
        numerical.  A subclass that wants non-numeric entries must override
        this method.
        """
        # check on each keypress if new result will be a number
        self.entry['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        self.entry['invalidcommand'] = 'bell'

    @staticmethod
    def is_number(entry):
        """
        tests to see if entry is acceptable (either empty, or able to be
        converted to a float.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def on_tab(self, event):
        """Refresh the view and shift focus when Tab key is hit."""
        self.on_return(event)
        return 'break'  # override default tkinter tab behavior

    def save_entry(self):
        """Saves widget's entry as self.stored_value , filling the entry with
        0.00 if it was empty.
        Subclasses should overwrite save_entry to suit needs of their data
        type and call to model
        """
        if not self.value_var.get():  # if entry left blank,
            self.value_var.set(0.00)  # fill it with zero
        value = float(self.value_var.get())
        self.value = value


class ArrayBox(EntryFrame):
    """
    Overrides EntryFrame to accept a numpy 2D-array, and a coordinate to a
    specific cell in the array to read to/write from.

    Methods overridden:
        __init__
        initialize
        save_entry

    Attributes:
        array: the 2D array to read/write from/to.
        row, col: the row and column of the array to read/write the Entry
        value from/to.

    """
    def __init__(self, parent=None,
                 array=None, coord=(0, 0),
                 **options):
        """Extend EntryFrame with references to a 2-D array and the
        coordinate to a specific cell in the array.

        :param array: a 2-D numpy array.
        :param coord: (int, int) tuple for the (row, column) of the array to
        associate the Entry with."""
        self.array = array
        self.row, self.col = coord
        EntryFrame.__init__(self, parent,
                            # name, color,
                            **options)

    def initialize(self):
        """Read the current value from the 2-D array and associate it with a
        StringVar object."""
        self.value_var = StringVar()
        self.value = self.array[self.row, self.col]
        self.value_var.set(self.value)

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
        if self.array.shape[0] > 1:  # if more than one row, assume J matrix
            self.array[self.col, self.row] = self.value  # fill cross-diagonal
                                                         # element


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
        realtime: True if data/model should be refreshed as the SpinBox arrow
                  button is held down.
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
        :param realtime: (boolean) True if data/model should be refreshed as
        the SpinBox arrow button is held down."""
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
        self.entry.bind('<FocusOut>', lambda event: self.refresh())
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


class VarBox(Frame):
    """
    A tkinter Frame that holds a labeled Entry widget, restricts its input to
    type (float), updates its value to the master.vars dict, and calls
    master.request_plot() when a change is made to the value.

    Requirements:
        The master (aka parent) must have a dict named master.vars and a
        method called request_plot.

    Methods:
        is_number: tests to see if a value is either a number or None.

        entry_is_changed: determines if the Entry value has been changed
        since the variable was last saved.

        on_return: binding for <Return>

        on_tab: binding for <Tab>

        to_dict: update the Entry value in the parent's dictionary

    Attributes (public--see TODO):
        widgetName: (str) Name of the widget; also used as a dict key.
    TODO:
        * refactor code so that this class (which is largely redundant with
        EntryBox and its subclasses) can be eliminated.
        * review all code and learn appropriate use of private
        methods to refactor.
    """
    def __init__(self, parent=None, name='', default=0.00, **options):
        """Associate a name with the VarBox widget, and read the default
        value for its Entry.

        Keyword arguments:
            parent: the parent tkinter object
            name: used as text for the Label widget, plus used as a dict key
            and as a name for identifying the widget.
            default: The default value to initiate the Entry widget with
            **options: the standard optional kwargs for a Frame object
        """
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if a change is made
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    @staticmethod
    def is_number(entry):
        """
        tests to see if entry is acceptable (either empty, or able to be
        converted to a float.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def entry_is_changed(self):
        """Check if the current Entry value differs from the last saved
        value.

        :return: True if changed, False if not.
        """
        return self.master.vars[self.widgetName] != float(self.value.get())

    def on_return(self, event):
        """Refresh the view and shift focus when Return key is hit."""
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        """Refresh the view and shift focus when Tab key is hit."""
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()

    def to_dict(self):
        """Saves widget's entry in the parent's dict, filling the entry with
        0.00 if it was empty.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = float(self.value.get())


class IntBox(Frame):
    """Overrides VarBox so that the Entry is restricted to integers only.

    TODO: not only should this either subclass from VarBox, or create custom
    Entry widgets for floats, ints, etc (see comment below), but the widget
    traversal bindings for return/tab/focus out used by the EntryFrame class
    should be adopted.
    """
    # Future refactor options: either create a base class for an input box
    # that varies in its input restriction (float, int, str etc), and/or
    # look into tkinter built-in entry boxes as component.
    def __init__(self, parent=None, name='', default=0, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP, expand=NO, fill=NONE)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, width=7, validate='key')  # check for int on keypress
        ent.pack(side=TOP, expand=NO, fill=NONE)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))
        ent.bind('<Return>', lambda event: self.on_event(event))
        ent.bind('<FocusOut>', lambda event: self.on_event(event))

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_int), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    @staticmethod
    def is_int(entry):
        """
        tests to see if entry string can be converted to integer
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            int(entry)
            return True
        except ValueError:
            return False

    def on_event(self, event):
        """
        On event: Records widget's status to the container's dictionary of
        values, fills the entry with 0 if it was empty, tells the container
        to send data to the model, and shifts focus to the next entry box (after
        Return or Tab).
        """
        self.to_dict()
        self.master.request_plot()
        event.widget.tk_focusNext().focus()

    def to_dict(self):
        """
        Converts entry to integer, and stores data in container's vars
        dictionary.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = int(self.value.get())


class VarButtonBox(Frame):
    """TODO: harmonize behavior/API of VarButtonBox with ArraySpinBox to
    avoid redundancy or idiosyncratic behavior."""
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
    def __init__(self, parent=None, name='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP)

        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if a change is made
        # To-Do: consistent routines for VarBox, VarButtonBox, ArrayBox etc.
        # e.g. rename on_tab for general purpose on focus-out
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

        # Create a grid for buttons and increment
        minus_plus_up = Frame(self)
        minus_plus_up.rowconfigure(0,
                                   minsize=30)  # make 2 rows ~same height
        minus_plus_up.columnconfigure(2,
                                      weight=1)  # lets arrow buttons fill
        minus_plus_up.pack(side=TOP, expand=Y, fill=X)

        minus = Button(minus_plus_up, text='-',
                       command=lambda: self.decrease())
        plus = Button(minus_plus_up, text='+',
                      command=lambda: self.increase())
        up = Button(minus_plus_up, text=up_arrow, command=lambda: None)
        up.bind('<Button-1>', lambda event: self.zoom_up())
        up.bind('<ButtonRelease-1>', lambda event: self.stop_action())

        self.mouse1 = False  # Flag used to check if left button held down

        minus.grid(row=0, column=0, sticky=NSEW)
        plus.grid(row=0, column=1, sticky=NSEW)
        up.grid(row=0, column=2, sticky=NSEW)

        # Increment is also limited to numerical entry
        increment = Entry(minus_plus_up, width=4, validate='key')
        increment.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        self.inc = StringVar()
        increment.config(textvariable=self.inc)
        self.inc.set(str(1))  # 1 replaced by argument later?
        increment['validatecommand'] = (self.register(self.is_number), '%P')
        increment['invalidcommand'] = 'bell'

        down = Button(minus_plus_up, text=down_arrow, command=lambda: None)
        down.grid(row=1, column=2, sticky=NSEW)
        down.bind('<Button-1>', lambda event: self.zoom_down())
        down.bind('<ButtonRelease-1>', lambda event: self.stop_action())

    @staticmethod
    def is_number(entry):
        """
        tests to see if entry is acceptable (either empty, or able to be
        converted to a float.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def entry_is_changed(self):
        """True if current entry doesn't match stored entry"""
        return self.master.vars[self.widgetName] != float(self.value.get())

    def on_return(self, event):
        """Records change to entry, calls model, and focuses on next widget
        """
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        """Records change to entry, and calls model"""
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()

    def to_dict(self):
        """
        Records widget's contents to the container's dictionary of
        values, filling the entry with 0.00 if it was empty.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = float(self.value.get())

    def stop_action(self):
        """ButtonRelease esets self.mouse1 flag to False"""
        self.mouse1 = False

    def increase(self):
        """Increases ent by inc"""
        current = float(self.value.get())
        increment = float(self.inc.get())
        self.value.set(str(current + increment))
        self.on_tab()

    def decrease(self):
        """Decreases ent by inc"""
        current = float(self.value.get())
        decrement = float(self.inc.get())
        self.value.set(str(current - decrement))
        self.on_tab()

    def zoom_up(self):
        """Increases ent by int as long as button-1 held down"""
        increment = float(self.inc.get())
        self.mouse1 = True
        self.change_value(increment)

    def zoom_down(self):
        """Decreases ent by int as long as button-1 held down"""
        decrement = - float(self.inc.get())
        self.mouse1 = True
        self.change_value(decrement)

    def change_value(self, increment):
        """Adds increment to the value in ent"""
        if self.mouse1:
            self.value.set(str(float(self.value.get()) + increment))
            self.on_tab()  # store value, call model

            # Delay was originally set to 10, but after MVC refactor this
            #  caused an infinite loop (apparently a race condition where
            #  stop action never fired. Testing with the two singlet DNMR
            #  model: still loops at 30 ms; 40 works but uneven; 50 works
            #  fine.
            # May want to refactor how up/down arrows work
            self.after(50, lambda: self.change_value(increment))


if __name__ == '__main__':
    import numpy as np

    class TestFrame(Frame):
        def __init__(self, parent, **options):
            Frame.__init__(self, parent, **options)
            self.vars = {}

        def request_plot(self):
            # for child in self.winfo_children():
            #     print('I have child: ', child.name)
            # print('requesting calculation from the model')
            # print(dummy_array)
            pass

    dummy_array = np.array([[1, 42, 99]])

    root = Tk()
    root.title('test widgets')
    mainwindow = TestFrame(root)
    mainwindow.pack()

    widgets = {'Array Box': ArrayBox,
               'ArraySpinBox': ArraySpinBox,
               'VarBox': VarBox,
               'IntBox': IntBox,
               'VarButtonBox': VarButtonBox}
    widget_list = [val(parent=mainwindow, name=key, array=dummy_array) if
                   'Array' in key
                   else val(parent=mainwindow, name=key)
                   for key, val in widgets.items()]
    for widget in widget_list:
        widget.pack(side=LEFT)

    # TODO: add code to test behavior as well as instantiation
    #
    # baseclass = EntryFrame(mainwindow, name='baseclass',
    #                        model=mainwindow.call_model)
    # baseclass.pack(side=LEFT)
    # newarray = ArrayBox(mainwindow, array=dummy_array, coord=(0, 1),
    #                     name='V42', model=mainwindow.call_model)
    # newarray.pack(side=LEFT)
    # newspinbox = ArraySpinBox(mainwindow, array=dummy_array, coord=(0, 2),
    #                           name='V99', model=mainwindow.call_model)
    # newspinbox.pack(side=LEFT)

    # Add space to right to debug spinbox arrows
    # Label(mainwindow, text='spacer', bg='white', bd=0).pack(side=LEFT)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

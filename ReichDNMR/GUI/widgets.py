"""Custom widgets composed from standard tkinter widgets"""
from tkinter import *


class EntryFrame(Frame):
    """
    A tkinter Frame that holds a labeled entry widget with added behavior.
    EntryFrame will call the function (provided as 'model' in the arguments)
    when a change in the entry's value is committed.

    EntryFrame is intended as a new base class that will be inherited from.
    For example, the initialize() method needs to be overwritten to change
    the default initial entry of 0.00.

    Arguments (in addition to standard Frame options):
        name-- for widget label and introspection
        model-- a function that will request a calculation from the Model

    """

    def __init__(self, parent=None, name='', color='white',
                 model=None,
                 **options):
        """
        __init__ is broken into multiple method references, to allow
        subclasses to modify as needed.
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
        however
        initial values are passed into them.
        """
        self.value_var = StringVar()
        self.value = 0.0
        self.value_var.set(self.value)

    def add_label(self):
        Label(self, text=self.name, bg=self.color, bd=0).pack(side=TOP)

    def add_entry(self):
        """
        Subclasses of EntryBox that use a different entry widget (e.g. SpinBox)
        should overwrite this function.
        """
        self.entry = Entry(self, width=7,
                           validate='key')  # check for number on keypress)
        self.entry.pack(side=TOP, fill=X)
        self.entry.config(textvariable=self.value_var)

    def bind_entry(self):
        """
        EntryFrame assumes action should only be taken when a change in the
        Entry widget is "committed" by hitting Return, Tab, or clicking
        outside the widget.
        Subclasses may overwrite/extend bind_entry to tailor behavior
        """
        self.entry.bind('<Return>', lambda event: self.on_return(event))
        self.entry.bind('<Tab>', lambda event: self.on_tab(event))
        self.entry.bind('<FocusOut>', lambda event: self.refresh())

    def on_return(self, event):
        self.refresh()
        self.find_next_entry(self.entry).focus()

    def refresh(self):
        if self.entry_is_changed():
            self.save_entry()
            self.model()

    def entry_is_changed(self):
        return self.value != float(self.value_var.get())

    def find_next_entry(self, current_widget):
        """
        Looks at the next entry in tkinter's widget traversal. If it is not of
        type Entry or Spinbox, it keeps looking until it finds one.
        Subclasses can modify this behavior if other widget types are to be
        acknowledged.
        :param current_widget: the widget that needs focus changed to the
        next entry-like widget
        :return: the next entry-like widget
        """
        next_entry = current_widget.tk_focusNext()
        if next_entry.widgetName in ['entry', 'spinbox']:
            return next_entry
        else:
            return self.find_next_entry(next_entry)

    def validate_entry(self):
        """
        The base EntryFrame class assumes the entry contents should be numerical
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
        self.on_return(event)
        return 'break'  # override default tkinter tab behavior

    def save_entry(self):
        """
        Saves widget's entry as self.stored_value , filling the entry with
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
    Modifies EntryFrame to accept a numpy 2D-array, and a coordinate to a
    specific cell in the array to read to/write from.
    """
    def __init__(self, parent=None,
                 array=None, coord=(0, 0),
                 **options):
        self.array = array
        self.row, self.col = coord
        EntryFrame.__init__(self, parent,
                            # name, color,
                            **options)

    def initialize(self):
        self.value_var = StringVar()
        self.value = self.array[self.row, self.col]
        self.value_var.set(self.value)

    def save_entry(self):
        """
        Records widget's status to the array, filling the entry with
        0.00 if it was empty.
        Currently assumes, if the array is 2D, that it is meant to be
        symmetric, and auto-updates the cross-diagonal element as well.
        """
        if not self.value_var.get():  # if entry left blank,
            self.value_var.set(0.00)  # fill it with zero
        self.value = float(self.value_var.get())
        self.array[self.row, self.col] = self.value
        if self.array.shape[0] > 1:  # if more than one row, assume J matrix
            self.array[self.col, self.row] = self.value  # fill cross-diagonal
                                                    # element


class ArraySpinBox(ArrayBox):
    """
    Modifies ArraySpinBox to use a SpinBox instead of an Entry widget.

    Arguments (in addition to standard ArrayBox options):
        from_, to, increment: SpinBox arguments (minimum and maximum values,
                              and incremental change on each arrow click)
        realtime: True if data/model should be refreshed as the SpinBox arrow
                  button is held down.
    """
    def __init__(self, parent=None, from_=0.00, to=100.00, increment=1,
                 realtime=False,
                 **options):
        self.realtime = realtime
        self.spinbox_kwargs = {'from_': from_,
                               'to': to,
                               'increment': increment}
        ArrayBox.__init__(self, parent, **options)

    def add_entry(self):
        self.add_spinbox(**self.spinbox_kwargs)

    def add_spinbox(self, **kwargs):
        self.entry = Spinbox(self, width=7,
                             validate='key',  # check for number on keypress
                             # from_=-100000, to=100000, increment=1
                             **kwargs
                             )
        self.entry.pack(side=TOP, fill=X)
        self.entry.config(textvariable=self.value_var)

    def bind_entry(self):
        self.entry.bind('<Return>', lambda event: self.on_return(event))
        self.entry.bind('<Tab>', lambda event: self.on_tab(event))
        self.entry.bind('<FocusOut>', lambda event: self.refresh())
        self.entry.bind('<ButtonPress-1>', lambda event: self.on_press())
        self.entry.bind('<ButtonRelease-1>', lambda event: self.on_release())

    def on_press(self):
        if self.realtime:
            self.loop_refresh()

    def loop_refresh(self):
        self.refresh()
        self.button_held_job = self._root().after(50, self.loop_refresh)

    def on_release(self):
        if self.realtime:
            self._root().after_cancel(self.button_held_job)

        # A 1-ms delay allows the StringVar to be updated prior to the
        # entry_is_changed check. See related StackOverflow question:
        # https://stackoverflow.com/questions/46504930/
        self.after(1, self.refresh)


if __name__ == '__main__':
    import numpy as np
    dummy_array = np.array([[1, 42, 99]])
    root = Tk()
    root.title('test widgets')

    class TestFrame(Frame):
        def __init__(self, parent, **options):
            Frame.__init__(self, parent, **options)

        def call_model(self):
            for child in self.winfo_children():
                print('I have child: ', child.name)
            print('requesting calculation from the model')
            print(dummy_array)

    mainwindow = TestFrame(root)
    mainwindow.pack()

    baseclass = EntryFrame(mainwindow, name='baseclass',
                           model=mainwindow.call_model)
    baseclass.pack(side=LEFT)
    newarray = ArrayBox(mainwindow, array=dummy_array, coord=(0, 1),
                        name='V42', model=mainwindow.call_model)
    newarray.pack(side=LEFT)
    newspinbox = ArraySpinBox(mainwindow, array=dummy_array, coord=(0, 2),
                              name='V99', model=mainwindow.call_model)
    newspinbox.pack(side=LEFT)

    # Add space to right to debug spinbox arrows
    # Label(mainwindow, text='spacer', bg='white', bd=0).pack(side=LEFT)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

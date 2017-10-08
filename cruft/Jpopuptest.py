"""
A stripped-down GUI used to test dialog for entering 2nd-order simulation data.
"""
import numpy as np
from tkinter import *
from guimixin import GuiMixin
from ReichDNMR.nspin import get_reich_default


class VarFrame(Frame):
    """
    A rudimentry input box that allows a float input.
    Currently limited to input of:
    -title
    """
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        Label(self, text='text goes here').pack(side=TOP, expand=NO)


class nspin_entry(Frame):
    """
    A frame used to store the data structures sent to the nmrmath.nspinspec
    simulation.
    """
    def __init(self, parent=None, nspins=4, **options):
        Frame.__init__(self, parent, **options)
        self.freqs, self.J = get_reich_default(nspins)


class VarBox(Frame):
    """
    Eventually will emulate what the Reich entry box does, more or less.
    Idea is to fill the VarFrame with these modules.
    Current version: checks that only numbers are entered; returns contents
    in a popup.
    Looking ahead: trick may be linking their contents with the calls to
    nmrmath. Also, need to make sure floats, not ints, are returned. Can
    change the is_number routine so that if integer entered, replaced with
    float?
    Inputs:
    -text: appears above the entry box
    -default: default value in entry
    """
    def __init__(self, parent=None, name='', default=0.00,
                 color='white', **options):
        # Added 'color' variable for customization
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=0,
                       background=color, **options)
        Label(self, text=name, bg=color, bd=0).pack(side=TOP)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))
        ent.bind('<Return>', lambda event: self.on_event(event))
        ent.bind('<FocusOut>', lambda event: self.on_event(event))

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

    def on_event(self, event):
        self.to_dict()
        self.master.call_model()
        event.widget.tk_focusNext().focus()

    def to_dict(self):
        """
        On event: Records widget's status to the container's dictionary of
        values, fills the entry with 0.00 if it was empty, tells the container
        to send data to the model, and shifts focus to the next entry box (after
        Return or Tab).
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = float(self.value.get())


def rowentry():
    """
    Used to test format for a popup window for entering V/J data
    for second-order simulations.
    """
    tl = Toplevel()
    Label(tl, text='Second-Order Simulation').pack(side=TOP)
    datagrid = Frame(tl)

    # For gridlines, background set to the line color (e.g. 'black')
    datagrid.config(background='black')

    # Planning ahead: if entryboxes are not going to be named, need a way to
    # keep track of them. Plan for now is to to use lists and/or arrays to hold
    # them by position.
    # May instead make custom VarBox for Vs and Js, whose update modifies
    # list / array in parent frame
    v_entries = []
    j_entries = np.empty((4, 4), dtype=object)

    Label(datagrid, bg='gray90').grid(row=0, column=0, sticky=NSEW,
                                      padx=1, pady=1)
    for col in range(1, 5):
        Label(datagrid, text='V%d' % col, width=8, height=3,
              bg='gray90').grid(
            row=0, column=col, sticky=NSEW, padx=1, pady=1)

    for row in range(1, 5):
        vtext = "V" + str(row)
        v = VarBox(datagrid, name=vtext, color='gray90')
        v_entries.append(v)
        v.grid(row=row, column=0, sticky=NSEW, padx=1, pady=1)
        for col in range(1, 5):
            if col < row:
                j = VarBox(datagrid, name="J%d%d" % (col, row))
                j.grid(row=row, column=col, sticky=NSEW, padx=1, pady=1)
                j_entries[row - 1, col - 1] = j
            else:
                Label(datagrid, bg='grey').grid(
                    row=row, column=col, sticky=NSEW, padx=1, pady=1)

    datagrid.pack()


def colentry2():
    tl = Toplevel()
    Label(tl, text='Second-Order Simulation').pack(side=TOP)
    datagrid = Frame(tl)
    datagrid.config(background='black')
    v_entries = []
    Label(datagrid, bg='gray').grid(row=0, column=0, sticky=NSEW,
                                    padx=1, pady=1)
    for col in range(1, 5):
        vtext = 'V' + str(col)
        v = VarBox(datagrid, name=vtext, color='gray90')
        v_entries.append(v)
        v.grid(row=0, column=col, sticky=NSEW, padx=1, pady=1)

    for row in range(1, 4):
        Label(datagrid, text='V%d' % (row + 1), width=8, height=3,
              bg='gray90').grid(row=row, column=0, sticky=NSEW, padx=1, pady=1)
        for col in range(1, 5):
            if col <= row:
                VarBox(datagrid, name="J%d%d" % (col, row + 1)).grid(
                    row=row, column=col, sticky=NSEW, padx=1, pady=1)
            else:
                Label(datagrid, bg='grey').grid(
                    row=row, column=col, sticky=NSEW, padx=1, pady=1)
    datagrid.pack()


def colentry():
    tl = Toplevel()
    Label(tl, text='Second-Order Simulation').pack(side=TOP)
    datagrid = Frame(tl)
    v_entries = []
    Label(datagrid, bg='grey').grid(row=0, column=0,
                                    sticky=NSEW)
    for row in range(1, 5):
        Label(datagrid, text='V%d' % row, width=7).grid(row=row, column=0,
                                                        sticky=NSEW)
    for col in range(1, 5):
        vtext = "V" + str(col)
        v = VarBox(datagrid, name=vtext)
        v_entries.append(v)
        v.grid(row=0, column=col, sticky=NSEW)
        for row in range(1, 5):
            if row < col:
                VarBox(datagrid, name="J%d%d" % (row, col)).grid(
                    row=row, column=col)
            else:
                Label(datagrid, bg='grey').grid(row=row, column=col,
                                                sticky=NSEW)

    datagrid.pack()


root = Tk()

# Adding Sidebar skeleton
sideBar = Frame(root, bg='orange', relief=RIDGE, borderwidth=3)
sideBar.pack(side=LEFT, expand=YES, fill=Y)
Label(sideBar, text='Sidebar frame').pack(
    anchor=CENTER, expand=YES, fill=NONE)

# Add the top frame for variables
VariablesBar = VarFrame(root, relief=RIDGE, borderwidth=3, bg='green')
VariablesBar.pack(side=TOP, expand=YES, fill=X)

get_popup = Button(root, text='column', command=lambda: colentry2())
get_popup.pack(side=BOTTOM)
get_popup2 = Button(root, text='row', command=lambda: rowentry())
get_popup2.pack(side=BOTTOM)


Canvas(root, width=800, height=600, bg='beige').pack()

TestBox = VarBox(VariablesBar, name='Test', default=0.00)
TestBox.pack(side=LEFT)

root.mainloop()

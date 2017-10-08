"""An attempt to answer my SO MVC question"""

from tkinter import *


# Actual model would be imported. "Dummy" model for testing below.
def dummy_model(dic):
    """
    A "dummy" model for testing the ability for a toolbar to ping the model.
    Argument:
    -dic: a dictionary whose values are numbers.
    Result:
    -prints the sum of dic's values.
    """
    total = 0
    for value in dic.values():
        total += value
    print('The total of the entries is: ', total)


class ToolBar(Frame):
    """
    A frame object that contains entry widgets, a dictionary of
    their current contents, and a function to call the appropriate model.
    """
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.vars = {}

    def call_model(self):
        print('Sending to dummy_model: ', self.vars)
        dummy_model(self.vars)


class VarBox(Frame):
    """
    A customized Frame containing a numerical entry box
    Arguments:
    -name: Name of the variable; appears above the entry box
    -default: default value in entry
    """
    def __init__(self, parent=None, name='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))
        ent.bind('<Return>',   lambda event: self.to_dict(event))
        ent.bind('<FocusOut>', lambda event: self.to_dict(event))

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

    def to_dict(self, event):
        """
        On event: Records widget's status to the container's dictionary of
        values, fills the entry with 0.00 if it was empty, tells the container
        to send data to the model, and shifts focus to the next entry box (after
        Return or Tab).
        """
        if not self.value.get():    # if entry left blank,
            self.value.set(0.00)    # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = float(self.value.get())
        self.master.call_model()
        event.widget.tk_focusNext().focus()


root = Tk()  # create app window
BarParentFrame = ToolBar(root)  # holds individual toolbar frames
BarParentFrame.pack(side=TOP)
BarParentFrame.widgetName = 'BarParentFrame'

# Pad out rest of window for visual effect
SpaceFiller = Canvas(root, width=800, height=600, bg='beige')
SpaceFiller.pack(expand=YES, fill=BOTH)

Label(BarParentFrame, text='placeholder').pack(expand=NO, fill=X)
A = VarBox(BarParentFrame, name='A', default=5.00)
A.pack(side=LEFT)
B = VarBox(BarParentFrame, name='B', default=3.00)
B.pack(side=LEFT)

root.mainloop()

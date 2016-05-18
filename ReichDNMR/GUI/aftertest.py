"""
A stripped-down GUI used to test the "increase value" button of EntryBox
"""

from tkinter import *


class EntryBox(Frame):

    def __init__(self, parent=None, default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text='Test EntryBox').pack(side=TOP)

        # Entries will be limited to numerical
        ent = Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

        up = Button(self, text=u"\u21e7", command=lambda: None)  # up arrow
        up.pack(side=TOP)
        up.bind('<Button-1>', lambda event: self.increase())
        up.bind('<ButtonRelease-1>', lambda event: self.stop_action())
        self.mouse1 = False  # flag to indicate if Button 1 currently pressed

        increment = Entry(self, width=4, validate='key')
        increment.pack(side=TOP)
        self.inc = StringVar()
        increment.config(textvariable=self.inc)
        self.inc.set("1")
        increment['validatecommand'] = (self.register(self.is_number), '%P')
        increment['invalidcommand'] = 'bell'

    def is_number(self, entry):
        """
        tests to see if Entry is acceptable (either empty, or able to be
        converted to a float.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def stop_action(self):
        self.mouse1 = False
        print('Button released')

    def increase(self):
        increment = float(self.inc.get())
        self.mouse1 = True
        self.change_value(increment)

    def change_value(self, increment):
        if not self.mouse1:
            print('change_value detected the button was released')
        else:
            print('increasing value')
            current_value = float(self.value.get())
            new_value = current_value + increment
            self.value.set(str(new_value))
            print('calling model')
            print(new_value + 0.1)  # a placeholder function for demo purposes
            print('waiting 250')

            # The fix is that: the function call can't take arguments.
            # The result of the function call gets passed to .after method, and
            # it is that result that is executed. e.g. if the function
            # returns None, that's what .after executes.
            # SO: need to use a lambda, which returns a function to be used
            # by .after
            self.after(250, lambda: self.change_value(increment))
            #root.after(250, self.change_value(increment))


root = Tk()

# Add the top frame for variables
TopBar = Frame(root, relief=RIDGE, borderwidth=3, bg='green')
TopBar.pack(side=TOP, expand=NO, fill=X)

# Pad the rest of the window out with a canvas
Canvas(root, width=800, height=600, bg='beige').pack()

TestBox = EntryBox(TopBar, default=0.00)
TestBox.pack(side=LEFT, expand=NO, fill=NONE)

root.mainloop()

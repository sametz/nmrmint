"""
A stripped-down GUI used to test variable bar config
This version is to see if a lot of the "self"s can be eliminated
"""


from tkinter import *
from guimixin import GuiMixin


class VarFrame(Frame):
    """
    A frame for holding the variable boxes
    """
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        Label(self, text='text goes here').pack(side=TOP, expand=NO)


class VarBox(GuiMixin, Frame):
    """
    Eventually will emulate what the Reich entry box does, more or less.
    Idea is to fill the VarFrame with these modules.
    Looking ahead: trick may be linking their contents with the calls to
    nmrmath.
    Inputs:
    -text: appears above the entry box
    -default: default value in entry
    """
    def __init__(self, parent=None, text='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=text).pack(side=TOP)
        ent = Entry(self, validate='key')
        ent.insert(0, default)
        ent.pack(side=TOP, fill=X)
        value = ent.get()
        ent.bind('<Return>', lambda event: self.result(value))
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        ent['invalidcommand'] = 'bell'


    def result(self, value):
        self.infobox('Return', value)

    @staticmethod
    def is_number(entry):
        if not entry:
            return True
        try:
            float(entry)
            return True
        except ValueError:
            return False


root = Tk()

# Adding Sidebar skeleton
sideBar = Frame(root, bg='orange', relief=RIDGE, borderwidth=3)
sideBar.pack(side=LEFT, expand=YES, fill=Y)
Label(sideBar, text='Sidebar frame').pack(
    anchor=CENTER, expand=YES, fill=NONE)

# Add the top frame for variables
VariablesBar = VarFrame(root, relief=RIDGE, borderwidth=3, bg='green')
VariablesBar.pack(side=TOP, expand=YES, fill=X)

Canvas(root, width=800, height=600, bg='beige').pack()

TestBox = VarBox(VariablesBar, text='Test', default=0.00)
TestBox.pack(side=LEFT)

root.mainloop()

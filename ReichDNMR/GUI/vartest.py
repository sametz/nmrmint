"""
A stripped-down GUI used to test variable bar config
"""


from tkinter import *
from guimixin import GuiMixin


class VarFrame(Frame):
    """
    A rudimentry input box that allows a float input.
    Currently limited to input of:
    -title
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
    """
    def __init__(self, parent=None, text='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=text).pack(side=TOP)
        self.ent = Entry(self, validate='key')
        self.ent.insert(0, default)
        self.ent.pack(side=TOP, fill=X)
        self.ent.bind('<Return>', lambda event: self.result())
        self.ent['validatecommand'] = (self.register(self.is_number), '%P')
        self.ent['invalidcommand'] = 'bell'

    def result(self):
        value = self.ent.get()
        self.infobox('Return', value)

    def is_number(self, entry):
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

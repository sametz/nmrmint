"""
A stripped-down GUI used to test menu-swapping.
"""


from tkinter import *
from guimixin import GuiMixin


class RadioFrame(Frame):
    """
    Creates and packs radio button frames into parent.
    arguments:
    -buttons: a tuple of (text, function) tuples
    -title: an optional title to put above the button list
    """
    def __init__(self, parent=None, buttons=(), title='', **options):
        Frame.__init__(self, parent, **options)
        # self.pack(side=TOP, expand=NO, fill=X)
        Label(self, text=title).pack(side=TOP)
        self.var = StringVar()
        for button in buttons:
            Radiobutton(self, text=button[0], command=button[1],
                        variable=self.var,
                        value=button[0]).pack(anchor=NW)
        self.var.set(buttons[0][0])


class CalcTypeFrames(GuiMixin, Frame):
    """
    Creates a frame that will store and manage the individual button menus
    for the different calc types, which will be selected by
    CalcTypeFrame.
    """
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack(side=TOP, anchor=N, expand=YES, fill=X)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        multiplet_buttons = (('AB', lambda: None),
                             ('AB2', lambda: None))
        self.MultipletButtons = RadioFrame(self,
                                      buttons=multiplet_buttons,
                                      title='Multiplet')
        self.MultipletButtons.grid(row=0, column=0, sticky=N)

        abc_buttons = (('AB', lambda: none),
                       ('3-Spin', lambda: None),
                       ('4-Spin', lambda: None),
                       ('5-Spin', lambda: None),
                       ('6-Spin', lambda: None),
                       ('7-Spin', lambda: None),
                       ('8-Spin', lambda: None))
        self.ABC_Buttons = RadioFrame(self,
                                 buttons=abc_buttons,
                                 title='2-7 Spins')
        self.ABC_Buttons.grid(row=0, column=0, sticky=N)

        self.framedic = {'multiplet': self.MultipletButtons, 'abc':
            self.ABC_Buttons}
        self.sf2('multiplet')
    def select_frame(self, frame):
        #self.infobox(frame, 'raising ' + frame)
        self.framedic[frame].tkraise()

    def sf2(self, frame):
        for key in self.framedic:
            #self.infobox(key, 'considering ' + key)
            if key == frame:
                #self.infobox(key, 'gridding ' + key)
                self.framedic[key].grid()
            else:
                #self.infobox(key, 'ungridding ' + key)
                self.framedic[key].grid_remove()

root = Tk()
sideBar = Frame(root, bg='orange')
sideBar.pack(side=LEFT, expand=NO, fill=Y)
Canvas(root, width=800, height=600, bg='beige').pack()
ctf = CalcTypeFrames(sideBar)
ctf.pack()
buttonbar = Frame(sideBar).pack(side=BOTTOM)
Button(buttonbar, text='multiplet',
       command=lambda: ctf.select_frame('multiplet')).pack()
Button(buttonbar, text='abc',
       command=lambda: ctf.select_frame('abc')).pack()
Button(buttonbar, text='multiplet2',
       command=lambda: ctf.sf2('multiplet')).pack()
Button(buttonbar, text='abc2',
       command=lambda: ctf.sf2('abc')).pack()
root.mainloop()

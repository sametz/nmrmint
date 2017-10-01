"""Custom tkinter frames with added features."""
from tkinter import *


class RadioFrame(Frame):
    """
    A tkinter Frame containing a radio button menu and optional title.
    """

    def __init__(self, parent=None, buttons=(), title='', **options):
        """arguments:
        -buttons: a tuple of (text, function) tuples
        -title: an optional title to put above the button list"""
        Frame.__init__(self, parent, **options)
        Label(self, text=title).pack(side=TOP)
        self.var = StringVar()
        for button in buttons:
            Radiobutton(self, text=button[0], command=button[1],
                        variable=self.var,
                        value=button[0]).pack(anchor=NW)
        self.var.set(buttons[0][0])  # turns the top button on


if __name__ == '__main__':

    def button_callback(response):
        print(response)

    buttons = (
        ('A', lambda: button_callback('You picked A!')),
        ('B', lambda: button_callback('You picked B!')),
        ('C', lambda: button_callback('You picked C!'))
    )

    root = Tk()
    root.title('test Frames')
    RadioFrame(root, buttons, 'test buttons').pack()

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

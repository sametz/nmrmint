"""Custom tkinter frames with added features.

Provides the following class:
* RadioFrame: extends tkinter Frame by adding a radiobutton list and title label
"""

from tkinter import *


class RadioFrame(Frame):
    """Extend a tkinter Frame by adding a radio button menu and optional
    title label.

    Assumes that the top button should be turned on by default.
    """

    def __init__(self, parent=None, buttons=(), title='', **options):
        """Keyword arguments:
        :param parent: parent tkinter object
        :param buttons: a tuple of ('text', callback) tuples (one for each
        button)
        :param title: optional text for a title label
        :param options: standard Frame kwargs
        """
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

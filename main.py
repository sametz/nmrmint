"""The main routine for the nmrmint app, to be run from the command line."""


import tkinter as tk

from nmrmint.controller.controller import Controller

root = tk.Tk()
root.title('nmrmint')
app = Controller(root)

# workaround fix for Tk problems and mac mouse/trackpad:
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass

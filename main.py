"""The main routine for the UW-DNMR app, to be run from the command line."""


import tkinter as tk

from uw_dnmr.controller.controller import Controller

root = tk.Tk()
root.title('uw_dnmr')
app = Controller(root)

# workaround fix for Tk problems and mac mouse/trackpad:
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass

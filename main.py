"""The main routine for the ReichDNMR app, to be run from the command line."""


import tkinter as tk

from ReichDNMR.controller.controller import Controller

root = tk.Tk()
root.title('ReichDNMR')
app = Controller(root)

# workaround fix for Tk problems and mac mouse/trackpad:
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass

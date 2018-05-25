"""The main routine for the nmrmint app, to be run from the command line."""


import tkinter as tk

from nmrmint.controller.controller import Controller

root = tk.Tk()

width, height = root.winfo_screenwidth(), root.winfo_screenheight()
padding_x = int(width * 0.1)
padding_y = int(height * 0.1)
xoffset, yoffset = padding_x / 2, padding_y / 2
geometry = "%dx%d%+d%+d" % (width-padding_x, height-padding_y, xoffset, yoffset)
root.geometry(geometry)

root.title('nmrmint')
app = Controller(root)

# workaround fix for Tk problems and mac mouse/trackpad:
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass

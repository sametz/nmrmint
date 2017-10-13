import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import *
from numpy import arange, pi, sin, cos


f = Figure(figsize=(5, 4), dpi=100)
a = f.add_subplot(111)


def plotcos():
    c = cos(2 * pi * t)
    a.clear()
    a.plot(t, c)


root = Tk()

t = arange(0.0, 3.0, 0.01)
s = sin(2 * pi * t)
a.plot(t, s)

canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)

clear = Button(root, text='clear', command=lambda: a.clear())
clear.pack(side=BOTTOM)
cosbutton = Button(root, text='cos', command=lambda: plotcos())
cosbutton.pack(side=BOTTOM)

root.mainloop()

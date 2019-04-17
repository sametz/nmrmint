"""matplotlib backends for plotting to Tkinter, plus creating EPS and PDF
exports.

Provides the following class:
* MPLplot: extends FigureCanvasTkAgg with a Figure and an API of plotting
commands.

Provides the following functions:
* save_as_eps: plots and saves a figure in EPS format.
* save_as_pdf: plots and saves a figure in PDF format.
"""

from tkinter import *
from tkinter.filedialog import asksaveasfilename

import matplotlib
matplotlib.use("TkAgg")  # must be invoked before the imports below

# Some MPL backends were deprecated. See:
# https://stackoverflow.com/questions/50330320/what-to-use-instead-of-navigationtoolbar2tkagg

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,

# So the following was changed to:
                                               NavigationToolbar2Tk)
from matplotlib.backends.backend_pdf import FigureCanvasPdf
from matplotlib.backends.backend_ps import FigureCanvasPS
from matplotlib.figure import Figure


class MPLplot(FigureCanvasTkAgg):
    """Extends on FigureCanvasTkAgg by including a
    matplotlib Figure object, plus an API for plotting.

    Attributes:
        x_min, x_max: minimum and maximum values for the x axis.

    Methods:
        plot_current: plot data to the top axis (i.e. the spectrum affected
        by the current toolbar inputs)
        plot_total: plot data to the bottom axis (i.e. the summation spectrum)
        set_total_plot_window: set the width of the total plot
        clear_current: clear the current plot
        clear_total: clear the total plot
    """

    def __init__(self, master=None, **options):
        """Extend FigureCanvasTkAgg with a Matplotlib Figure object, then add
        and pack itself plus a toolbar into the master.

        :param master: parent tkinter object
        """
        self._figure = Figure(figsize=(7, 5.6), dpi=100)
        FigureCanvasTkAgg.__init__(self, self._figure, master, **options)
        self._current_plot = self._figure.add_subplot(211)
        # self.current_plot.invert_xaxis()
        self._total_plot = self._figure.add_subplot(212)
        # self.total_plot.invert_xaxis()
        self.x_min = -1  # ppm
        self.x_max = 12  # ppm
        self.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self._toolbar = NavigationToolbar2Tk(self, master)
        self._toolbar.update()

    def plot_current(self, x, y):
        """Plot x, y data to the current_plot axis.

        Requires self._set_current_window() to set an appropriate zoom level.

        :param x: (numpy ndarray)
        :param y: (numpy ndarray)
        """
        self._current_plot.invert_xaxis()  # for NMR style high-->low
        self._set_current_window(x, y)
        self._current_plot.plot(x, y, linewidth=1)
        self.draw_idle()

    def _set_current_window(self, x, y):
        """Find the x limits of the current signal (> 1% intensity) and set
        the window to be 0.2 ppm on either side.
        """
        left = False
        right = False

        for i, intensity in enumerate(y):
            if intensity > 0.01:
                left = i
                break

        for j, intensity in enumerate(reversed(y)):
            if intensity > 0.01:
                right = j
                break

        x_min = x[left] - 0.2
        x_max = x[-right] + 0.2
        self._current_plot.set_xlim(x_max, x_min)  # should flip x axis
        self.draw_idle()

    def plot_total(self, x, y):
        """Plot x, y data to the total_plot axis.

        :param x: (numpy ndarray)
        :param y: (numpy ndarray)
        """
        self._total_plot.plot(x, y, linewidth=1)
        self.set_total_plot_window()

    def set_total_plot_window(self, *x_limits):
        """Set the width of the total spectrum.

        :param x_limits: (float, float) of (minimum chemical shift,
        maximum chemical shift)
        """
        if x_limits:
            self.x_min, self.x_max = x_limits
        self._total_plot.set_xlim(self.x_max, self.x_min)  # should flip x axis
        self.draw_idle()

    def clear_current(self):
        """Clear the current spectrum plot"""
        self._current_plot.clear()
        self._figure.canvas.draw_idle()

    def clear_total(self):
        """Clear the summation spectrum plot."""
        self._total_plot.clear()
        self._figure.canvas.draw_idle()


def _create_figure(x, y, xlim, figsize):
    figure = Figure(figsize=figsize)
    axes = figure.add_subplot(111)
    axes.plot(x, y, linewidth=0.3)
    axes.set_xlim(*xlim)
    return figure


def save_as_eps(x, y, xlim, figsize, orientation):
    """Create and save an EPS file from plot data.

    :param x: (numpy ndarray)
    :param y: (numpy ndarray)
    :param xlim: (float, float) a tuple of
    (max chemical shift, min chemical shift)
    :param figsize: (float, float) a tuple of (plot width, plot height) in
    inches.
    :param orientation: 'landscape' or 'portrait'"""
    figure = _create_figure(x, y, xlim, figsize)
    backend = FigureCanvasPS(figure)
    filename = asksaveasfilename()
    if filename:
        if filename[-4:] != '.eps':
            filename += '.eps'
        backend.print_eps(filename, orientation=orientation)


def save_as_pdf(x, y, xlim, figsize):
    """Create and save a PDF file from plot data.

    Currently, it doesn't seem possible to select landscape vs. portrait for
    PDF. Try _save_as_eps if that feature is important.

    :param x: (numpy ndarray)
    :param y: (numpy ndarray)
    :param xlim: (float, float) a tuple of
    (max chemical shift, min chemical shift)
    :param figsize: (float, float) a tuple of (plot width, plot height) in
    inches.
    """
    figure = _create_figure(x, y, xlim, figsize)
    backend = FigureCanvasPdf(figure)
    filename = asksaveasfilename()
    if filename:
        if filename[-4:] != '.pdf':
            filename += '.pdf'
        backend.print_pdf(filename)

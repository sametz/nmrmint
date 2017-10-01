"""Custom tkinter frames that hold multiple widgets"""
import numpy as np
from ReichDNMR.initialize import getWINDNMRdefault
from tkinter import *
from ReichDNMR.GUI.widgets import ArrayBox, ArraySpinBox


class SecondOrderBar(Frame):
    """
    A Frame that holds n frequency entry boxes, an entry box for peak width
    (default 0.5 Hz), a 1-D array for frequencies, a 2-D array for coupling
    constants, and a button to pop up a window for entering J values as well
    as frequencies.
    Arguments:
        controller: controller object with a
        n: number of spins
    Dependencies:
        numpy
        ReichDNMR.initialize.getWINDNMRdefault for WINDNMR default values
        ReichDNMR.GUI.widgets for custom ArrayBox and ArraySpinBox widgets

    """

    def __init__(self, parent=None, controller=None, n=4, **options):
        Frame.__init__(self, parent, **options)
        self.controller = controller

        # Store a list of entry widgets for all frequencies
        # (used by vj_popup)
        self.v_widgets = np.zeros(n, dtype=object)
        self.v, self.j = getWINDNMRdefault(n)
        self.w_array = np.array([[0.5]])

        self.add_frequency_widgets(n)
        self.add_peakwidth_widget()
        self.add_J_button(n)

    def add_frequency_widgets(self, n):
        for freq in range(n):
            vbox = ArrayBox(self, array=self.v, coord=(0, freq),
                            name='V' + str(freq + 1),
                            model=self.request_plot)
            self.v_widgets[freq] = vbox
            vbox.pack(side=LEFT)

    def add_peakwidth_widget(self):
        wbox = ArrayBox(self, array=self.w_array, coord=(0, 0), name="W",
                        model=self.request_plot)
        wbox.pack(side=LEFT)

    def add_J_button(self, n):
        vj_button = Button(self, text="Enter Js",
                           command=lambda: self.vj_popup(n))
        vj_button.pack(side=LEFT, expand=N, fill=NONE)

    def vj_popup(self, n):
        """
        Creates a new Toplevel window that provides entries for both
        frequencies and J couplings, and updates self.v and self.j when
        entries change.
        :param n: number of spins
        """
        tl = Toplevel()
        Label(tl, text='Second-Order Simulation').pack(side=TOP)
        # datagrid = ArrayFrame(tl, self.request_plot, self.v_widgets)
        datagrid = Frame(tl)

        # For gridlines, background set to the line color (e.g. 'black')
        datagrid.config(background='black')

        Label(datagrid, bg='gray90').grid(row=0, column=0, sticky=NSEW,
                                          padx=1, pady=1)
        for col in range(1, n + 1):
            Label(datagrid, text='V%d' % col, width=8, height=3,
                  bg='gray90').grid(
                row=0, column=col, sticky=NSEW, padx=1, pady=1)

        for row in range(1, n + 1):
            vtext = "V" + str(row)
            v = ArrayBox(datagrid, array=self.v,
                         coord=(0, row - 1),  # V1 stored in v[0, 0], etc.
                         name=vtext, color='gray90',
                         model=self.request_plot)
            v.grid(row=row, column=0, sticky=NSEW, padx=1, pady=1)
            for col in range(1, n + 1):
                if col < row:
                    j = ArrayBox(datagrid, array=self.j,
                                 # J12 stored in j[0, 1] (and j[1, 0]) etc
                                 coord=(col - 1, row - 1),
                                 name="J%d%d" % (col, row),
                                 model=self.request_plot)
                    j.grid(row=row, column=col, sticky=NSEW, padx=1, pady=1)
                else:
                    Label(datagrid, bg='grey').grid(
                        row=row, column=col, sticky=NSEW, padx=1, pady=1)

        datagrid.pack()

    def request_plot(self):
        # self.controller.update_view_plot(self.v[0, :], self.j,
        #                                  self.w_array[0, 0])
        kwargs = {'v': self.v[0, :],
                  'j': self.j,
                  'w': self.w_array[0, 0]}

        self.controller.update_with_dict(**kwargs)


class SecondOrderSpinBar(SecondOrderBar):
    """A subclass of SecondOrderBar that uses ArraySpinBox widgets for the
    toolbar.
    """
    def __init__(self, parent=None,
                 from_=-10000, to=10000.00, increment=1, realtime=False,
                 **options):
        self.spinbox_kwargs = {'from_': from_,
                               'to': to,
                               'increment': increment,
                               'realtime': realtime}
        SecondOrderBar.__init__(self, parent, **options)

    def add_frequency_widgets(self, n):
        for freq in range(n):
            vbox = ArraySpinBox(self, array=self.v, coord=(0, freq),
                                name='V' + str(freq + 1),
                                model=self.request_plot,
                                **self.spinbox_kwargs)
            self.v_widgets[freq] = vbox
            vbox.pack(side=LEFT)

    def add_peakwidth_widget(self):
        """
        Currently hard-wired to vary from 0.01 to 100 Hz, with an increment
        of 0.1 Hz.
        """
        wbox = ArraySpinBox(self, array=self.w_array, coord=(0, 0),
                            name="W",
                            model=self.request_plot,
                            from_=0.01, to=100, increment=0.1,
                            realtime=self.spinbox_kwargs['realtime'])
        wbox.pack(side=LEFT)


if __name__ == '__main__':
    dummy_array_1 = np.array([[1, 2, 3]])
    dummy_array_2 = np.array([[11, 12, 13]])


    class DummyController:
        @staticmethod
        def update_with_dict(**kwargs):
            print(kwargs)


    dummy_controller = DummyController()

    root = Tk()
    root.title('test toolbars')

    toolbar_1 = SecondOrderBar(root, controller=dummy_controller)
    toolbar_1.pack(side=TOP)
    toolbar_2 = SecondOrderSpinBar(root, controller=dummy_controller,
                                   realtime=False,
                                   from_=-10000, to=10000, increment=1
                                   )
    toolbar_2.pack(side=TOP)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

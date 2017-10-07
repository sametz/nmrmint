"""Custom tkinter frames that hold multiple widgets"""
import numpy as np
from ReichDNMR.initialize import getWINDNMRdefault
from tkinter import *
from ReichDNMR.GUI.widgets import ArrayBox, ArraySpinBox

# the following are only temporary, to get old functionality back
from ReichDNMR.model.nmrmath import AB, AB2, ABX, ABX3, AAXX, first_order, AABB
from ReichDNMR.model.nmrmath import nspinspec
from ReichDNMR.model.nmrplot import tkplot

up_arrow = u"\u21e7"
down_arrow = u"\u21e9"
left_arrow = u"\u21e6"
right_arrow = u"\u21e8"


class ToolBar(Frame):
    """
    A frame object that contains entry widgets, a dictionary of
    their current contents, and a function to call the appropriate model.
    """
    # f = Figure(figsize=(5, 4), dpi=100)
    # a = f.add_subplot(111)

    # canvas = FigureCanvasTkAgg(f, master=root)
    # canvas.show()
    # canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    # toolbar = NavigationToolbar2TkAgg(canvas, root)
    # toolbar.update()
    # canvas._tkcanvas.pack(anchor=SE, expand=YES, fill=BOTH)

    def __init__(self, parent=None, controller=None, **options):
        Frame.__init__(self, parent, **options)
        self.controller = controller
        self.model = 'model'  # must be overwritten by subclasses
        self.vars = {}

    def request_plot(self):
        self.controller.new_update(self.model, **self.vars)


class AB_Bar(ToolBar):
    """
    Creates a bar of AB quartet inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AB
    """
    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        self.model = 'AB'
        Jab    = VarBox(self, name='Jab',    default=12.00)
        Vab    = VarBox(self, name='Vab',    default=15.00)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jab.pack(side=LEFT)
        Vab.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    # def call_model(self):

        # _Jab = self.vars['Jab']
        # _Vab = self.vars['Vab']
        # _Vcentr = self.vars['Vcentr']
        # spectrum = AB(_Jab, _Vab, _Vcentr, Wa=0.5, RightHz=0, WdthHz=300)
        # x, y = tkplot(spectrum)
        # canvas.clear()
        # canvas.plot(x, y)


class AB2_Bar(ToolBar):
    """
    Creates a bar of AB2 spin system inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AB2
    """
    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        self.model = 'AB2'
        Jab = VarBox(self, name='J',    default=12.00)
        dV = VarBox(self, name='dV',    default=15.00)
        Vab = VarBox(self, name='Vab', default=150)
        Jab.pack(side=LEFT)
        dV.pack(side=LEFT)
        Vab.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    # def call_model(self):
    #     _Jab = self.vars['Jab']
    #     _Vab = self.vars['Vab']
    #     _Vcentr = self.vars['Vcentr']
    #     spectrum = AB2(_Jab, _Vab, _Vcentr, Wa=0.5, RightHz=0, WdthHz=300)
    #     x, y = tkplot(spectrum)
    #     canvas.clear()
    #     canvas.plot(x, y)


class ABX_Bar(ToolBar):
    """
    Creates a bar of ABX spin system inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.ABX
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        self.model = 'ABX'
        Jab = VarBox(self, name='Jab', default=12.00)
        Jax = VarBox(self, name='Jax', default=2.00)
        Jbx = VarBox(self, name='Jbx', default=8.00)
        Vab = VarBox(self, name='Vab', default=15.00)
        Vcentr = VarBox(self, name='Vcentr', default=118)
        Jab.pack(side=LEFT)
        Jax.pack(side=LEFT)
        Jbx.pack(side=LEFT)
        Vab.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    # def call_model(self):
    #     _Jab = self.vars['Jab']
    #     _Jax = self.vars['Jax']
    #     _Jbx = self.vars['Jbx']
    #     _Vab = self.vars['Vab']
    #     _Vcentr = self.vars['Vcentr']
    #     spectrum = ABX(_Jab, _Jax, _Jbx, _Vab, _Vcentr, Wa=0.5, RightHz=0,
    #                    WdthHz=300)
    #     x, y = tkplot(spectrum)
    #     canvas.clear()
    #     canvas.plot(x, y)


class ABX3_Bar(ToolBar):
    """
    Creates a bar of ABX3 spin system inputs. Currently assumes "canvas" is the
    MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.ABX3
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        self.model = 'ABX3'
        Jab = VarBox(self, name='Jab', default=-12.00)
        Jax = VarBox(self, name='Jax', default=7.00)
        Jbx = VarBox(self, name='Jbx', default=7.00)
        Vab = VarBox(self, name='Vab', default=14.00)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jab.pack(side=LEFT)
        Jax.pack(side=LEFT)
        Jbx.pack(side=LEFT)
        Vab.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    # def call_model(self):
    #     _Jab = self.vars['Jab']
    #     _Jax = self.vars['Jax']
    #     _Jbx = self.vars['Jbx']
    #     _Vab = self.vars['Vab']
    #     _Vcentr = self.vars['Vcentr']
    #     spectrum = ABX3(_Jab, _Jax, _Jbx, _Vab, _Vcentr, Wa=0.5, RightHz=0,
    #                     WdthHz=300)
    #     x, y = tkplot(spectrum)
    #     canvas.clear()
    #     canvas.plot(x, y)


class AAXX_Bar(ToolBar):
    """
    Creates a bar of AA'XX' spin system inputs. Currently assumes "canvas" is
    the MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AAXX
    """

    def __init__(self, parent=None, **options):
        # WINDNMR uses all caps JAA', JXX', etc. However, the model function
        # uses Jab, Jax etc. Also, with conversion to using kwargs instead of
        #  args, can't have dict keys with apostrophes. So, VarBox names
        # coverted to args in nmrmath.AAXX for now. Future: probably want to
        # refactor so that toolbar widgets can have separate labels and dict
        # keys.
        ToolBar.__init__(self, parent, **options)
        self.model = 'AAXX'
        Jaa = VarBox(self, name="Jaa", default=15.00)
        Jxx = VarBox(self, name="Jxx", default=-10.00)
        Jax = VarBox(self, name="Jax", default=40.00)
        Jax_prime = VarBox(self, name="Jax_prime", default=6.00)
        Vcentr = VarBox(self, name="Vcentr", default=150)
        Jaa.pack(side=LEFT)
        Jxx.pack(side=LEFT)
        Jax.pack(side=LEFT)
        Jax_prime.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    # def call_model(self):
    #     _Jaa = self.vars["JAA'"]
    #     _Jxx = self.vars["JXX'"]
    #     _Jax = self.vars["JAX"]
    #     _Jax_prime = self.vars["JAX'"]
    #     _Vcentr = self.vars["Vcentr"]
    #     spectrum = AAXX(_Jaa, _Jxx, _Jax, _Jax_prime, _Vcentr,
    #                     Wa=0.5, RightHz=0, WdthHz=300)
    #     x, y = tkplot(spectrum)
    #     canvas.clear()
    #     canvas.plot(x, y)


class AABB_Bar(ToolBar):
    # see comments to AAXX_bar for problem. Here, will try to customize
    # request_plot to work around the label conflict
    """
    Creates a bar of AA'BB' spin system inputs. Currently assumes "canvas" is
    the MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.AABB
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        self.model = 'AABB'
        Vab = VarBox(self, name='VAB', default=40.00)
        Jaa = VarBox(self, name="JAA'", default=15.00)
        Jbb = VarBox(self, name="JBB'", default=-10.00)
        Jab = VarBox(self, name="JAB", default=40.00)
        Jab_prime = VarBox(self, name="JAB'", default=6.00)
        Vcentr = VarBox(self, name="Vcentr", default=150)
        Vab.pack(side=LEFT)
        Jaa.pack(side=LEFT)
        Jbb.pack(side=LEFT)
        Jab.pack(side=LEFT)
        Jab_prime.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def request_plot(self):
        kwargs = self.make_kwargs()
        self.controller.new_update(self.model, **kwargs)

    def make_kwargs(self):
        _Vab = self.vars['VAB']
        _Jaa = self.vars["JAA'"]
        _Jbb = self.vars["JBB'"]
        _Jab = self.vars["JAB"]
        _Jab_prime = self.vars["JAB'"]
        _Vcentr = self.vars["Vcentr"]

        data = {'Vab': _Vab,
                'Jaa': _Jaa,
                'Jbb': _Jbb,
                'Jab': _Jab,
                'Jab_prime': _Jab_prime,
                'Vcentr': _Vcentr}
        return data


class FirstOrder_Bar(ToolBar):
    """
    Creates a bar of first-order coupling inputs. Currently assumes "canvas"
    is the MPLGraph instance.
    Dependencies: nmrplot.tkplot, nmrmath.first_order
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        self.model = 'first_order'
        Jax = VarBox(self, name='JAX', default=7.00)
        a = IntBox(self, name='#A', default=2)
        Jbx = VarBox(self, name='JBX', default=3.00)
        b = IntBox(self, name='#B', default=1)
        Jcx = VarBox(self, name='JCX', default=2.00)
        c = IntBox(self, name='#C', default=0)
        Jdx = VarBox(self, name='JDX', default=7.00)
        d = IntBox(self, name='#D', default=0)
        Vcentr = VarBox(self, name='Vcentr', default=150)
        Jax.pack(side=LEFT)
        a.pack(side=LEFT)
        Jbx.pack(side=LEFT)
        b.pack(side=LEFT)
        Jcx.pack(side=LEFT)
        c.pack(side=LEFT)
        Jdx.pack(side=LEFT)
        d.pack(side=LEFT)
        Vcentr.pack(side=LEFT)
        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def request_plot(self):
        kwargs = self.make_kwargs()
        self.controller.new_update(self.model, **kwargs)

    def make_kwargs(self):
        _Jax = self.vars['JAX']
        _a   = self.vars['#A']
        _Jbx = self.vars['JBX']
        _b = self.vars['#B']
        _Jcx = self.vars['JCX']
        _c   = self.vars['#C']
        _Jdx = self.vars['JDX']
        _d = self.vars['#D']
        _Vcentr = self.vars['Vcentr']
        singlet = (_Vcentr, 1)  # using default intensity of 1
        allcouplings = [(_Jax, _a), (_Jbx, _b), (_Jcx, _c), (_Jdx, _d)]
        couplings = [coupling for coupling in allcouplings if coupling[1] != 0]
        data = {'signal': singlet,
                'couplings': couplings}
        return data


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

        # self.controller.update_with_dict(**kwargs)
        self.controller.new_update('nspin', **kwargs)


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


class DNMR_TwoSingletBar(ToolBar):
    """
    DNMR simulation for 2 uncoupled exchanging nuclei.
    -Va > Vb are the chemcial shifts (slow exchange limit)
    -ka is the a-->b rate constant (note: WINDNMR uses ka + kb here)
    -Wa, Wb are effectively T2a and T2b (check width at half height vs. T2s)
    -pa is % of molecules in state a. Note for calculation need to /100 to
    convert to mol fraction.
    """

    def __init__(self, parent=None, **options):
        ToolBar.__init__(self, parent, **options)
        self.model = 'DNMR_Two_Singlets'
        Va = VarButtonBox(self, name='Va', default=165.00)
        Vb = VarButtonBox(self, name='Vb', default=135.00)
        ka = VarButtonBox(self, name='ka', default=1.50)
        Wa = VarButtonBox(self, name='Wa', default=0.5)
        Wb = VarButtonBox(self, name='Wb', default=0.5)
        pa = VarButtonBox(self, name='%a', default=50)
        for widget in [Va, Vb, ka, Wa, Wb, pa]:
            widget.pack(side=LEFT)

        # initialize self.vars with toolbox defaults
        for child in self.winfo_children():
            child.to_dict()

    def request_plot(self):
        _Va = self.vars['Va']
        _Vb = self.vars['Vb']
        _ka = self.vars['ka']
        _Wa = self.vars['Wa']
        _Wb = self.vars['Wb']
        _pa = self.vars['%a'] / 100
        self.controller.new_update(self.model, _Va, _Vb, _ka, _Wa, _Wb, _pa)


class DNMR_AB_Bar(ToolBar):
        """
        DNMR simulation for 2 coupled exchanging nuclei.
        -Va > Vb are the chemcial shifts (slow exchange limit)
        -J is the coupling constant
        -kAB is the exchange rate constant
        -W is peak width at half-height in absence of exchange
        """

        def __init__(self, parent=None, **options):
            ToolBar.__init__(self, parent, **options)
            self.model = 'DNMR_AB'
            Va = VarButtonBox(self, name='Va', default=165.00)
            Vb = VarButtonBox(self, name='Vb', default=135.00)
            J = VarButtonBox(self, name='J', default=12.00)
            kAB = VarButtonBox(self, name='kAB', default=1.50)
            W_ = VarButtonBox(self, name='W',
                              default=0.5)  # W is a tkinter string,
            # so used W_
            for widget in [Va, Vb, J, kAB, W_]:
                widget.pack(side=LEFT)

            # initialize self.vars with toolbox defaults
            for child in self.winfo_children():
                child.to_dict()

        def call_model(self):
            _Va = self.vars['Va']
            _Vb = self.vars['Vb']
            _J = self.vars['J']
            _kAB = self.vars['kAB']
            _W = self.vars['W']

            x, y = dnmrplot_AB(_Va, _Vb, _J, _kAB, _W)
            canvas.clear()
            canvas.plot(x, y)


# temporarily placing some widgets below, to expedite getting toolbars working


class VarBox(Frame):
    """
    Eventually will emulate what the Reich entry box does, more or less.
    Idea is to fill the VarFrame with these modules.
    Current version: checks that only numbers are entered; returns contents
    in a popup.
    Looking ahead: trick may be linking their contents with the calls to
    nmrmath. Also, need to make sure floats, not ints, are returned. Can
    change the is_number routine so that if integer entered, replaced with
    float?
    Inputs:
    -text: appears above the entry box
    -default: default value in entry
    """
    def __init__(self, parent=None, name='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, width=7,
                    validate='key')  # check for number on keypress
        ent.pack(side=TOP, fill=X)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))

        # Default behavior: both return and tab will shift focus to next
        # widget; only save data and ping model if a change is made
        ent.bind('<Return>', lambda event: self.on_return(event))
        ent.bind('<Tab>', lambda event: self.on_tab())

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_number), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    @staticmethod
    def is_number(entry):
        """
        tests to see if entry is acceptable (either empty, or able to be
        converted to a float.)
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            float(entry)
            return True
        except ValueError:
            return False

    def entry_is_changed(self):
        return self.master.vars[self.widgetName] != float(self.value.get())

    def on_return(self, event):
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()
        event.widget.tk_focusNext().focus()

    def on_tab(self):
        if self.entry_is_changed():
            self.to_dict()
            self.master.request_plot()

    def to_dict(self):
        """
        Records widget's contents to the container's dictionary of
        values, filling the entry with 0.00 if it was empty.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0.00)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = float(self.value.get())


# def warw(bar): pass
    """
    Many of the models include Wa (width), Right-Hz, and WdthHz boxes.
    This function tacks these boxes onto a ToolBar.
    Input:
    -ToolBar that has been filled out
    Output:
    -frame with these three boxes and default values left-packed on end
    ***actually, this could be a function in the ToolBar class definition!
    """


class IntBox(Frame):
    """
    A modification of VarBox code. Restricts inputs to integers.
    Inputs:
    -text: appears above the entry box
    -default: default value in entry
    """
    # Future refactor options: either create a base class for an input box
    # that varies in its input restriction (float, int, str etc), and/or
    # look into tkinter built-in entry boxes as component.
    def __init__(self, parent=None, name='', default=0.00, **options):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
        Label(self, text=name).pack(side=TOP, expand=NO, fill=NONE)
        self.widgetName = name  # will be key in dictionary

        # Entries will be limited to numerical
        ent = Entry(self, width=7, validate='key')  # check for int on keypress
        ent.pack(side=TOP, expand=NO, fill=NONE)
        self.value = StringVar()
        ent.config(textvariable=self.value)
        self.value.set(str(default))
        ent.bind('<Return>', lambda event: self.on_event(event))
        ent.bind('<FocusOut>', lambda event: self.on_event(event))

        # check on each keypress if new result will be a number
        ent['validatecommand'] = (self.register(self.is_int), '%P')
        # sound 'bell' if bad keypress
        ent['invalidcommand'] = 'bell'

    @staticmethod
    def is_int(entry):
        """
        tests to see if entry string can be converted to integer
        """
        if not entry:
            return True  # Empty string: OK if entire entry deleted
        try:
            int(entry)
            return True
        except ValueError:
            return False

    def on_event(self, event):
        """
        On event: Records widget's status to the container's dictionary of
        values, fills the entry with 0 if it was empty, tells the container
        to send data to the model, and shifts focus to the next entry box (after
        Return or Tab).
        """
        self.to_dict()
        self.master.request_plot()
        event.widget.tk_focusNext().focus()

    def to_dict(self):
        """
        Converts entry to integer, and stores data in container's vars
        dictionary.
        """
        if not self.value.get():  # if entry left blank,
            self.value.set(0)  # fill it with zero
        # Add the widget's status to the container's dictionary
        self.master.vars[self.widgetName] = int(self.value.get())

class VarButtonBox(Frame):
        """
        A deluxe VarBox that is closer to WINDNMR-style entry boxes.
        ent = entry that holds the value used for calculations
        increment = the amount added to or subtracted from ent by the buttons
        minus and plus buttons subtract/add once;
        up and down buttons repeat as long as button held down.
        Arguments:
        -text: appears above the entry box
        -default: default value in entry
        """

        # To do: use inheritance to avoid repeating code for different widgets
        def __init__(self, parent=None, name='', default=0.00, **options):
            Frame.__init__(self, parent, relief=RIDGE, borderwidth=1, **options)
            Label(self, text=name).pack(side=TOP)

            self.widgetName = name  # will be key in dictionary

            # Entries will be limited to numerical
            ent = Entry(self, width=7,
                        validate='key')  # check for number on keypress
            ent.pack(side=TOP, fill=X)
            self.value = StringVar()
            ent.config(textvariable=self.value)
            self.value.set(str(default))

            # Default behavior: both return and tab will shift focus to next
            # widget; only save data and ping model if a change is made
            # To-Do: consistent routines for VarBox, VarButtonBox, ArrayBox etc.
            # e.g. rename on_tab for general purpose on focus-out
            ent.bind('<Return>', lambda event: self.on_return(event))
            ent.bind('<Tab>', lambda event: self.on_tab())

            # check on each keypress if new result will be a number
            ent['validatecommand'] = (self.register(self.is_number), '%P')
            # sound 'bell' if bad keypress
            ent['invalidcommand'] = 'bell'

            # Create a grid for buttons and increment
            minus_plus_up = Frame(self)
            minus_plus_up.rowconfigure(0,
                                       minsize=30)  # make 2 rows ~same height
            minus_plus_up.columnconfigure(2,
                                          weight=1)  # lets arrow buttons fill
            minus_plus_up.pack(side=TOP, expand=Y, fill=X)

            minus = Button(minus_plus_up, text='-',
                           command=lambda: self.decrease())
            plus = Button(minus_plus_up, text='+',
                          command=lambda: self.increase())
            up = Button(minus_plus_up, text=up_arrow, command=lambda: None)
            up.bind('<Button-1>', lambda event: self.zoom_up())
            up.bind('<ButtonRelease-1>', lambda event: self.stop_action())

            self.mouse1 = False  # Flag used to check if left button held down

            minus.grid(row=0, column=0, sticky=NSEW)
            plus.grid(row=0, column=1, sticky=NSEW)
            up.grid(row=0, column=2, sticky=NSEW)

            # Increment is also limited to numerical entry
            increment = Entry(minus_plus_up, width=4, validate='key')
            increment.grid(row=1, column=0, columnspan=2, sticky=NSEW)
            self.inc = StringVar()
            increment.config(textvariable=self.inc)
            self.inc.set(str(1))  # 1 replaced by argument later?
            increment['validatecommand'] = (self.register(self.is_number), '%P')
            increment['invalidcommand'] = 'bell'

            down = Button(minus_plus_up, text=down_arrow, command=lambda: None)
            down.grid(row=1, column=2, sticky=NSEW)
            down.bind('<Button-1>', lambda event: self.zoom_down())
            down.bind('<ButtonRelease-1>', lambda event: self.stop_action())

        @staticmethod
        def is_number(entry):
            """
            tests to see if entry is acceptable (either empty, or able to be
            converted to a float.)
            """
            if not entry:
                return True  # Empty string: OK if entire entry deleted
            try:
                float(entry)
                return True
            except ValueError:
                return False

        def entry_is_changed(self):
            """True if current entry doesn't match stored entry"""
            return self.master.vars[self.widgetName] != float(self.value.get())

        def on_return(self, event):
            """Records change to entry, calls model, and focuses on next widget"""
            if self.entry_is_changed():
                self.to_dict()
                self.master.request_plot()
            event.widget.tk_focusNext().focus()

        def on_tab(self):
            """Records change to entry, and calls model"""
            if self.entry_is_changed():
                self.to_dict()
                self.master.request_plot()

        def to_dict(self):
            """
            Records widget's contents to the container's dictionary of
            values, filling the entry with 0.00 if it was empty.
            """
            if not self.value.get():  # if entry left blank,
                self.value.set(0.00)  # fill it with zero
            # Add the widget's status to the container's dictionary
            self.master.vars[self.widgetName] = float(self.value.get())

        def stop_action(self):
            """ButtonRelease esets self.mouse1 flag to False"""
            self.mouse1 = False

        def increase(self):
            """Increases ent by inc"""
            current = float(self.value.get())
            increment = float(self.inc.get())
            self.value.set(str(current + increment))
            self.on_tab()

        def decrease(self):
            """Decreases ent by inc"""
            current = float(self.value.get())
            decrement = float(self.inc.get())
            self.value.set(str(current - decrement))
            self.on_tab()

        def zoom_up(self):
            """Increases ent by int as long as button-1 held down"""
            increment = float(self.inc.get())
            self.mouse1 = True
            self.change_value(increment)

        def zoom_down(self):
            """Decreases ent by int as long as button-1 held down"""
            decrement = - float(self.inc.get())
            self.mouse1 = True
            self.change_value(decrement)

        def change_value(self, increment):
            """Adds increment to the value in ent"""
            if self.mouse1:
                self.value.set(str(float(self.value.get()) + increment))
                self.on_tab()  # store value, call model

                # Delay was originally set to 10, but after MVC refactor this
                #  caused an infinite loop (apparently a race condition where
                #  stop action never fired. Testing with the two singlet DNMR
                #  model: still loops at 30 ms; 40 works but uneven; 50 works
                #  fine.
                # May want to refactor how up/down arrows work
                self.after(50, lambda: self.change_value(increment))


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

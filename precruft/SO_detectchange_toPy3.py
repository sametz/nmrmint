"""My attempt to convert this SO answer to Python 3"""

import tkinter as tk


class MyApp(tk.Tk):
    """Example app that uses Tcl arrays"""

    def __init__(self, parent=None, **options):

        tk.Tk.__init__(self, parent, **options)

        self.arrayvar = ArrayVar()
        self.labelvar = tk.StringVar()

        rb1 = tk.Radiobutton(text="one", variable=self.arrayvar("radiobutton"), value=1)
        rb2 = tk.Radiobutton(text="two", variable=self.arrayvar("radiobutton"), value=2)
        cb = tk.Checkbutton(text="checked?", variable=self.arrayvar("checkbutton"),
                             onvalue="on", offvalue="off")
        entry = tk.Entry(textvariable=self.arrayvar("entry"))
        label = tk.Label(textvariable=self.labelvar)
        spinbox = tk.Spinbox(from_=1, to=11, textvariable=self.arrayvar("spinbox"))
        button = tk.Button(text="click to print contents of array", command=self.OnDump)

        for widget in (cb, rb1, rb2, spinbox, entry, button, label):
            widget.pack(anchor="w", padx=10)

        self.labelvar.set("Click on a widget to see this message change")
        self.arrayvar["entry"] = "something witty"
        self.arrayvar["radiobutton"] = 2
        self.arrayvar["checkbutton"] = "on"
        self.arrayvar["spinbox"] = 11

        self.arrayvar.trace(mode="w", callback=self.OnTrace)

    def OnDump(self):
        """Print the contents of the array"""
        print(self.arrayvar.get())

    def OnTrace(self, varname, elementname, mode):
        """Show the new value in a label"""
        self.labelvar.set("%s changed; new value='%s'" % (elementname, self.arrayvar[elementname]))


class ArrayVar(tk.Variable):
    """A variable that works as a Tcl array variable"""

    _default = {}
    _elementvars = {}

    def __init__(self, parent=None, **options):
        tk.Variable.__init__(self, parent, **options)

    def __del__(self):
        self._tk.globalunsetvar(self._name)
        for elementvar in self._elementvars:
            del elementvar

    def __setitem__(self, elementname, value):
        if elementname not in self._elementvars:
            v = ArrayElementVar(varname=self._name, elementname=elementname, master=self._master)
            self._elementvars[elementname] = v
        self._elementvars[elementname].set(value)

    def __getitem__(self, name):
        if name in self._elementvars:
            return self._elementvars[name].get()
        return None

    def __call__(self, elementname):
        """Create a new StringVar as an element in the array"""
        if elementname not in self._elementvars:
            v = ArrayElementVar(varname=self._name, elementname=elementname, master=self._master)
            self._elementvars[elementname] = v
        return self._elementvars[elementname]

    def set(self, dictvalue):
        # this establishes the variable as an array
        # as far as the Tcl interpreter is concerned
        self._master.eval("array set {%s} {}" % self._name)

        for (k, v) in dictvalue.iteritems():
            self._tk.call("array","set",self._name, k, v)

    def get(self):
        """Return a dictionary that represents the Tcl array"""
        value = {}
        for (elementname, elementvar) in self._elementvars.iteritems():
            value[elementname] = elementvar.get()
        return value


class ArrayElementVar(tk.StringVar):
    """A StringVar that represents an element of an array"""
    _default = ""

    def __init__(self, varname, elementname, master):
        self._master = master
        self._tk = master.tk
        self._name = "%s(%s)" % (varname, elementname)
        self.set(self._default)

    def __del__(self):
        """Unset the variable in Tcl."""
        self._tk.globalunsetvar(self._name)


if __name__ == "__main__":
    app=MyApp()
    app.wm_geometry("400x200")
    app.mainloop()
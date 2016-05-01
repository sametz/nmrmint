# File: labelframes.py
# References:
#    http://www.tcl.tk/man/tcl/TkCmd/ttk_labelframe.htm
"""from pyinmyeye.blogspot.com. Investigating its utility."""
from tkinter import *
from tkinter import ttk
from demopanels import MsgPanel, SeeDismissPanel


class LabelFramesDemo(ttk.Frame):

    def __init__(self, isapp=True, name='labelframesdemo'):
        ttk.Frame.__init__(self, name=name)
        self.pack(expand=Y, fill=BOTH)
        self.master.title('Label Frames Demo')
        self.isapp = isapp
        self._create_widgets()

    def _create_widgets(self):
        if self.isapp:
            MsgPanel(self,
              ["Label frames are used to group related widgets together.\n",
               "The 'label' may be either plain text or another widget.\n\n",
               "Individual option states are controlled by the Option label "
               "widget"])

            SeeDismissPanel(self)

        self._create_demo_panel()

    def _create_demo_panel(self):
        demoPanel = Frame(self)
        demoPanel.pack(side=TOP, fill=BOTH, expand=Y)

        valuePane = self._create_value_pane(demoPanel)
        optionPane = self._create_option_pane(demoPanel)
        valuePane.pack(side=LEFT,  expand=True, padx=10, pady=10, fill=BOTH)
        optionPane.pack(side=LEFT, expand=True, padx=10, pady=10, fill=BOTH)

    def _create_value_pane(self, parent):
        # labelanchor N+S centers the label frame text at the top
        # of the frame; S+N - centers on bottom, E+W - to the right
        # W+E - to the left
        lf = ttk.Labelframe(parent, text='Values', labelanchor=N + S)

        self.rb = []
        for i in range(4):
            b = ttk.Radiobutton(lf, text='This is value {}'.format(i),
                                value=i)
            b.pack(side=TOP, fill=X, pady=2)
            self.rb.append(b)

        return lf

    def _create_option_pane(self, parent):
        lf = ttk.Labelframe(parent, text='options')

        self.cbOpt = ttk.Checkbutton(lf, text='Use this option',
                                         command=self._toggle_opt)
        lf['labelwidget'] = self.cbOpt

        self.cbs = []
        for opt in ['Option 1', 'Option 2', 'Option 3']:
            b = ttk.Checkbutton(text=opt, variable=IntVar(),
                                state='disabled', onvalue=1, offvalue=0)
            v = b.cget('variable')  # get variable name
            b.setvar(v, 0)          # set var to off value

            b.pack(in_=lf, side=TOP, fill=X, pady=2, padx=25, anchor=W)
            self.cbs.append(b)

        return lf

    def _toggle_opt(self):
        # state of the option buttons controlled
        # by the state of the Option frame label widget
        for opt in self.cbs:
            if self.cbOpt.instate(('selected', )):
                opt['state'] = '!disabled'  # enable option
            else:
                opt['state'] = 'disabled'

if __name__ == '__main__':
    LabelFramesDemo().mainloop()

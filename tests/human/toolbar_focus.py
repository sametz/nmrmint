"""A human-run test to see if toolbars have correct widget traversal.

Currently only tests FirstOrderBar.
"""
# TODO: add other toolbars as well.

# Purpose: intent is an integration test for toolbars and widgets, to test the
# widget._find_next_entry method (and, at some future time, ._on_return,
# ._on_tab, ._refresh as well.) When a similar, automated test was attempted,
# 'assert current_entry is not next_entry' was always false, and the initial
# entry widget was returned. Hypothesis is that _find_next_entry requires
# .tk.focusNext() and that this in turn requires the mainloop.

import tkinter as tk

from nmrmint.GUI.toolbars import FirstOrderBar


def dummy_callback(*args, **kwargs):
    print(args)
    print(kwargs)


# noinspection PyProtectedMember
def focus_next_entry():
    global current_entry
    next_entry = current_entry.master._find_next_entry(current_entry)
    next_entry.focus()
    print('current: ', current_entry.widgetName, current_entry)
    print('next: ', next_entry.widgetName, next_entry)
    assert current_entry is not next_entry
    assert isinstance(current_entry, (tk.Entry, tk.Spinbox))
    current_entry = next_entry


if __name__ == '__main__':

    root = tk.Tk()
    root.title('test toolbars')

    # Note: immediately packing testbar broke things
    testbar = FirstOrderBar(root, callback=dummy_callback)  # .pack(side=tk.TOP)
    print(type(testbar))
    # noinspection PyProtectedMember
    first_widget = testbar._fields['# of nuclei']
    first_entry = first_widget.entry
    current_entry = first_entry

    focusbutton = tk.Button(testbar,
                            name='focus_button',
                            text='Reset Focus',
                            command=lambda: first_entry.focus())

    focusnextbutton = tk.Button(testbar,
                                name='focus_next_button',
                                text='Next Focus',
                                command=lambda: focus_next_entry())

    focusbutton.pack(side=tk.LEFT)
    focusnextbutton.pack(side=tk.LEFT)
    testbar.pack(side=tk.TOP)

    # workaround fix for Tk problems and mac mouse/trackpad:
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass

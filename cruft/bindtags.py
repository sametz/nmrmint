import tkinter

def on_frame_click(e):
    print("frame clicked")

def retag(tag, *args):
    '''Add the given tag as the first bindtag for every widget passed in'''
    for widget in args:
        widget.bindtags((tag,) + widget.bindtags())

tk = tkinter.Tk()
a_frame = tkinter.Frame(tk, bg="red", padx=20, pady=20)
a_label = tkinter.Label(a_frame, text="A Label")
a_button = tkinter.Button(a_frame, text="click me!")
a_frame.pack()
a_label.pack()
a_button.pack()
tk.protocol("WM_DELETE_WINDOW", tk.destroy)
retag("special", a_frame, a_label, a_button)
tk.bind_class("special", "<Button>", on_frame_click)
tk.mainloop()
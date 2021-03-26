# import tkinter

from tkinter import *


class Timer:
    def __init__(self, parent):
        # variable storing time
        self.seconds = 0
        # label displaying time
        self.label = Label(parent, text="0 s", font="Arial 30", width=10)
        self.label.pack()
        # start the timer

    def fct(self):
        self.label.after(1000, self.refresh_label)

    def refresh_label(self):
        """ refresh the content of the label every second """
        # increment the time
        self.seconds += 1
        # display the new time
        self.label.configure(text="%i s" % self.seconds)
        # request tkinter to call self.refresh after 1s (the delay is given in ms)
        self.label.after(1000, self.refresh_label)


root = Tk()
timer = Timer(root)
timer.fct()
root.mainloop()

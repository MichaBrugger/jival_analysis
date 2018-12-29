import tkinter as tk
from Main import Main

"""
Inspired by sentdex and his course "Object Oriented Programming Crash Course with Python 3"
"""

# Defining different font-styles
LARGE_FONT = ("Verdana", 12)


# Will be stored in a proper place later, just have it here for now
target = ['Shop']
daysback = '2'
Call_Main = Main()
Call_Main.operations_on_csv(target, daysback)


class AnalysisApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side='top', fill='both', expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = StartPage(container, self)

        self.frames[StartPage] = frame

        frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Download")
        button1.pack()

#app = AnalysisApp()
#app.mainloop()
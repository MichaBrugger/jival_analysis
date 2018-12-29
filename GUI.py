import tkinter as tk
from Main import Main
from QueriesSQL import SQL_Queries

"""
Inspired by sentdex and his course "Object Oriented Programming Crash Course with Python 3"
"""

# Defining different font-styles
LARGE_FONT = ("Verdana", 12)


# Will be stored in a proper place later, just have it here for now
target = ['Route']
betterScore = 0.5
Bonus = 6000

Call_Main = Main()



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

        e = tk.Entry()
        e.pack()

        e.focus_set()

        def callback():
            daysback = e.get()
            Call_Main.operations_on_csv(daysback)

        b = tk.Button(text="get", width=10, command=callback)
        b.pack()


app = AnalysisApp()
app.mainloop()
import tkinter as tk
from Main import Main
from QueriesSQL import SQL_Queries

"""
Inspired by sentdex and his course "Object Oriented Programming Crash Course with Python 3"
"""

"""
The following code is meant to be the baseline for a future driver and route analysis for Jivana Vitality. I wrote it
during my internship as a project for the HSG XCamp course. While the current version is not yet capable of the in-depth
analysis that is the goal for the future, it  already serves as an overview for both managers and executives to see how
certain routes and drivers are performing.

To add some context to the project:
Jivana Vitality India Pvt. Ltd. is an Indian for-profit company providing affordable drinking water. It was founded in
2014 by three HSG Students and has since established itself as the biggest water provider in Udaipur, India.
In both rural and urban parts of India access to affordable, clean drinking water is still a big problem and many people
have problems with diseases caused by polluted water. Jivana Vitality tackles this problem by providing bottled - water
quality water for a fraction of the price that bottled water costs, thus making it affordable for everyone. Through five
water-shops in Udaipur we deliver 80'000 liters of water daily to over 5000 active customers directly to their doorstep.

With around 35 routes, each 'driven' by multiple drivers, a performance overview is getting more and more difficult. In
addition Jivana is currently planning expansions to other cities, which makes a automated performance analysis a must.
"""

# All the GUI part is currently heavily under construction, will all be commented/formatted in the next days

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
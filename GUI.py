import tkinter as tk
from Main import Main
from tkinter import ttk
from pandastable import Table, TableModel


# The long term goal is to create a GUI that displays the generated data frames as a stand-alone executable (I did some
# successful first tries with pyinstaller in this regard). This would make it much easier to distribute to the company
# managers since they wouldn't have to install python and all of it's libraries to run the code.

# --------------------------------------

# Calculations currently don't get executed since they are not attached to anything

# Here I store all the input variables that later should be implemented in the GUI (daysback is already "implemented')
betterScore = 0.5 # to get bonus the drivers have to score better than x% of their peers (from 0 to 1)
Bonus = 6000 # how much is the "pot" for the bonuses in INR
Call_Main = Main() # --> here for convenience, doesnt really belong here
#daysback has a input field when you run the code --> needs a number to work

# ---------------------------------------

"""
Inspired by sentdex and his course "Object Oriented Programming Crash Course with Python 3"
"""

# All the GUI part is currently heavily under construction, The AnalysisApp is basically just a copy from sentdexs
# youtube course. The Input page was just to see if tkinter is actually working for me and doing what I want it to do.

# Defining different font-styles
LARGE_FONT = ("Verdana", 12)

class AnalysisApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="Jival.ico")
        tk.Tk.wm_title(self, "Jivana Vitality India Pvt. Ltd.")

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Start Page', command=lambda: self.show_frame(StartPage))
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)
        tk.Tk.config(self, menu=menubar)

        self.frames = {}

        for F in (StartPage, DownloadPage, AnalysisPage, OutputPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(padx=10, pady=10)

        button1 = ttk.Button(self, text="Page 1", command=lambda: controller.show_frame(DownloadPage))
        button1.pack()


class DownloadPage(tk.Frame):

    def __init__(self, parent,controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Download Page", font=LARGE_FONT)
        label.pack(padx=10, pady=10)

        def download():
            daysback = daysbackEntry.get()
            Call_Main.operations_on_csv(daysback)
            controller.show_frame(AnalysisPage)

        daysbackEntry = tk.Entry(self)
        daysbackEntry.insert(0, '12')
        daysbackEntry.pack()
        daysbackEntry.focus_set()

        DownloadButton = ttk.Button(self, text="Download Data", width=15, command=download)
        DownloadButton.pack()

        BackHomeButton = ttk.Button(self, text="Back Home", command=lambda: controller.show_frame(StartPage))
        BackHomeButton.pack()


class AnalysisPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Analysis", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        def analysis():
            target = ['Shop', 'Driver_ID']
            Call_Main.calculations(target, betterScore, Bonus)
            controller.show_frame(OutputPage)

        AnalysisButton = ttk.Button(self, text="Execute Analysis", width=15, command=analysis)
        AnalysisButton.pack()

        BackHomeButton = ttk.Button(self, text="Back Home", command=lambda: controller.show_frame(StartPage))
        BackHomeButton.pack()

class OutputPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Display", font=LARGE_FONT)
        label.pack(padx=10, pady=10)

        
        def display():
            DisplayButton.destroy()
            Output_Ranked = Call_Main.getOutputRanked()
            tk.Frame.__init__(self)
            self.main = self.master
            f = ttk.Frame(self.main)
            f.pack(fill='both', expand=1)
            self.table = pt = Table(f, dataframe=Output_Ranked)
            pt.show()
        """
        def display():
            Output_Ranked = Call_Main.getOutputRanked()
        """

        DisplayButton = ttk.Button(self, text="Display", command=display)
        DisplayButton.pack()

        BackHomeButton = ttk.Button(self, text="Back Home", command=lambda: controller.show_frame(StartPage))
        BackHomeButton.pack()

app = AnalysisApp()
app.geometry("800x600")
app.mainloop()
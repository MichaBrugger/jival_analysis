import tkinter as tk
from Main import Main


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
# youtube course. The Input page was just to see if tkinter is actually working for me and  doing what I want it to do

# Defining different font-styles
LARGE_FONT = ("Verdana", 12)

class AnalysisApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        frame = InputPage(container, self)
        self.frames[InputPage] = frame
        #frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame(InputPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

class InputPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Future Input Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        w = tk.Label(text="Put in the amount of days that should be downloaded and analysed.\n\nIf you want a new set"
                          "of days you currently\nhave to delete the downloaded files or wait for a new day :)")
        w.pack()

        def download():
            daysback = daysbackEntry.get()
            Call_Main.operations_on_csv(daysback)
            #need some kind of input verification here (it needs to be a number)
            # then the window needs to be closed so the rest of the code runs through

        def analysis():
            #Quickfix to run the code properly
            #target = targetEntry.get() #something didnt work properly there
            target = ['Shop', 'Driver_ID']
            Call_Main.calculations(target, betterScore, Bonus)

        daysbackEntry = tk.Entry()
        daysbackEntry.insert(0, '12')
        daysbackEntry.pack(side='left')
        daysbackEntry.focus_set()

        DownloadButton = tk.Button(text="Download Data", width=15, command=download, justify='left')
        DownloadButton.pack(side='left')

        """
        targetEntry = tk.Entry()
        targetEntry.insert(0, 'Driver_ID')
        targetEntry.pack(side='right')
        targetEntry.focus_set()
        """

        AnalysisButton = tk.Button(text="Execute Analysis", width=15, command=analysis)
        AnalysisButton.pack(side='right')


app = AnalysisApp()
app.mainloop()
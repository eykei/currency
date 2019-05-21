'''
Description: Uses a currency api to obtain history of world currencies against the dollar.

Usage:
1. Add any currencies you wish to exclude to exclusions.txt. (one 3 letter currency code per line)
2. Run interface.py
3. Select desired number of datapoint and number of days in history (note datapoins < days), Click Generate
4. Use the << or >> button to view the next or previous 6 charts

Status: Working

ToDo: For some time ranges, currencies don't exist, causing a mismatch in numpy array sizes
'''


from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import configparser
import helper

config= configparser.ConfigParser()
config.read('config.ini')

apiKey = config['API']['apiKey1']


class App:
    def __init__(self, master):
        self.frame = Frame(master)
        self.frame.pack()
        self.plot_index = -1

        nextButton = Button(self.frame, text=">>", command=self.next)
        nextButton.grid(row=3, column=4, ipadx=10, sticky=W+E+N+S)
        
        prevButton = Button(self.frame, text="<<", command=self.prev)
        prevButton.grid(row=3, column=3, ipadx=10, sticky=W+E+N+S)

        self.numDataPointsVar = StringVar()
        e1=Entry(self.frame, textvariable=self.numDataPointsVar, width=20)
        e1.grid(row=3, column=0, ipadx=10, sticky=W+E+N+S)
        e1.insert(0, "# Data Points")

        self.startingPointVar = StringVar()
        e2=Entry(self.frame, textvariable=self.startingPointVar, width=20)
        e2.grid(row=3, column=1, ipadx=10, sticky=W+E+N+S)
        e2.insert(0, "# Days Ago")

        generateButton = Button(self.frame, text="generate", command=self.generateData)
        generateButton.grid(row=3, column=2, ipadx=10, sticky=W+E+N+S)

    def generateData(self):
        self.time_points, self.currencies, self.exchange_matrix, self.nonoutlier_indices, self.slopes, self.coefficients = helper.generateData(apiKey, int(self.numDataPointsVar.get()),
                                                                                           int(self.startingPointVar.get()))
        self.plot(self.plot_index)

    def plot(self, k):
        fig = helper.generatePlot(self.time_points, self.currencies, self.exchange_matrix, self.nonoutlier_indices, self.slopes, self.coefficients, k)

        canvas = FigureCanvasTkAgg(fig, master=self.frame)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=5)

    def next(self):
        self.plot_index -= 6
        self.plot(self.plot_index)

    def prev(self):
        self.plot_index += 6
        self.plot(self.plot_index)

root = Tk()
root.wm_title("Travel Advisor")
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
root.geometry(f"{w}x{h}+0+0")
app=App(root)
root.mainloop()

# def _quit():
#     root.quit()     # stops mainloop
#     root.destroy()  # this is necessary on Windows to prevent
#                     # Fatal Python Error: PyEval_RestoreThread: NULL tstate
#
#
# button = tkinter.Button(master=root, text="Quit", command=_quit)
# button.pack(side=tkinter.BOTTOM)

# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
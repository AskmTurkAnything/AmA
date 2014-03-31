#AmA GUI

from tkinter import *
import os,sys

class Application(Frame):

    def __init__(self, master):
        """Initialize Frame"""
        Frame.__init__(self, master)
        self.grid()
        self.input_filename()
        self.input_assignments()
        self.input_cost()
        self.input_tags()
        
        self.submit_button = Button(self, text = "Submit", command = self.submit)
        self.submit_button.grid(row = 13, column = 0, sticky = W)

    def input_filename(self):
        """Input for filename"""
        self.instruction = Label(self, text = "Enter file address (example C:\stuff.txt) ")
        self.instruction.grid(row = 0, column = 0, columnspan = 6, sticky = W)

        self.filename = Entry(self)
        self.filename.grid(row = 1, column = 1, sticky = W)

        self.display = Text(self, width = 35, height = 5, wrap = WORD)
        self.display.grid(row = 3, column = 0, columnspan = 4, sticky = W)

    def input_assignments(self):
        """Input # of Mturk assignments for the file"""
        self.instruction = Label(self, text = "Enter # of MTurk assignments for this file")
        self.instruction.grid(row = 5, column = 0, columnspan = 2, sticky = W)

        self.assignments = Entry(self)
        self.assignments.grid(row = 6, column = 1, sticky = W)

    def input_cost(self):
        """Input payout"""
        self.instruction = Label(self, text = "Enter payout per assignment")
        self.instruction.grid(row = 7, column = 0, columnspan = 1, sticky = W)

        self.payout = Entry(self)
        self.payout.grid(row = 8, column = 1, sticky = W)
        
    def input_tags(self):
        """Input tags"""
        self.instruction = Label(self, text = "Enter tags for this assignment, separated by commas")
        self.instruction.grid(row = 9, column = 0, columnspan = 3, sticky = W)

        self.description = Entry(self)
        self.description.grid(row = 10, column = 1, sticky = W)
        
    def submit(self):
        """Pressing submit passes the contents of input boxes to the variables used in CLI"""

        """This box displays contents of opened text file"""
        content = self.filename.get()
        fileaddress = open(content, 'r')
        message = fileaddress.read()
        self.display.insert(0.0, message)

        max_assignments = self.assignments.get()

        cost = self.payout.get()

        tags = self.description.get()
        
root = Tk()
root.title("AmA I/O")
root.geometry("400x400")
app=Application(root)

root.mainloop()

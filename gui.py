from Tkinter import *
import subprocess
import re

colour_code = re.compile(r'\033\[(9[1-5]|[0-1])m')

class Application(Frame):
    def set_focus(self, event):
        self.TEXT.focus_set()

    def run(self, pyfile):
        self.TEXT.configure(state="normal")
        self.TEXT.delete(1.0, END)  # clear text
        self.TEXT.configure(state="disabled")
        p = subprocess.Popen(['python', pyfile, '--nocolours'], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        while p.poll() is None:
            l = p.stdout.readline()
            colour_code.sub('', l)  # strip ANSI colour sequences
            self.TEXT.configure(state="normal")
            self.TEXT.insert(END, l)
            self.TEXT.configure(state="disabled")
        self.TEXT.configure(state="normal")
        self.TEXT.insert(END, p.stdout.read())
        self.TEXT.configure(state="disabled")

    def createWidgets(self):
        self.SCAN = Button(self)
        self.SCAN["text"] = "Scan"
        self.SCAN["command"] = lambda: self.run('scan.py')

        self.SCAN.pack({"side": "left"})

        self.PROC = Button(self)
        self.PROC["text"] = "Process"
        self.PROC["command"] = lambda: self.run('process.py')

        self.PROC.pack({"side": "left"})

        self.TEXT = Text(self)
        self.TEXT.pack({"side": "left"})
        self.TEXT.configure(state="disabled")
        self.TEXT.bind('<1>', self.set_focus)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()

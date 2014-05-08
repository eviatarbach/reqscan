import subprocess

from Tkinter import *

SYMBOLOGIES = ['ean13', 'ean8', 'upca', 'upce', 'isbn13', 'isbn10', 'i25',
               'code39', 'code128', 'pdf417', 'qrcode']

class Application(Frame):
    def set_focus(self, event):
        self.TEXT.focus_set()

    def run(self, pyfile):
        self.SCAN.configure(state="disabled")
        self.PROC.configure(state="disabled")
        self.TEXT.configure(state="normal")
        self.TEXT.delete(1.0, END)  # clear text
        self.TEXT.configure(state="disabled")
        p = subprocess.Popen(['python', pyfile, '--nocolours', '--dir',
                             '' if (self.d == 'default') else self.DIR.get()],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        while p.poll() is None:
            l = p.stdout.readline()
            self.TEXT.configure(state="normal")
            self.TEXT.insert(END, l)
            self.TEXT.configure(state="disabled")
        self.TEXT.configure(state="normal")
        self.TEXT.insert(END, p.stdout.read())
        self.TEXT.configure(state="disabled")
        self.SCAN.configure(state="normal")
        self.PROC.configure(state="normal")

    def set_state(self, widget, state):
        if widget.winfo_children():
            for child in widget.winfo_children():
                child.configure(state=state)
        else:
            widget.configure(state=state)

    def createWidgets(self):
        self.TEXT = Text(self)
        self.TEXT.grid(row=0, column=2)
        self.TEXT.configure(state="disabled")
        self.TEXT.bind('<1>', self.set_focus)

        self.d = StringVar()
        self.d.set('default')

        self.SCANOPTIONS = Frame(self)
        self.SCANOPTIONS.grid(row=0, column=0, sticky='N')

        Label(self.SCANOPTIONS, text='Scan options:').grid(row=0, column=0,
                                                           sticky='W')

        self.source = StringVar()

        Label(self.SCANOPTIONS, text='DPI:').grid(row=1, column=0, sticky='W')
        Entry(self.SCANOPTIONS).grid(row=2, column=0, sticky='W')
        Label(self.SCANOPTIONS, text='Scan source:').grid(row=3, column=0,
                                                          sticky='W')
        OptionMenu(self.SCANOPTIONS, self.source, 'a', 'b').grid(row=4,
                                                                 column=0,
                                                                 sticky='W')
        Button(self.SCANOPTIONS, text="Scan",
               command=lambda: self.run('scan.py')).grid(row=5, column=0,
                                                         sticky='W')
        self.PROCOPTIONS = Frame(self)
        self.PROCOPTIONS.grid(row=0, column=1, sticky='N')

        self.DEFAULTDIR = Radiobutton(self.PROCOPTIONS, text="Default (today's date)",
                                      var=self.d, value='default',
                                      command=lambda:
                                               self.DIR.configure(state='disabled'))
        self.CUSTOMDIR = Radiobutton(self.PROCOPTIONS, text="Custom",
                                     var=self.d, value='custom',
                                     command=lambda:
                                              self.DIR.configure(state='normal'))

        Label(self.PROCOPTIONS, text="Process to folder:").grid(row=0, column=0, sticky='W')
        self.DEFAULTDIR.grid(row=1, column=0, sticky='W')
        self.CUSTOMDIR.grid(row=2, column=0, sticky='W')
        self.DIR = Entry(self.PROCOPTIONS)
        self.DIR.grid(row=3, column=0, sticky='W')
        self.DIR.configure(state="disabled")

        self.PROC = Button(self.PROCOPTIONS, text="Process",
                           command=lambda: self.run('process.py'))

        self.PROC.grid(row=4, column=0, sticky='W')

        self.CROP = Frame(self.PROCOPTIONS)
        self.CROP.grid(row=6, column=0, sticky='W')

        self.crop_check_state = StringVar()
        self.CROP_CHECK = Checkbutton(self.PROCOPTIONS, text="Crop",
                                      variable=self.crop_check_state,
                                      command=lambda:
                                               self.set_state(self.CROP,
                                                              self.crop_check_state.get()),
                                      onvalue='normal', offvalue='disabled')
        self.crop_check_state.set('disabled')

        self.CROP_CHECK.grid(row=5, column=0, sticky='W')
        self.cropbox = [IntVar(), IntVar(), IntVar(), IntVar()]
        Label(self.CROP, text='(').grid(row=0, column=0)
        Entry(self.CROP, textvariable=self.cropbox[0]).grid(row=0, column=1)
        Label(self.CROP, text=',').grid(row=0, column=2)
        Entry(self.CROP, textvariable=self.cropbox[1]).grid(row=0, column=3)
        Label(self.CROP, text=')').grid(row=0, column=4)

        Label(self.CROP, text='(').grid(row=1, column=0)
        Entry(self.CROP, textvariable=self.cropbox[2]).grid(row=1, column=1)
        Label(self.CROP, text=',').grid(row=1, column=2)
        Entry(self.CROP, textvariable=self.cropbox[3]).grid(row=1, column=3)
        Label(self.CROP, text=')').grid(row=1, column=4)

        self.set_state(self.CROP, 'disabled')
        self.symbologies = Frame(self.PROCOPTIONS)
        Label(self.PROCOPTIONS, text='Symbologies:').grid(row=7, column=0,                                                           sticky='W')
        self.symbologies.grid(row=8, column=0, sticky='W')

        for i, sym in enumerate(SYMBOLOGIES):
            Checkbutton(self.symbologies, text=sym).grid(row=i//2, column=i%2,
                                                         sticky='W')

        # Data Matrix reading is not provided by ZBar, so has to be handled
        # separately
        Checkbutton(self.symbologies, text='datamatrix').grid(row=(i + 1)//2,
                                                              column=(i + 1)%2,
                                                              sticky='W')

        self.resize = DoubleVar()
        self.resize.set(1.0)
        self.resize_field = Entry(self.PROCOPTIONS, textvariable=self.resize,
                                  state='disabled')
        self.resize_field.grid(row=10, column=0, sticky='W')
        self.resize_var = StringVar()
        self.resize_var.set('disabled')
        Checkbutton(self.PROCOPTIONS, text='Resize', variable=self.resize_var,
                    onvalue='normal', offvalue='disabled',
                    command=lambda: self.set_state(self.resize_field,
                                                   self.resize_var.get())).grid(row=9, column=0, sticky='W')

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
app = Application(master=root)
app.master.title('Reqscan')
app.mainloop()
root.destroy()

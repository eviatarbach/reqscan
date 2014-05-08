#!/usr/bin/env python
'''
Copyright 2011--2014 Eviatar Bach

This file is part of reqscan.

reqscan is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

reqscan is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
reqscan. If not, see http://www.gnu.org/licenses/.

reqscan is an open-source Python-based electronic medical record
(EMR) system, focusing on automatically digitizing records with barcode
recognition.'''

import subprocess

from Tkinter import *

SYMBOLOGIES = ['ean13', 'ean8', 'upca', 'upce', 'isbn13', 'isbn10', 'i25',
               'code39', 'code128', 'pdf417', 'qrcode']

class Application(Frame):
    def run_script(self, pyfile):
        self.SCAN.configure(state="disabled")
        self.PROC.configure(state="disabled")
        self.output.configure(state="normal")
        self.output.delete(1.0, END)  # clear text
        self.output.configure(state="disabled")
        p = subprocess.Popen(['python', pyfile, '--nocolours', '--dir',
                              ('' if (self.dir_var.get() == 'default') else
                               self.dir.get())],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        while p.poll() is None:
            l = p.stdout.readline()
            self.output.configure(state="normal")
            self.output.insert(END, l)
            self.output.configure(state="disabled")
        self.output.configure(state="normal")
        self.output.insert(END, p.stdout.read())
        self.output.configure(state="disabled")
        self.SCAN.configure(state="normal")
        self.PROC.configure(state="normal")

    def set_state(self, widget, state):
        '''Set states of a widget's children if it has any, else just set its
           state.'''
        if widget.winfo_children():
            for child in widget.winfo_children():
                child.configure(state=state)
        else:
            widget.configure(state=state)

    def create_widgets(self):
        # Script output
        self.output = Text(self, state='disabled')
        self.output.grid(row=0, column=2)

        # Don't let there be a cursor
        self.output.bind('<1>', lambda event: self.output.focus_set())

        self.scan_pane = Frame(self)
        self.scan_pane.grid(row=0, column=0, sticky='N')

        Label(self.scan_pane, text='Scan options:').grid(row=0, column=0,
                                                         sticky='W')

        Label(self.scan_pane, text='DPI:').grid(row=1, column=0, sticky='W')
        self.dpi = IntVar()
        self.dpi.set(300)
        Entry(self.scan_pane, textvariable=self.dpi).grid(row=2,
                                                          column=0,
                                                          sticky='W')

        self.source = StringVar()
        Label(self.scan_pane, text='Scan source:').grid(row=3, column=0,
                                                        sticky='W')

        OptionMenu(self.scan_pane, self.source, 'a', 'b').grid(row=4,
                                                               column=0,
                                                               sticky='W')
        Button(self.scan_pane, text="Scan",
               command=lambda: self.run_script('scan.py')).grid(row=5,
                                                                column=0,
                                                                sticky='W')
        self.process_pane = Frame(self)
        self.process_pane.grid(row=0, column=1, sticky='N')

        self.dir_var = StringVar()
        self.dir_var.set('default')

        self.default_dir = Radiobutton(self.process_pane, text="Default (today's date)",
                                       var=self.dir_var, value='default',
                                       command=lambda:
                                                self.dir.configure(state='disabled'))
        self.custom_dir = Radiobutton(self.process_pane, text="Custom",
                                      var=self.dir_var, value='custom',
                                      command=lambda:
                                               self.dir.configure(state='normal'))

        Label(self.process_pane, text="Process to folder:").grid(row=0, column=0, sticky='W')
        self.default_dir.grid(row=1, column=0, sticky='W')
        self.custom_dir.grid(row=2, column=0, sticky='W')
        self.dir = Entry(self.process_pane)
        self.dir.grid(row=3, column=0, sticky='W')
        self.dir.configure(state="disabled")

        self.crop = Frame(self.process_pane)
        self.crop.grid(row=6, column=0, sticky='W')

        self.crop_check_state = StringVar()
        self.crop_CHECK = Checkbutton(self.process_pane, text="Crop",
                                      variable=self.crop_check_state,
                                      command=lambda:
                                               self.set_state(self.crop,
                                                              self.crop_check_state.get()),
                                      onvalue='normal', offvalue='disabled')
        self.crop_check_state.set('disabled')

        self.crop_CHECK.grid(row=5, column=0, sticky='W')
        self.cropbox = [IntVar(), IntVar(), IntVar(), IntVar()]
        Label(self.crop, text='(').grid(row=0, column=0)
        Entry(self.crop, textvariable=self.cropbox[0]).grid(row=0, column=1)
        Label(self.crop, text=',').grid(row=0, column=2)
        Entry(self.crop, textvariable=self.cropbox[1]).grid(row=0, column=3)
        Label(self.crop, text=')').grid(row=0, column=4)

        Label(self.crop, text='(').grid(row=1, column=0)
        Entry(self.crop, textvariable=self.cropbox[2]).grid(row=1, column=1)
        Label(self.crop, text=',').grid(row=1, column=2)
        Entry(self.crop, textvariable=self.cropbox[3]).grid(row=1, column=3)
        Label(self.crop, text=')').grid(row=1, column=4)

        self.set_state(self.crop, 'disabled')
        self.symbologies = Frame(self.process_pane)
        Label(self.process_pane, text='Symbologies:').grid(row=7, column=0,                                                           sticky='W')
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
        self.resize_field = Entry(self.process_pane, textvariable=self.resize,
                                  state='disabled')
        self.resize_field.grid(row=10, column=0, sticky='W')
        self.resize_var = StringVar()
        self.resize_var.set('disabled')
        Checkbutton(self.process_pane, text='Resize', variable=self.resize_var,
                    onvalue='normal', offvalue='disabled',
                    command=lambda: self.set_state(self.resize_field,
                                                   self.resize_var.get())).grid(row=9, column=0, sticky='W')

        self.PROC = Button(self.process_pane, text="Process",
                           command=lambda: self.run_script('process.py'))

        self.PROC.grid(row=4, column=0, sticky='W')

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()

root = Tk()
app = Application(master=root)
app.master.title('Reqscan')
app.mainloop()

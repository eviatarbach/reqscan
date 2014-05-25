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
import ConfigParser

from Tkinter import *
import ttk
import tkFont

SYMBOLOGIES = ['ean13', 'ean8', 'upca', 'upce', 'isbn13', 'isbn10', 'i25',
               'code39', 'code128', 'pdf417', 'qrcode']

class Application(Frame):
    def scan(self):
        try:
            dpi = self.dpi.get()
        except ValueError:  # some value invalid for an int, like 'a'
            dpi = 300
        opt_dict = {'dpi': dpi,
                    'source': self.source.get()}
        self.config.defaults().update(opt_dict)
        self.save_options()
        self.run_script('scan.py')

    def process(self):
        try:
            if self.resize_var.get() == 'normal':
                resize = self.resize_field.get()
            else:
                resize = 1.0
        except ValueError:
            resize = 1.0

        try:
            if self.crop_check_state.get() == 'normal':
                cropbox = ' '.join([str(field.get()) for field in self.cropbox])
            else:
                cropbox = 'None'
        except ValueError:
            cropbox = 'None'
        opt_dict = {'cropbox': cropbox,
                    'datamatrix': ('True' if (self.data_matrix.get() == 1) else
                                   'False'),
                    'symbologies': ' '.join(filter(None,
                                                   [(SYMBOLOGIES[i] if var.get()
                                                     else '') for i, var in
                                                    enumerate(self.sym_vars)])),
                    'resize': resize}
        self.config.defaults().update(opt_dict)
        self.save_options()
        self.run_script('process.py')

    def save_options(self):
        with open('options_gui.txt', 'w') as options_file:
            self.config.add_section('Options')
            self.config.write(options_file)
            #options_file.close()

    def run_script(self, pyfile):
        self.scan_button.configure(state="disabled")
        self.process_button.configure(state="disabled")
        self.output.configure(state="normal")
        self.output.delete(1.0, END)  # clear text
        self.output.configure(state="disabled")
        p = subprocess.Popen(['python', pyfile, '--nocolours', '--gui', '--dir',
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
        self.scan_button.configure(state="normal")
        self.process_button.configure(state="normal")

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
        self.output.grid(row=0, column=2, sticky='N', padx=(40, 0))

        # Don't let there be a cursor
        self.output.bind('<1>', lambda event: self.output.focus_set())

        # Start scan widgets
        self.scan_pane = Frame(self, relief='groove', borderwidth=1)
        self.scan_pane.grid(row=0, column=0, sticky='N', ipadx=15, ipady=15)

        self.bold_font = tkFont.Font(font='TkDefaultFont')
        self.bold_font['weight'] = 'bold'
        self.scan_label = ttk.Label(self.scan_pane, text='Scan options',
                                    font=self.bold_font)
        self.scan_label.grid(row=0, column=0, sticky='W', pady=(0, 15))

        ttk.Label(self.scan_pane, text='DPI:').grid(row=1, column=0,
                                                    sticky='W')
        self.dpi = IntVar()
        self.dpi.set(300)
        ttk.Entry(self.scan_pane, textvariable=self.dpi,
                  width=6).grid(row=2,
                                column=0,
                                sticky='W',
                                pady=(0, 15))

        self.source = StringVar()
        ttk.Label(self.scan_pane, text='Scan source:').grid(row=3, column=0,
                                                        sticky='W')

        ttk.Entry(self.scan_pane, textvariable=self.source).grid(row=4,
                                                                column=0,
                                                                sticky='W')
        self.scan_button = ttk.Button(self, text="Scan",
                                      command=self.scan)
        self.scan_button.grid(row=1, column=0, sticky='W')

        # Start process widgets
        self.process_pane = Frame(self, relief='groove', borderwidth=1)
        self.process_pane.grid(row=0, column=1, sticky='N', ipadx=15, ipady=15,
                               pady=(0, 15), padx=(15, 0))

        ttk.Label(self.process_pane, text='Process options',
                  font=self.bold_font).grid(row=0, column=0, sticky='W',
                                            pady=(0, 15))

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

        ttk.Label(self.process_pane, text="Process to folder:").grid(row=1, column=0, sticky='W')
        self.default_dir.grid(row=2, column=0, sticky='W')
        self.custom_dir.grid(row=3, column=0, sticky='W')
        self.dir = ttk.Entry(self.process_pane)
        self.dir.grid(row=4, column=0, sticky='W')
        self.dir.configure(state="disabled")

        self.crop = Frame(self.process_pane)
        self.crop.grid(row=6, column=0, sticky='W')

        self.crop_check_state = StringVar()
        self.crop_check = Checkbutton(self.process_pane, text="Crop",
                                      variable=self.crop_check_state,
                                      command=lambda:
                                               self.set_state(self.crop,
                                                              self.crop_check_state.get()),
                                      onvalue='normal', offvalue='disabled')
        self.crop_check_state.set('disabled')

        self.crop_check.grid(row=5, column=0, sticky='W', pady=(15, 0))
        self.cropbox = [IntVar(), IntVar(), IntVar(), IntVar()]
        ttk.Label(self.crop, text='(').grid(row=0, column=0)
        ttk.Entry(self.crop, textvariable=self.cropbox[0],
                  width=7).grid(row=0, column=1)
        ttk.Label(self.crop, text=', ').grid(row=0, column=2)
        ttk.Entry(self.crop, textvariable=self.cropbox[1],
                  width=7).grid(row=0, column=3)
        ttk.Label(self.crop, text=')').grid(row=0, column=4)
        ttk.Label(self.crop, text='(').grid(row=1, column=0)
        ttk.Entry(self.crop, textvariable=self.cropbox[2],
                  width=7).grid(row=1, column=1)
        ttk.Label(self.crop, text=', ').grid(row=1, column=2)
        ttk.Entry(self.crop, textvariable=self.cropbox[3],
                  width=7).grid(row=1, column=3)
        ttk.Label(self.crop, text=')').grid(row=1, column=4)

        self.set_state(self.crop, 'disabled')
        self.symbologies = Frame(self.process_pane)
        ttk.Label(self.process_pane, text='Symbologies:').grid(row=7, column=0,
                                                               sticky='W',
                                                               pady=(15, 0))
        self.symbologies.grid(row=8, column=0, sticky='W')

        self.sym_vars = [IntVar() for sym in SYMBOLOGIES]

        for i, sym in enumerate(SYMBOLOGIES):
            Checkbutton(self.symbologies, text=sym,
                        variable=self.sym_vars[i]).grid(row=i//2, column=i%2,
                                                        sticky='W')

        # Data Matrix reading is not provided by ZBar, so has to be handled
        # separately
        self.data_matrix = IntVar()
        Checkbutton(self.symbologies, text='datamatrix',
                    variable=self.data_matrix).grid(row=(i + 1)//2,
                                                              column=(i + 1)%2,
                                                              sticky='W')

        self.resize = DoubleVar()
        self.resize.set(1.0)
        self.resize_field = ttk.Entry(self.process_pane, textvariable=self.resize,
                                      state='disabled', width=5)
        self.resize_field.grid(row=10, column=0, sticky='W')
        self.resize_var = StringVar()
        self.resize_var.set('disabled')
        Checkbutton(self.process_pane, text='Resize', variable=self.resize_var,
                    onvalue='normal', offvalue='disabled',
                    command=lambda: self.set_state(self.resize_field,
                                                   self.resize_var.get())).grid(row=9, column=0, sticky='W', pady=(15, 0))

        self.process_button = ttk.Button(self, text="Process",
                                         command=self.process)

        self.process_button.grid(row=1, column=1, sticky='W')

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()
        self.config = ConfigParser.RawConfigParser()
        '''with open('options_gui.txt', 'w+') as options_file:
            try:
                self.config.readfp(options_file)
            except (IOError, ConfigParser.NoSectionError):
                pass'''
        #self.options_file.close()

root = Tk()
root.resizable(0, 0) # disable resizing
root.configure(padx=20, pady=20)
root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file='icon.png'))
app = Application(master=root)
app.master.title('Reqscan')
app.mainloop()

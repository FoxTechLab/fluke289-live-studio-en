# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
import queue
import threading
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from .history import load_session
from .history_gui import HistoryWindow,BG,TEXT,MUTED
from .comparison import choices,compare_histories,preferred_pair,comparison_stats

class ComparisonWindow:
    def __init__(self,parent,paths=None):
        self.window=tk.Toplevel(parent,bg=BG);self.window.title('Compare two recordings');self.window.geometry('1050x610');self.window.minsize(950,560)
        self.paths=[None,None]
        self.sources=[None,None];self.options=[[],[]];self.boxes=[];self.names=[];self.jobs=queue.Queue();self.closed=False
        self.window.protocol('WM_DELETE_WINDOW',self.close)
        body=tk.Frame(self.window,bg=BG,padx=18,pady=18);body.pack(fill='both',expand=True)
        tk.Label(body,text='Compare recordings A and B',bg=BG,fg=TEXT,font=('DejaVu Sans',16,'bold')).pack(anchor='w')
        for index,label in enumerate(['A','B']):
            row=tk.Frame(body,bg=BG);row.pack(fill='x',pady=10)
            ttk.Button(row,text=f'Choose file {label}…',command=lambda i=index:self.load(i)).pack(side='left')
            name=tk.StringVar(value='No file selected');self.names.append(name)
            tk.Label(row,textvariable=name,bg=BG,fg=MUTED).pack(side='left',padx=12)
            box=ttk.Combobox(body,state='readonly');box.pack(fill='x');self.boxes.append(box)
        row=tk.Frame(body,bg=BG);row.pack(fill='x',pady=12)
        self.mode=tk.StringVar(value='Meter time')
        ttk.Combobox(row,textvariable=self.mode,state='readonly',values=['Meter time','From both series starts'],width=25).pack(side='left')
        tk.Label(row,text='Shift B by seconds (+ later, − earlier):',bg=BG,fg=TEXT).pack(side='left',padx=10)
        self.shift=tk.StringVar(value='0');ttk.Entry(row,textvariable=self.shift,width=12).pack(side='left')
        limit_row=tk.Frame(body,bg=BG);limit_row.pack(fill='x',pady=(0,8))
        tk.Label(limit_row,text='Maximum matched-reading time gap [s]:',bg=BG,fg=TEXT).pack(side='left')
        self.tolerance=tk.StringVar(value='0.5')
        ttk.Entry(limit_row,textvariable=self.tolerance,width=10).pack(side='left',padx=8)
        self.feedback=tk.StringVar(value='Select files A and B using the buttons above.')
        tk.Label(body,textvariable=self.feedback,bg=BG,fg=TEXT,wraplength=880,justify='left').pack(fill='x',pady=(0,10))
        self.compare_button=ttk.Button(body,text='Compare on one chart',command=self.show,state='disabled')
        self.compare_button.pack(anchor='w')
        tk.Label(body,text='Select the same unit. Start alignment aligns origins; it does not synchronize measurements. Files remain unchanged.',bg=BG,fg=MUTED,wraplength=880,justify='left').pack(anchor='w',pady=10)
        self.window.after(100,self.poll)
        for index,path in enumerate((paths or [])[:2]):self.load(index,path)

    def load(self,index,path=None):
        if path is None:path=filedialog.askopenfilename(parent=self.window,title='Select recording '+ 'AB'[index],filetypes=[('Fluke recordings','*.csv *.json *.sqlite3'),('All files','*')])
        if not path:return
        self.names[index].set('Loading…');self.sources[index]=None;self.boxes[index].set('')
        self.options[index]=[];self.boxes[index]['values']=[]
        self.compare_button.configure(state='disabled')
        self.feedback.set('Loading file '+ 'AB'[index]+'…')
        def work():
            try:self.jobs.put((index,path,load_session(path),None))
            except Exception as error:self.jobs.put((index,path,None,str(error)))
        threading.Thread(target=work,daemon=True).start()

    def poll(self):
        if self.closed:return
        try:
            while True:
                index,path,history,error=self.jobs.get_nowait()
                if error:
                    self.names[index].set('Read error');self.feedback.set('Could not load the file. Select it again.');messagebox.showerror('Comparison',error,parent=self.window);continue
                self.sources[index]=history;self.paths[index]=str(Path(path).resolve());self.names[index].set(Path(path).name)
                self.options[index]=choices(history)
                self.boxes[index]['values']=[f'Series {s} · '+{'PRIMARY':'Main reading (PRIMARY)','LIVE':'Current reading (LIVE)','MAXIMUM':'Interval maximum (MAXIMUM)','MINIMUM':'Interval minimum (MINIMUM)'}.get(field,field)+f' · {unit}' for s,field,unit in self.options[index]]
                if self.options[index]:
                    preferred=next((i for i,c in enumerate(self.options[index]) if c[1]=='PRIMARY'),0)
                    self.boxes[index].current(preferred)
                self.match_fields()
        except queue.Empty:pass
        self.window.after(100,self.poll)

    def match_fields(self):
        ready=all(h is not None for h in self.sources)
        self.compare_button.configure(state='normal' if ready else 'disabled')
        if not ready:
            self.feedback.set('Select and load both files A and B to match readings.')
            return
        pair=preferred_pair(*self.options)
        if pair:
            for index,selection in enumerate(pair):self.boxes[index].current(self.options[index].index(selection))
            self.feedback.set(f'Automatically selected A: {pair[0][1]} ↔ B: {pair[1][1]} · {pair[0][2]}. Click “Compare on one chart”.')
        else:
            self.feedback.set('These files share no measurement unit. Select another pair.')
            self.compare_button.configure(state='disabled')

    def show(self):
        try:
            if any(h is None for h in self.sources):raise ValueError('Select both files and wait for them to load.')
            selections=[options[box.current()] for options,box in zip(self.options,self.boxes) if box.current()>=0]
            if len(selections)!=2:raise ValueError('Select a field in both files.')
            shift=float(self.shift.get().replace(',','.'));relative=self.mode.get()!='Meter time'
            history=compare_histories(*self.sources,*selections,shift=shift,relative=relative)
            tolerance=float(self.tolerance.get().replace(',','.'))
            history.comparison_stats=comparison_stats(history,tolerance)
            title=f'A: {self.names[0].get()} | B: {self.names[1].get()} | B offset: {shift:g} s'
            history.comparison_metadata={'source_paths':list(self.paths),'file_a':self.names[0].get(),'file_b':self.names[1].get(),'field_a':selections[0][1],'field_b':selections[1][1],'unit':selections[0][2],'shift':shift,'relative':relative,'tolerance':tolerance}
            history.comparison_description=f'A: {self.names[0].get()} · {selections[0][1]}\nB: {self.names[1].get()} · {selections[1][1]}\n'+('Time from each series start' if relative else 'Alignment by Fluke reading time')+f' · B offset: {shift:g} s'
            if selections[0][1]!=selections[1][1]:
                history.comparison_description+='\nNote: different reading types are being compared, e.g. an interval maximum and a current reading.'
            HistoryWindow(self.window,history,title=title,live=False)
        except (ValueError,KeyError) as error:messagebox.showerror('Comparison',str(error),parent=self.window)

    def close(self):self.closed=True;self.window.destroy()

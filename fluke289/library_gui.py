# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
import queue
import threading
from pathlib import Path
from datetime import datetime,timezone
import tkinter as tk
from tkinter import ttk,filedialog,messagebox,simpledialog
from .library import Library
from .history import load_session
from .history_gui import HistoryWindow,BG,TEXT,MUTED
from .comparison_gui import ComparisonWindow

def duration_text(seconds):
    seconds=int(seconds);days,seconds=divmod(seconds,86400);hours,seconds=divmod(seconds,3600);minutes,seconds=divmod(seconds,60)
    return (f'{days} days ' if days else '')+f'{hours:02}:{minutes:02}:{seconds:02}'

class LibraryWindow:
    def __init__(self,parent):
        self.catalog=Library();self.closed=False;self.busy=False;self.entries={};self.jobs=queue.Queue();self.sort_key='start';self.reverse=True
        self.window=tk.Toplevel(parent,bg=BG);self.window.title('Measurement library');self.window.geometry('1280x720');self.window.minsize(1050,600)
        self.window.protocol('WM_DELETE_WINDOW',self.close)
        body=tk.Frame(self.window,bg=BG,padx=18,pady=16);body.pack(fill='both',expand=True)
        tk.Label(body,text='Measurement library',bg=BG,fg=TEXT,font=('DejaVu Sans',19,'bold')).pack(anchor='w')
        tk.Label(body,text='Add a recordings folder or individual files. Files remain in their original locations.',bg=BG,fg=MUTED).pack(anchor='w',pady=(4,12))
        top=tk.Frame(body,bg=BG);top.pack(fill='x')
        self.actions=[]
        for label,command in [('Add folder…',self.add_folder),('Add files…',self.add_files),('Refresh library',self.refresh)]:
            b=ttk.Button(top,text=label,command=command);b.pack(side='left',padx=(0,8));self.actions.append(b)
        self.recursive=tk.BooleanVar(value=False)
        ttk.Checkbutton(top,text='Include subfolders',variable=self.recursive).pack(side='left')
        filters=tk.Frame(body,bg=BG);filters.pack(fill='x',pady=12)
        tk.Label(filters,text='Search:',bg=BG,fg=TEXT).pack(side='left')
        self.search=tk.StringVar();ttk.Entry(filters,textvariable=self.search).pack(side='left',fill='x',expand=True,padx=8)
        self.source=tk.StringVar(value='All sources');box=ttk.Combobox(filters,textvariable=self.source,state='readonly',values=['All sources','Application','Fluke memory'],width=22);box.pack(side='left')
        self.search.trace_add('write',lambda *_:self.render());self.source.trace_add('write',lambda *_:self.render())
        area=tk.Frame(body,bg=BG);area.pack(fill='both',expand=True)
        columns=['name','start','functions','units','duration','count','source','state']
        self.table=ttk.Treeview(area,columns=columns,show='headings',selectmode='extended')
        labels=['Name','Start date (UTC)','Function','Units','Duration','Intervals / samples','Source','State']
        for key,label,width in zip(columns,labels,[250,165,150,100,105,120,140,100]):
            self.table.heading(key,text=label,command=lambda k=key:self.sort(k));self.table.column(key,width=width,minwidth=65)
        self.table.grid(row=0,column=0,sticky='nsew')
        sy=ttk.Scrollbar(area,orient='vertical',command=self.table.yview);sy.grid(row=0,column=1,sticky='ns')
        sx=ttk.Scrollbar(area,orient='horizontal',command=self.table.xview);sx.grid(row=1,column=0,sticky='ew')
        self.table.configure(yscrollcommand=sy.set,xscrollcommand=sx.set);area.rowconfigure(0,weight=1);area.columnconfigure(0,weight=1)
        self.table.bind('<<TreeviewSelect>>',lambda e:self.selection_changed());self.table.bind('<Double-Button-1>',lambda e:self.open_selected())
        bar=tk.Frame(body,bg=BG);bar.pack(fill='x',pady=12)
        self.open_button=ttk.Button(bar,text='Open selected',command=self.open_selected,state='disabled');self.open_button.pack(side='left')
        self.compare_button=ttk.Button(bar,text='Compare two selected',command=self.compare,state='disabled');self.compare_button.pack(side='left',padx=8)
        self.label_button=ttk.Button(bar,text='Label recording…',command=self.rename,state='disabled');self.label_button.pack(side='left')
        self.remove_button=ttk.Button(bar,text='Remove from list',command=self.remove,state='disabled');self.remove_button.pack(side='right')
        self.status=tk.StringVar(value='Choose “Add folder…” to find existing recordings.')
        tk.Label(body,textvariable=self.status,bg=BG,fg=TEXT,anchor='w',justify='left',wraplength=1180).pack(fill='x')
        self.details=tk.StringVar();tk.Label(body,textvariable=self.details,bg=BG,fg=MUTED,anchor='w',justify='left',wraplength=1180).pack(fill='x',pady=8)
        self.issues=[];ttk.Button(body,text='Skipped file details',command=self.show_issues).pack(anchor='w')
        self.reload();self.window.after(100,self.poll)

    def job(self,kind,work):
        if self.busy:return
        self.busy=True;self.status.set('Processing… LIVE preview remains active.')
        for b in self.actions:b.configure(state='disabled')
        self.selection_changed()
        def run():
            try:self.jobs.put((kind,work(),None))
            except Exception as error:self.jobs.put((kind,None,str(error)))
        threading.Thread(target=run,daemon=True).start()
    def add_folder(self):
        folder=filedialog.askdirectory(parent=self.window,title='Select measurement folder')
        if folder:
            recursive=self.recursive.get();self.job('scan',lambda:self.catalog.scan(folder,recursive))
    def add_files(self):
        paths=filedialog.askopenfilenames(parent=self.window,title='Add saved measurements',filetypes=[('Fluke measurements','*.csv *.json *.sqlite3'),('All files','*')])
        if not paths:return
        def work():
            count=0;errors=[]
            for path in paths:
                try:self.catalog.add(path);count+=1
                except Exception as error:errors.append(Path(path).name+': '+str(error))
            return count,errors
        self.job('scan',work)
    def refresh(self):self.job('scan',self.catalog.refresh)
    def reload(self):
        self.entries={m['path']:m for m in self.catalog.entries()};self.render()
    def render(self):
        if not hasattr(self,'table'):return
        selected=self.table.selection();self.table.delete(*self.table.get_children())
        query=self.search.get().casefold().strip();source=self.source.get();visible=[]
        for item in self.entries.values():
            item=dict(item)
            try:
                stat=Path(item['path']).stat()
                item['state']='Available' if (stat.st_mtime_ns,stat.st_size)==(item['mtime'],item['size']) else 'Changed - refresh'
            except OSError:item['state']='File missing'
            item['name']=item['label'] or item['name']
            if source!='All sources' and not item['source'].startswith(source):continue
            if query and query not in ' '.join(str(v) for v in item.values()).casefold():continue
            visible.append(item)
        visible.sort(key=lambda m:m.get(self.sort_key,''),reverse=self.reverse)
        for m in visible:
            date=datetime.fromtimestamp(m['start'],timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            functions=m['functions']
            for code,label in [('TEMPERATURE','Temperature'),('OHMS','Resistance'),('V_AC','Voltage AC'),('V_DC','Voltage DC'),('HERTZ','Frequency')]:functions=functions.replace(code,label)
            units=m['units']
            for code,label in [('OHM','Ω'),('CEL','°C'),('FAR','°F')]:units=units.replace(code,label)
            self.table.insert('','end',iid=m['path'],values=(m['name'],date,functions,units,duration_text(m['duration']),m['count'],m['source'],m['state']))
        keep=[p for p in selected if self.table.exists(p)]
        if keep:self.table.selection_set(keep)
        self.selection_changed()
    def sort(self,key):
        self.reverse=not self.reverse if key==self.sort_key else False;self.sort_key=key;self.render()
    def selection_changed(self):
        if not hasattr(self,'open_button'):return
        paths=self.table.selection();available=all(Path(p).is_file() for p in paths)
        self.open_button.configure(state='normal' if len(paths)==1 and available and not self.busy else 'disabled')
        self.compare_button.configure(state='normal' if len(paths)==2 and available and not self.busy else 'disabled')
        self.label_button.configure(state='normal' if len(paths)==1 and not self.busy else 'disabled')
        self.remove_button.configure(state='normal' if paths and not self.busy else 'disabled')
        if hasattr(self,'details'):
            text='Ctrl-select two recordings to compare them. Removing an entry does not delete the file.'
            if len(paths)==1:
                m=self.entries[paths[0]];text=m['path']+'\nTime base: '+m['clock']
            elif len(paths)==2:text='A: '+Path(paths[0]).name+'\nB: '+Path(paths[1]).name
            self.details.set(text)
    def open_selected(self):
        paths=self.table.selection()
        if len(paths)!=1 or self.busy:return
        path=paths[0];self.job('open',lambda:(path,load_session(path)))
    def compare(self):
        paths=self.table.selection()
        if len(paths)==2 and not self.busy:ComparisonWindow(self.window,paths=paths)
    def rename(self):
        paths=self.table.selection()
        if len(paths)!=1:return
        item=self.entries[paths[0]]
        label=simpledialog.askstring('Library label','Display name (file remains unchanged):',initialvalue=item['label'] or item['name'],parent=self.window)
        if label is not None:
            try:self.catalog.label(paths[0],label);self.reload()
            except Exception as error:messagebox.showerror('Library',str(error),parent=self.window)
    def remove(self):
        paths=self.table.selection()
        if paths:
            try:self.catalog.remove(paths);self.reload();self.status.set('Entries removed. Files remain on disk; refreshing the folder may add them again.')
            except Exception as error:messagebox.showerror('Library',str(error),parent=self.window)
    def show_issues(self):
        messagebox.showinfo('Skipped files','\n'.join(self.issues[:30]) or 'No errors in the last scan.',parent=self.window)
    def poll(self):
        if self.closed:return
        try:
            while True:
                kind,data,error=self.jobs.get_nowait();self.busy=False
                for b in self.actions:b.configure(state='normal')
                if error:self.status.set('Operation failed: '+error)
                elif kind=='open':
                    path,history=data;HistoryWindow(self.window,history,title='Saved session • '+Path(path).name,live=False)
                    self.status.set('Opened '+Path(path).name)
                else:
                    count,self.issues=data;self.reload();self.status.set(f'Read {count} recordings. In library: {len(self.entries)}. Skipped / errors: {len(self.issues)}.')
                self.selection_changed()
        except queue.Empty:pass
        self.window.after(100,self.poll)
    def close(self):self.closed=True;self.window.destroy()

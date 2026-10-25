# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
# This program comes with NO WARRANTY; see COPYING for license terms.
import json
from datetime import datetime, timezone
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .display import format_reading
from .memory import KINDS, to_history
from .history_gui import HistoryWindow
from .library import remember_recording

MEMORY_LIVE_HINT='Exit memory browsing on the meter and return to LIVE measurement. Then retry in the application.'

BG='#10151d'; CARD='#1a2230'; TEXT='#edf2f7'; MUTED='#9aaac0'

def timestamp_text(value):
    if value is None: return '—'
    try: return datetime.fromtimestamp(value,timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError,OverflowError,OSError): return str(value)

class MemoryWindow:
    def __init__(self,parent,worker):
        self.worker=worker
        self.closed=False; self.busy=False; self.items=[]; self.archive=None; self.identity=''
        self.diagnostics=[]
        self.download_path=None
        self.window=tk.Toplevel(parent,bg=BG)
        self.window.title('Fluke 289 memory • read only')
        self.window.geometry('1150x730'); self.window.minsize(900,600)
        self.window.protocol('WM_DELETE_WINDOW',self.close)
        body=tk.Frame(self.window,bg=BG); body.pack(fill='both',expand=True,padx=20,pady=16)
        tk.Label(body,text='Fluke 289 memory',bg=BG,fg='#f6c744',font=('DejaVu Sans',20,'bold')).pack(anchor='w')
        tk.Label(body,text='Originals remain in the meter. LIVE pauses only during transfer.',bg=BG,fg=MUTED).pack(anchor='w',pady=(4,12))
        tk.Label(body,text=MEMORY_LIVE_HINT,bg=BG,fg='#f6c744',wraplength=850,justify='left').pack(anchor='w',pady=(0,10))
        controls=tk.Frame(body,bg=BG); controls.pack(fill='x')
        self.list_button=ttk.Button(controls,text='List recordings',command=self.list_items)
        self.list_button.pack(side='left')
        self.download_button=ttk.Button(controls,text='Download selected recording',command=self.download,state='disabled')
        self.download_button.pack(side='left',padx=8)
        self.cancel_button=ttk.Button(controls,text='Cancel transfer',command=self.worker.memory_cancel.set,state='disabled')
        self.cancel_button.pack(side='left')
        self.status=tk.StringVar(value='Click “List recordings”. Stop file recording in the application first.')
        tk.Label(body,textvariable=self.status,bg=BG,fg=TEXT,wraplength=1050,justify='left').pack(fill='x',pady=12)
        self.progress=ttk.Progressbar(body,mode='determinate'); self.progress.pack(fill='x',pady=(0,10))
        columns=('kind','index','name','start','end','samples')
        self.table=ttk.Treeview(body,columns=columns,show='headings',height=9)
        for col,label,width in zip(columns,['Type','No.','Name','Start (UTC from Fluke data)','End','Intervals'],[100,45,200,200,180,80]):
            self.table.heading(col,text=label,anchor='w'); self.table.column(col,width=width,anchor='w')
        self.table.pack(fill='both',expand=True)
        self.table.bind('<<TreeviewSelect>>',lambda e:self.update_buttons())
        self.details=tk.Text(body,height=7,bg=CARD,fg=TEXT,wrap='word',relief='flat',padx=10,pady=10)
        self.details.pack(side='bottom',fill='x',pady=10,before=self.table); self.details.configure(state='disabled')
        bottom=tk.Frame(body,bg=BG); bottom.pack(side='bottom',fill='x',before=self.details)
        self.view_button=ttk.Button(bottom,text='Open downloaded data and chart',command=self.view,state='disabled')
        self.view_button.pack(side='left')
        self.save_button=ttk.Button(bottom,text='Save full backup…',command=self.save,state='disabled')
        self.save_button.pack(side='left',padx=8)
        ttk.Button(bottom,text='Save diagnostics…',command=self.save_diagnostics).pack(side='right')

    def update_buttons(self):
        self.list_button.configure(state='disabled' if self.busy else 'normal')
        self.download_button.configure(state='normal' if not self.busy and self.table.selection() else 'disabled')
        self.cancel_button.configure(state='normal' if self.busy else 'disabled')
        for button in [self.view_button,self.save_button]:
            button.configure(state='normal' if self.archive and not self.busy else 'disabled')

    def list_items(self):
        if self.busy: return
        self.busy=True; self.status.set('Listing recordings… checking QSLS and recording headers')
        self.progress['value']=0; self.update_buttons()
        self.worker.memory_request('list')

    def download(self):
        selected=self.table.selection()
        if self.busy or not selected: return
        item=self.items[int(selected[0])]
        name=''.join(c if c.isalnum() or c in '-_' else '_' for c in item['name']).strip('_') or 'recording'
        path=filedialog.asksaveasfilename(parent=self.window,title='Select where to save Fluke data',initialfile=f'fluke289-{name}.json',defaultextension='.json',filetypes=[('Fluke JSON backup','*.json')])
        if not path: return
        self.download_path=path
        self.busy=True; self.status.set('Downloading: '+item['name']+' • file: '+path)
        self.progress['value']=0; self.update_buttons()
        self.worker.memory_request('download',item)

    def event(self,kind,data):
        if self.closed: return
        if kind=='memory_progress':
            done,total=data
            self.progress.configure(maximum=max(1,total),value=done)
            self.status.set(f'Reading: {done} / {total}')
        elif kind=='memory_error':
            self.status.set('Download failed: '+data['message']+'\n'+MEMORY_LIVE_HINT)
            self.diagnostics=data.get('diagnostics',[])
        elif kind=='memory_result':
            self.identity=data['identity']
            if data['operation']=='list':
                self.items=data['result']
                self.table.delete(*self.table.get_children())
                for index,item in enumerate(self.items):
                    self.table.insert('','end',iid=str(index),values=(KINDS[item['kind']][0],item['index']+1,item['name'],timestamp_text(item['start']),timestamp_text(item['end']),item.get('sample_count','—')))
                self.status.set(f'Read {len(self.items)} recordings. Select a recording and click “Download”.' if self.items else 'Memory contains no recordings.')
            else:
                self.archive=data['result']; self.archive['identity']=self.identity
                self.status.set('Downloaded: '+self.archive['header']['name']+' • data remains in application memory until saved')
                h=self.archive['header']
                text=f"{h['name']} • {KINDS[h['kind']][0]}\n{h['primary']} / {h['secondary']}\n"
                text+='\n'.join(r['id']+': '+format_reading(r) for r in h['readings'])
                if h['kind']=='recording': text+='\nDownloaded intervals: '+str(len(self.archive['intervals']))+'; interval average remains a raw accumulator (not interpreted without validation).'
                if self.download_path:
                    path=self.download_path; self.download_path=None
                    self.write_archive(path)
                self.details.configure(state='normal'); self.details.delete('1.0','end'); self.details.insert('1.0',text); self.details.configure(state='disabled')
        elif kind=='memory_busy' and not data:
            self.busy=False; self.update_buttons()

    def view(self):
        if not self.archive: return
        history=to_history(self.archive,self.identity)
        if not history.samples:
            messagebox.showinfo('No samples','This recording has no readings with a valid time base.',parent=self.window)
            return
        HistoryWindow(self.window,history,title='Fluke memory • '+self.archive['header']['name'],live=False)

    def save(self):
        if not self.archive: return
        path=filedialog.asksaveasfilename(parent=self.window,title='Save full memory backup',initialfile='fluke289-memory.json',defaultextension='.json',filetypes=[('Fluke JSON backup','*.json')])
        if path: self.write_archive(path)

    def write_archive(self,path):
        try:
            payload=json.dumps(self.archive,ensure_ascii=False,indent=2,allow_nan=False)
            with open(path,'w',encoding='utf-8') as f: f.write(payload)
        except (OSError,ValueError) as e:
            self.status.set('File not saved. Data remains in memory — use “Save full backup…”.')
            messagebox.showerror('Save backup',str(e),parent=self.window)
            return False
        remember_recording(path)
        self.status.set('Full backup saved: '+str(path))
        return True

    def save_diagnostics(self):
        path=filedialog.asksaveasfilename(parent=self.window,title='Save memory diagnostics',defaultextension='.json')
        if path:
            try:
                with open(path,'w',encoding='utf-8') as f: json.dump({'diagnostics':self.diagnostics},f,ensure_ascii=False,indent=2)
            except OSError as e: messagebox.showerror('Diagnostics',str(e),parent=self.window)

    def close(self):
        if self.busy: self.worker.memory_cancel.set()
        self.closed=True; self.window.destroy()

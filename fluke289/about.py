# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
# This program comes with NO WARRANTY; see COPYING for license terms.
"""Offline release information, documentation and licensing."""
import json
import platform
import sys
import tkinter as tk
from tkinter import ttk
from importlib import metadata, resources
from . import __version__

AUTHOR_CREDIT = 'Software Development, Design & Testing by Piotr'
COOPERATION = 'Developed with assistance from OpenAI Codex'
LICENSE_ID = 'GPL-3.0-or-later'


def read_document(name):
    return resources.files('fluke289').joinpath('data', name).read_text(encoding='utf-8')


def build_information():
    try:
        return json.loads(read_document('build_info.json'))
    except (FileNotFoundError, ValueError):
        return {'version': __version__, 'build_id': 'development — no manifest',
                'date': 'unknown', 'tests': {'status': 'not run for this build'}}


def info_text():
    build = build_information()
    tests = build.get('tests', {})
    try: serial_version = metadata.version('pyserial')
    except metadata.PackageNotFoundError: serial_version = 'none'
    return '\n'.join([
        'Fluke 289 Live Studio',
        f'Version: {__version__}',
        f'Build: {build["build_id"]}',
        f'Release date: {build["date"]}',
        f'Source SHA-256: {build.get("source_sha256", "none")}',
        '', AUTHOR_CREDIT, COOPERATION,
        'Copyright (C) 2026 Piotr',
        'License: GNU GPL v3 or later ('+LICENSE_ID+')',
        'You may use, study, modify and redistribute under the GPL.',
        'Provided WITHOUT WARRANTY; see the License tab for full terms.',
        '',
        f'Build tests: {tests.get("count", "—")} • {tests.get("status", "no data")}',
        'Test environment: '+build.get('test_environment', 'unknown'),
        'Hardware acceptance: selected features confirmed by Piotr on Fluke 289 V1.41.',
        'See the Validation tab for scope and limitations.',
        '',
        'Current runtime environment:',
        'Python '+sys.version.split()[0]+' • '+platform.system()+' '+platform.release(),
        'Tcl/Tk '+str(tk.TclVersion)+' / '+str(tk.TkVersion)+' • pySerial '+serial_version,
        '',
        'Independent project. Not an official Fluke product or part of the GNU Project.',
        'Project: https://github.com/chudobapiotr5/fluke289-live-studio-en',
        'Do not use this application to establish the absence of hazardous voltage.',
    ])


class AboutWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent, bg='#10151d')
        self.window.title('About • Fluke 289 Live Studio')
        self.window.geometry('1040x760')
        self.window.minsize(800, 560)
        style = ttk.Style(self.window)
        style.configure('About.TNotebook', background='#10151d', borderwidth=0)
        style.configure('About.TNotebook.Tab', padding=(10, 8), background='#253144', foreground='#edf2f7')
        style.map('About.TNotebook.Tab', background=[('selected', '#f6c744')], foreground=[('selected', '#10151d')])
        heading = tk.Frame(self.window, bg='#10151d')
        heading.pack(fill='x', padx=20, pady=16)
        tk.Label(heading, text='Fluke 289 Live Studio', bg='#10151d', fg='#f6c744',
                 font=('DejaVu Sans', 20, 'bold')).pack(anchor='w')
        tk.Label(heading, text=AUTHOR_CREDIT+'  •  '+COOPERATION, bg='#10151d', fg='#9aaac0',
                 wraplength=980, justify='left').pack(anchor='w', pady=(6, 0))
        book = ttk.Notebook(self.window, style='About.TNotebook')
        book.pack(fill='both', expand=True, padx=20)
        documents = [
            ('Information', None), ('User guide', 'USER_GUIDE.md'),
            ('Documentation', 'PROTOCOL.md'), ('Tests', 'TESTS.txt'), ('GNU GPL license', 'COPYING')]
        for title, filename in documents:
            pane = tk.Frame(book, bg='#1a2230')
            book.add(pane, text=title)
            choice = None
            if title == 'Documentation':
                names = {
                    'Fluke memory (experimental)': 'MEMORY.md', 'Protocol and limitations': 'PROTOCOL.md', 'File formats': 'FORMATS.md',
                    'Diagnostics': 'DIAGNOSTICS.md', 'Validation and acceptance': 'VALIDATION.md',
                    'Development and builds': 'DEVELOPMENT.md', 'Authors': 'AUTHORS.md',
                    'Changelog': 'CHANGELOG.md', 'Third-party components and sources': 'THIRD_PARTY.md'}
                choice = ttk.Combobox(pane, values=list(names), state='readonly')
                choice.current(0)
                choice.pack(fill='x', padx=16, pady=10)
            content_pane = tk.Frame(pane, bg='#1a2230')
            content_pane.pack(fill='both', expand=True)
            scroll = ttk.Scrollbar(content_pane, orient='vertical')
            scroll.pack(side='right', fill='y')
            text = tk.Text(content_pane, bg='#1a2230', fg='#edf2f7', insertbackground='#edf2f7',
                           relief='flat', wrap='word', padx=18, pady=16,
                           font=('DejaVu Sans', 10), yscrollcommand=scroll.set)
            text.pack(fill='both', expand=True)
            scroll.configure(command=text.yview)
            def set_content(filename, widget=text):
                try: content = info_text() if filename is None else read_document(filename)
                except FileNotFoundError: content = 'Document missing from this package: '+filename
                widget.configure(state='normal')
                widget.delete('1.0', 'end')
                widget.insert('1.0', content)
                widget.configure(state='disabled')
                widget.yview_moveto(0)
            set_content(filename)
            if choice:
                choice.bind('<<ComboboxSelected>>', lambda event, picker=choice, mapping=names, show=set_content: show(mapping[picker.get()]))
        buttons = tk.Frame(self.window, bg='#10151d')
        buttons.pack(fill='x', padx=20, pady=14)
        ttk.Button(buttons, text='Copy information', command=self.copy_info).pack(side='left')
        ttk.Button(buttons, text='Close', command=self.window.destroy).pack(side='right')

    def copy_info(self):
        self.window.clipboard_clear()
        self.window.clipboard_append(info_text())

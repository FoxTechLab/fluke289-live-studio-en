# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
"""Ensure the international release ships usable English offline resources."""
import re
import unittest
from pathlib import Path
from fluke289.about import info_text, read_document
from fluke289.memory_gui import MEMORY_LIVE_HINT

class EnglishReleaseTests(unittest.TestCase):
    def test_english_runtime_and_offline_guides(self):
        self.assertIn('Version:', info_text())
        self.assertIn('WITHOUT WARRANTY', info_text())
        self.assertIn('Exit memory browsing', MEMORY_LIVE_HINT)
        for name in ['README.md', 'USER_GUIDE.md', 'PROTOCOL.md', 'FORMATS.md',
                     'MEMORY.md', 'DIAGNOSTICS.md', 'VALIDATION.md', 'DEVELOPMENT.md']:
            text = read_document(name)
            self.assertNotRegex(text, r'[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', name)
        self.assertIn('Interface language: English', read_document('README.md'))

    def test_user_facing_source_has_no_polish_release_labels(self):
        package = Path(__file__).resolve().parents[1] / 'fluke289'
        for path in package.glob('*.py'):
            text = path.read_text()
            self.assertNotRegex(text, r'[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', str(path))
            self.assertNotRegex(text, r'\b(?:Wybierz|Zapisz|Kopiuj|Zamknij|Brakuje|Odczyt|Pobierz|zakres)\b', str(path))

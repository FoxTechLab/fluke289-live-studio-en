# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
# This program comes with NO WARRANTY; see COPYING for license terms.
import unittest
from fluke289 import __version__
from fluke289.about import AUTHOR_CREDIT, info_text, read_document

class ReleaseDocumentationTests(unittest.TestCase):
    def test_offline_license_and_all_documents_exist(self):
        license_text=read_document('COPYING')
        self.assertIn('GNU GENERAL PUBLIC LICENSE',license_text)
        self.assertIn('Version 3, 29 June 2007',license_text)
        self.assertIn('END OF TERMS AND CONDITIONS',license_text)
        self.assertGreater(len(license_text),30000)
        for name in ['USER_GUIDE.md','PROTOCOL.md','FORMATS.md','DIAGNOSTICS.md',
                     'VALIDATION.md','DEVELOPMENT.md','AUTHORS.md','CHANGELOG.md','THIRD_PARTY.md','TESTS.txt']:
            self.assertTrue(read_document(name).strip(),name)

    def test_author_version_credit_and_no_fake_repo(self):
        text=info_text()
        self.assertIn('Software Development, Design & Testing by Piotr',text)
        self.assertIn('OpenAI Codex',text)
        self.assertIn(__version__,text)
        self.assertIn('GPL-3.0-or-later',text)
        self.assertIn('WITHOUT WARRANTY',text)
        self.assertNotIn('/home/',text)
        self.assertNotRegex(text,r'FLUKE 289,[^\n]*,\d{6,}')
        self.assertEqual(AUTHOR_CREDIT,'Software Development, Design & Testing by Piotr')

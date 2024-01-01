# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
#

# SPDX-License-Identifier: GPL-3.0-or-later
import os
import sys
import kbm
from kbm import SettingsParser
log = kbm.log.getChild(__name__)

class ArchiveManager:
    # I'm pretty sure I only want each instance to have access to its own settings
    def __init__(self, arc_type, is_local=True):
        self.arc_type = arc_type
        self.is_local = is_local
        self.name = 'ArchiveManager'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
    def FindArchive(how_recent=0):
        self.how_recent = how_recent
        with SettingsParser(self.arc_type) as s:
            try:
                self.save_dir = os.join(kbm.backupdir, s[self.arc_type])
            except KeyError as e:
                log.exception('ArchiveManager object reports invalid archive type specified.')
                sys.exit()
            self.recents = s['recent']
        


class Archiver(ArcManager):
    def __init__(self):
        super().__init__(arc_type, is_local)
        self.name = 'Archiver'

    def __repr__(self):
        return f"Archiver('{self.arc_type}', 'is_local={self.is_local}')"


class Unarchiver(ArcManager):
    def __init__(self):
        super().__init__(archive_type, is_local)
        self.name = 'Unarchiver'
        self.archive_type = archive_type
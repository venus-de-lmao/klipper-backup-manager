# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
#

# SPDX-License-Identifier: GPL-3.0-or-later
import os
import sys
import kbm
import tarfile
from kbm import SettingsParser
log = kbm.log.getChild(__name__)

class ArchiveManager:
    # I'm pretty sure I only want each instance to have access to its own settings
    def __init__(self, arc_type, is_local=True, how_recent=0):
        self.arc_type = arc_type
        self.is_local = is_local
        self.how_recent = how_recent
        self.name = 'ArchiveManager'
        with SettingsParser(self.arc_type) as s:
            if not self.arc_type in s:
                log.exception('SettingsParser reports no valid archive type of type \'%s\'', self.arc_type)
                raise
            self.arc_cfg = s[self.arc_type]
        self.recents = self.arc_cfg['recents']
        self.file_path = os.path.join(kbm.kbmlocal, self.recents[self.how_recent]['location'])
        if not tarfile.is_tarfile(self.file_path) or not os.path.exists(self.file_path):
            log.exception('Error validating file %s', self.file_path)
            raise FileNotFoundError('File does not exist or is not a tar archive.')

    def __enter__(self):
        return tarfile.open(self.file_path, 'r')
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        tarfile.close()



class Archiver(ArcManager):
    def __init__(self, arc_type, cmode, is_local, how_recent):
        super().__init__(arc_type, is_local, how_recent)
        self.name = 'Archiver'
        self.cmode = cmode
    def __enter__(self):
        return tarfile.open(self.file_path, f'w:{self.cmode}')

    def __repr__(self):
        return f"Archiver('{self.arc_type}', 'is_local={self.is_local}')"


class Unarchiver(ArcManager):
    def __init__(self):
        super().__init__(archive_type, is_local)
        self.name = 'Unarchiver'
        self.archive_type = archive_type
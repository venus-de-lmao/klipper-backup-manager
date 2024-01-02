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
    def __init__(self, arc_type, how_recent):
        self.arc_type = arc_type
        self.how_recent = how_recent
        self.name = 'ArchiveManager'
        with SettingsParser(self.arc_type) as s:
            if not self.arc_type in s:
                log.exception('SettingsParser reports no valid archive type of type \'%s\'', self.arc_type)
                raise
            self.arc_cfg = s[self.arc_type]
        self.recents = self.arc_cfg['recents']
        self.archive_path = os.path.join(kbm.kbmlocal, self.recents[self.how_recent]['location'])
    def __enter__(self):
        return self.file_path
    def __exit__(self, exc_type, exc_value, exc_traceback):
       return True

class Archiver(ArcManager):
    def __init__(self, arc_type, how_recent=0, cmode='xz'):

        super().__init__(arc_type, how_recent)
        self.name = 'Archiver'
        self.cmode = cmode
    def __enter__(self):
        # Generate a time-stamped filename in the format of gcode_2023-10-31_110345.tar.xz
        self.stampedfilename = f'{self.arc_type}_{kbm.file_timestamp()}.tar.{self.cmode}'
        self.file_path = os.path.join(self.archive_path, self.stampedfilename)
        self.file = tarfile.open(self.file_path, f'w:{self.cmode}')
        return self.file
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if type(exc_type) == NoneType:
            log.debug('Successfully wrote to file %s', self.file.name)
            log.debug('Updating recents list.')

        log.debug('Closing file %s', self.file.name)
        self.file.close()
        log.debug('Exiting Archiver context manager.')
        log.debug('Exception type:: %s', exc_type)
        log.debug('Value: %s', exc_value)
        log.debug('Traceback: %s', exc_traceback)
        
class Unarchiver(ArcManager):
    def __init__(self, arc_type, how_recent=0):
        super().__init__(arc_type, how_recent)
        self.name = 'Unarchiver'
    def __enter__(self):
        self.file = tarfile.open(self.file_path, 'r')
        return self.file
    def __exit__(self, exc_type, exc_value, exc_traceback):
        log.debug('Closing file %s', self.file.name)
        self.file.close() # assuming nothing has gone wrong up to this point
        log.debug('Exiting Unarchiver context manager.')
        log.debug('Exception type:: %s', exc_type)
        log.debug('Value: %s', exc_value)
        log.debug('Traceback: %s', exc_traceback)

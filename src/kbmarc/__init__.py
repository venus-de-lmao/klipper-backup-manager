# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
#

# SPDX-License-Identifier: GPL-3.0-or-later
import sys
import os
import tarfile
from pathlib import Path
import kbm

log = kbm.log.getChild(__name__)

pdata = os.path.expanduser(kbm.pdata)
phome = Path(pdata).parent.absolute()
class ArchiveManager:
    # I'm pretty sure I only want each instance to have access to its own settings
    def __init__(self, arc_type, how_recent):
        self.arc_type = arc_type
        self.how_recent = how_recent
        self.name = 'ArchiveManager'
        with kbm.SettingsParser(self.arc_type) as s:
           self.arc_cfg = s.pull_entry(self.arc_type)
        if not self.arc_cfg:
            log.exception('Entry \'%s\' not found in settings.', self.arc_type)
            sys.exit()
        self.file_path = os.path.join(kbm.backupdir, self.arc_cfg['recent'][self.how_recent])
    def __enter__(self):
        return self.file_path
    def __exit__(self, exc_type, exc_value, exc_traceback):
       return True

class Archiver(ArchiveManager):
    def __init__(self, arc_type, how_recent=0, cmode='xz'):
        os.chdir(Path(pdata).parent.absolute())
        super().__init__(arc_type, how_recent)
        self.name = 'Archiver'
        self.cmode = cmode
    def __enter__(self):
        # Generate a time-stamped filename in the format of gcode_2023-10-31_110345.tar.xz
        self.stampedfilename = f'{self.arc_type}_{kbm.file_timestamp()}.tar.{self.cmode}'
        self.file_path = os.path.join(kbm.backupdir, self.stampedfilename)
        self.file = tarfile.open(self.file_path, f'w:{self.cmode}')
        return self.file
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if type(exc_type) == NoneType:
            log.debug('Successfully wrote to file %s', self.file.name)
            log.debug('Updating recents list.')

        log.debug('Closing file %s', self.file.name)
        self.file.close()
        log.debug('Exiting Archiver context manager.')
class Unarchiver(ArchiveManager):
    def __init__(self, arc_type, how_recent=0):
        super().__init__(arc_type, how_recent)
        self.name = 'Unarchiver'
    def __enter__(self):
        try:
            self.file_path = os.path.join(kbm.backupdir, kbm.SettingsParser('default').pull_entry(self.arc_type)['recent'][self.how_recent])
        except:
            log.exception('Well, that didn\'t work.', exc_info=True)
        self.file = tarfile.open(self.file_path, 'r')
        return self.file
    def __exit__(self, exc_type, exc_value, exc_traceback):
        log.debug('Closing file %s', self.file.name)
        self.file.close() # assuming nothing has gone wrong up to this point
        log.debug('Exiting Unarchiver context manager.')

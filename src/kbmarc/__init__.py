# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
#

# SPDX-License-Identifier: GPL-3.0-or-later
import os
import sys
import kbm_
from kbm_ import SettingsParser
log = kbm_.log.getChild(__name__)

class ArcManager:
    # I'm pretty sure I only want each instance to have access to its own settings
    def __init__(self, archive_type, is_local=True):
        self.archive_type = archive_type
        self.is_local = is_local
        

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
    def FindArchive():
        with SettingsParser(self.archive_type) as s:
            if self.is_local:
                print("Looking for local archive of type %s" % self.archive_type)        


class Archiver(ArcManager):
    def __init__(self, archive_type):
        super().__init__(profile_name)
        self.archive_type = archive_type

    def __repr__(self):
        return f"Archiver('{self.profile_name}', '{self.archive_type}')"


class Unarchiver(ArcManager):
    def __init__(self, archive_type, is_local):
        super().__init__(archive_type, is_local)
        self.archive_type = archive_type

`

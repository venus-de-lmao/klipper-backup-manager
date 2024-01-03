import os
import pathlib
import tarfile

from progressbar import progressbar

import kbm
import kbm.settings

exc_exts = ['.bak','.bkp']
class Archive:
    def __init__(self, tag):
        self.date = kbm.file_timestamp() # generate timestamp when the object is instantiated
        self.tag = tag
        self.wdir = pathlib.Path(os.path.expanduser(kbm.settings.pull_entry('printer_data'))).parent.resolve()
        os.chdir(self.wdir)
    def create_file(self, cmode='xz'):
        self.cmode = cmode
        self.target_dir = os.join('printer_data', self.tag)
        self.filename = f'{self.tag}_backup_{self.date}.tar.{self.cmode}'
        self.new_archive = os.path.join(kbm.backupdir, self.filename)
        with tarfile.open(self.new_archive, f'w:{self.cmode}') as file:
            targets = [p for p in pathlib.Pat(self.target_dir).rglob('*') if p.suffix not in exc_exts]
            tl = list(targets)
            for x in progressbar(range(len(tl)), redirect_stdout=True):
                file.add(str(tl[x]))
                print(str(tl[x]))


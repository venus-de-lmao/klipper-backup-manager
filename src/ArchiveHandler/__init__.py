import os
import pathlib
import tarfile

from progressbar import progressbar

import KBM

exc_exts = ['.bak','.bkp']
class Archive:
    def __init__(self, tag):
        self.date = kbm.file_timestamp() # generate timestamp when the object is instantiated
        self.wdir = pathlib.Path(os.path.expanduser(kbm.settings.pull_entry('printer_data'))).parent.resolve()
        os.chdir(wdir)
    def create_file(self, cmode='xz'):
        self.cmode = cmode
        self.target_dir = os.join('printer_data', tag)
        self.filename = f'{self.tag}_backup_{self.date}.tar.{self.cmode}'
        self.new_archive = os.path.join(kbm.backupdir, self.filename)
        with tarfile.open(self.new_archive, f'w:{self.cmode}') as file:
            dirlist = list(pathlib.Path(self.target_dir).rglob("*"))
            targets = [p for p in pathlib.Path('printer_data').rglob('*') if p.suffix not in exc_exts]
            tl = list(targets)
            for x in progressbar(range(len(tl)), redirect_stdout=True):
                file.add(str(tl[x]))
                print(str(tl[x]))


import os
import pathlib
import tarfile

from progressbar import progressbar

import kbm
import kbm.settings

exc_exts = [".bak", ".bkp"]

log = kbm.log.getChild(__name__)
class Archive:
    def __init__(self, tag):
        self.date = kbm.file_timestamp()  # generate timestamp when the object is instantiated
        self.tag = tag
        self.wdir = pathlib.Path(os.path.expanduser(kbm.settings.pull_entry("printer_data"))).parent.resolve()
        os.chdir(self.wdir)

    def create_file(self, cmode="xz"):
        os.chdir(self.wdir)
        self.cmode = cmode if cmode in ["xz", "bz2", "gz"] else "xz"
        self.target_dir = os.join("printer_data", self.tag)
        self.filename = f"{self.tag}_backup_{self.date}.tar.{self.cmode}"
        self.new_archive = os.path.join(kbm.backupdir, self.filename)
        with tarfile.open(self.new_archive, f"w:{self.cmode}") as file:
            targets = [p for p in pathlib.Path(self.target_dir).rglob("*") if p.suffix not in exc_exts]
            tl = list(targets)
            for x in progressbar(range(len(tl)), redirect_stdout=True):
                fname_str = str(tl[x])
                file.add(fname_str)
                log.info('Archived %s', fname_str)
                
    def extract_file(self, archive_file):
        os.chdir(self.wdir)
        with tarfile.open(archive_file) as file:
            for x in (progressbar(range(len(m)), redirect_stdout=True)):
                x.extract()
                log.info('Extracted %s', x.name)
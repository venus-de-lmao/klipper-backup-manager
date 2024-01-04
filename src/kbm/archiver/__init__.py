import logging
import os
import pathlib
import sys
import tarfile

from progressbar import progressbar

import kbm

exc_exts = [".bak", ".bkp"]
class Archive:
    def __init__(self, tag, pdata='~/printer_data'):
        self.date = kbm.file_timestamp()  # generate timestamp when the object is instantiated
        self.tag = tag
        self.wdir = pathlib.Path(os.path.expanduser(pdata)).parent.resolve()
        self.log = logging.getLogger('kbm.Archive')
        os.chdir(self.wdir)

    def create_file(self, cmode="xz"):
        os.chdir(self.wdir)
        self.cmode = cmode if cmode in ["xz", "bz2", "gz"] else "xz"
        self.target_dir = os.path.join("printer_data", self.tag)
        if not os.path.isdir(self.target_dir):
            self.log.warning('Target does not exist or is not a directory. Exiting.')
            sys.exit()
        self.filename = f"{self.tag}_backup_{self.date}.tar.{self.cmode}"
        self.new_archive = os.path.join(kbm.backupdir, self.filename)
        with tarfile.open(self.new_archive, f"w:{self.cmode}") as file:
            targets = [p for p in pathlib.Path(self.target_dir).rglob("*") if p.suffix not in exc_exts]
            tl = list(targets)
            tgtl = len(tl)
            for x in progressbar(range(tgtl), redirect_stdout=True):
                file.add(tl[x])
                # print(tl[x])

    def extract_file(self, archive_file):
        os.chdir(self.wdir)
        with tarfile.open(archive_file) as file:
            m = file.list()
            for x in (progressbar(range(len(m)), redirect_stdout=True)):
                x.extract()

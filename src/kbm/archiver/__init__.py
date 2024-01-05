import os, sys
import pathlib
import tarfile
import kbm
import logging
from time import sleep
from progressbar import progressbar
exc_exts = [".bak", ".bkp"]
mode_names = {'xz': 'LZMA', 'bz2': 'BZIP2', 'gz': 'GZIP'}
class Archive:
    def __init__(self, tag, pdata='~/printer_data'):
        self.date = kbm.file_timestamp()  # generate timestamp when the object is instantiated
        self.tag = tag
        self.wdir = pathlib.Path(os.path.expanduser(pdata)).parent.resolve()
        self.log = logging.getLogger('kbm.Archive')
        self.log.debug('Archive object initialized.')
        os.chdir(self.wdir)

    def create_file(self, cmode="xz"):
        os.chdir(self.wdir)
        self.cmode = cmode if cmode in ["xz", "bz2", "gz"] else "xz"
        self.log.debug("Compression mode: %s", mode_names[self.cmode])
        self.target_dir = os.path.join("printer_data", self.tag)
        if not os.path.isdir(self.target_dir):
            self.log.warning('Target does not exist or is not a directory. Exiting.')
            sys.exit()
        self.filename = f"{self.tag}_backup_{self.date}.tar.{self.cmode}"
        self.new_archive = os.path.join(kbm.backupdir, self.filename)
        self.log.debug("Creating new archive: %s", self.new_archive)

        # I really don't like how I've implemented this, but that's a project for another day 
        with tarfile.open(self.new_archive, f"w:{self.cmode}") as file:
            targets = [p for p in pathlib.Path(self.target_dir).rglob("*") if p.suffix not in exc_exts]
            tl = list(targets)
            tgtl = len(tl)
            for x in progressbar(range(tgtl), redirect_stdout=True):
                file.add(tl[x])
                print(tl[x])
            global settings
            settings.add_recent(self.tag, self.new_archive)
            settings.write()

    def extract_file(self, archive_file):
        os.chdir(self.wdir)
        with tarfile.open(archive_file) as file:
            m = file.list()
            for x in (progressbar(range(len(m)), redirect_stdout=True)):
                x.extract()

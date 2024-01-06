import logging
import os
import pathlib
import kbm
from tqdm import tqdm
import tarfile
import logging
import sys

exc_exts = [".bak", ".bkp"]
mode_names = {'xz': 'LZMA', 'bz2': 'BZIP2', 'gz': 'GZIP'}
wdir = os.path.expanduser('~')
class Archive:
    def __init__(self, tag, pdata='~/printer_data', cmode='xz'):
        self.cmode = cmode if cmode in ["xz", "bz2", "gz"] else "xz"
        self.date = kbm.file_timestamp()  # generate timestamp when the object is instantiated
        self.tag = tag
        self.wdir = pathlib.Path(os.path.expanduser(pdata)).parent.resolve()
        global wdir
        wdir = self.wdir
        self.log = logging.getLogger('kbm.Archive')
        self.log.debug('Archive object initialized.')
        os.chdir(self.wdir)
        self.target_dir = os.path.join("printer_data", self.tag)
        if not os.path.isdir(self.target_dir):
            self.log.warning('Target does not exist or is not a directory. Exiting.')
            sys.exit()
        self.targets = [p for p in pathlib.Path(self.target_dir).rglob("*") if p.suffix not in exc_exts]
        self.filename = f"{self.tag}_backup_{self.date}.tar.{self.cmode}"
        self.new_archive = os.path.join(kbm.backupdir, self.filename)
        self.log.debug("Creating new archive: %s", self.new_archive)
    def size_up(self):
        self.dir_size = 0
        os.chdir(self.wdir)
        for path, dirs, files in os.walk(self.target_dir):
            for f in files:
                fp = os.path.join(path, f)
                fpsize = os.path.getsize(fp)
                self.dir_size += fpsize
                yield [fp, fpsize]
    def create_file(self):
        os.chdir(self.wdir)
        self.log.debug("Compression mode: %s", mode_names[self.cmode])
        # I really don't like how I've implemented this, but that's a project for another day 
        with tarfile.open(self.new_archive, f"w:{self.cmode}") as file:
            target_files = self.size_up()
            tl = list(target_files)
            bar = tqdm(total=self.dir_size, unit='B', unit_scale=True, unit_divisor=1024)
            for x in tl:
                bar.write(str(x[0]))
                file.add(str(x[0]))
                bar.update(x[1])

def extract_file(archive_file):
    os.chdir(wdir)
    with tarfile.open(archive_file) as file:
        dir_size = 0
        for f in file.getmembers():
            dir_size += f.size
        pbar = tqdm(total=dir_size, unit='B', unit_scale=True, unit_divisor=1024)
        for m in file.getmembers():
            pbar.write(m.name)
            file.extract(m)
            pbar.update(m.size)
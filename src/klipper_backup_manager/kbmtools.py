import tarfile
import os
import sys
from datetime import datetime as dt
exclude_exts=['.tmp','.ignore','.swp']

def timestamp(file=False):
    if file:
        return dt.now().strftime("%Y-%m-%d_%H%M%S")
    else:
        return dt.now().strftime("%Y/%m/%d %H:%M:%S")


def make_tarball(working_dir, filename, targets):
    if os.getcwd() != working_dir: os.chdir(working_dir)
    filename = filename+f'_{timestamp(file=True)}.tar.xz'
    try:
        tar = tarfile.open(filename, 'w:xz')
    except Exception as e:
        print(f'Error opening {tar} in write mode. Aborting.')
        print(e)
        sys.exit()
    for t in targets:
        tar.add(t, filter=lambda tarinfo: None if os.path.splitext(tarinfo.name[1] in exclude_exts else tarinfo)
        print(t)
    tar.close()

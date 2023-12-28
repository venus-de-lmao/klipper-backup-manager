import tarfile
import os
import sys
from datetime import datetime as dt

# Pass file as True to produce a timestamp suitable for a filename. Otherwise returns a plain date/time for logging.
def timestamp(file=False):
    if file:
        return dt.now().strftime("%Y-%m-%d_%H%M%S")
    else:
        return dt.now().strftime("%Y/%m/%d %H:%M:%S")

def log_line(file, out_txt):
    log_msg = timestamp()+' '+out
    try:
        with open(file, 'a') as l:
            l.write('\n')
            l.write(log_msg)
    except PermissionError:
        print(f'Permission denied accessing {log_file}. Logging disabled.')
        logging = False
        return None
    except Exception as e:
        print(f'Unexpected error writing to {log_file}.\n{e}\nLogging disabled.')
        logging = False
        return None


# Pass 'tag' to this function to generate a time/datestamped archive file
# in the format tag_YYYY-mm-dd_hhmmss.tar.xz
def make_tarball(working_dir, tag, targets):
    if os.getcwd() != working_dir: os.chdir(working_dir)
    filename = tag+f'_{timestamp(file=True)}.tar.xz'
    try:
        tar = tarfile.open(filename, 'w:xz')
    except Exception as e:
        print(f'Error opening {tar} in write mode. Aborting.')
        print(e)
        sys.exit()
    for t in targets:
        if not os.path.exists(t):
            print(f'{t} not found, skipping...')
        tar.add(t, filter=lambda tarinfo: None if os.path.splitext(tarinfo.name[1]) in exclude_exts else tarinfo)
    tar.list()
    tar.close()

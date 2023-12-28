import argparse
import tarfile
import os
import sys
from subprocess import run as run_cmd
import toml
from datetime import datetime as dt
homedir = os.path.expanduser('~')
log_dir=f'{homedir}/kbm/logs'
backup_dir=f'{homedir}/kbm/backups'
config='klipper-backup-manager/kbm.toml'
exclude_exts=['.tmp','.ignore','.swp']
verbose = False
logging = False

# Pass file as True to produce a timestamp suitable for a filename. Otherwise returns a plain date/time for logging.

def verboseprint(*args, **kwargs):
    if verbose: print(*args, **kwargs)
    if logging: log_line(log_file, *args)

def log_line(*args): 
    log_msg = ' '.join(args)
    stamped = dt.now().strftime('%Y/%m/%d %H:%M:%S')+' '+log_msg
    try:
        with open(file, 'a') as l:
            l.write('\n')
            l.write(stamped)
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
# Standard use for 
def make_tarball(tag, targets, working_dir=homedir):
    if os.getcwd() != working_dir: os.chdir(working_dir)
    filename = tag+f'_{timestamp(file=True)}.tar.xz'
    try:
        tar = tarfile.open(filename, 'w:xz')
    except Exception as e:
        verboseprint(f'Error opening {filename} in write mode. Aborting.')
        verboseprint(e)
        sys.exit()
    for t in targets:
        try:
            tar.add(t, filter=lambda tarinfo: None if os.path.splitext(tarinfo.name[1]) in exclude_exts else tarinfo)
        except FileNotFoundError:
            verboseprint(f'{t} not found.')
        except Exception as e:
            verboseprint(e)
            sys.exit()
    verboseprint(f'Backed up the following to {filename}:')
    tar.list()
    tar.close()
    return filename

parser = argparse.ArgumentParser(
        prog='Klipper Backup Manager'
        description='Create, restore, and manage backups of 3D printer files on a Klipper instance.'
        epilog='')

# I might add more options to this in the future.
parser.add_argument('-s', '--save', action='store',
        choices=['config','gcode','all'], nargs=1,
        dest='is_backup',
        required=True,
        metavar='TARGET',
        help='Specify which targets to back up.')

parser.add_argument('-v', '--verbose', action='store_true',
        dest='is_verbose',
        required=False,
        default=False,
        help='Enable verbose mode. Prints all output to stdout.')

parser.add_argument('-l', '--log', action='store_true',
        dest='is_logging',
        required=False,
        default=False,
        help=f'Enable logging. Writes all output to a text file in {log_dir}. This is off by default. Works with or without verbose mode.')


def do_backup(file, backup_type='rclone'):
    if backup_type == 'rclone':
        rclone_cmd = ['rclone', 'copy', file, 'gdrive:/kbm_backups']
        run_cmd(rclone_cmd)
        return True
#    elif backup_type =='ssh':
        # I'm still figuring out how to handle this

if __name__ == '__main__':
    run_args=parser.parse_args()
    if os.getcwd() != homedir: os.chdir(homedir)
    log_file = log_dir+kbmlib.timestamp().strftime('kbm_%Y-%m-%d_%H%M%S.log') if logging else None
    if run_args['is_backup'] == 'config':
        
    elif run_args['is_backup'] == 'gcode':
        # do gcode backup
    else:
        do both
    verbose = run_args['is_verbose']
    logging = run_args['is_logging']

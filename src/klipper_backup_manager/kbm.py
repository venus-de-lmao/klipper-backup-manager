#!/usr/bin/env python3

import argparse
import tarfile
import os
import sys
from subprocess import run as run_cmd
import shutil
import click
from datetime import datetime as dt
from io import StringIO 

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

homedir = os.path.expanduser('~')
kbm_dir = f'{homedir}/klipper-backup-manager'
log_dir=f'{kbm_dir}/logs'
log_file='blank.log'
backup_dir=f'{kbm_dir}/backups'
 
@click.command()
@click.option('--config', '-c', default=False, is_flag=True, help='back up Klipper config files')
@click.option('--gcode', '-g', default=False, is_flag=True, help='back up gcodes')
@click.option('--verbose', '-v', default=False, is_flag=True, help='enable verbose mode')
@click.option('--log', '-l', default=False, is_flag=True, help='enable logging')
def main(config, gcode, verbose, log):
    global do_cfg
    global do_gco
    global is_logging
    global is_verbose
    global log_file
    do_cfg = config;
    do_gco = gcode;
    is_logging = log
    is_verbose = verbose
    if os.getcwd() != homedir: os.chdir(homedir)
    if is_logging: 
        log_file = dt.now().strftime('kbm_%Y-%m-%d_%H%M%S.log')
        if not os.path.isdir(log_dir):
            try:
                os.mkdir(log_dir)
            except Exception as e:
                verboseprint('Error creating log directory.')
                verboseprint(e)
                sys.exit()

        print(log_file)
    do_backup(do_cfg, do_gco)

def verboseprint(*args, **kwargs):
    if is_verbose: print(*args, **kwargs)
    if is_logging: log_line(*args)

def log_line(*args):
    global is_logging
    log_msg = ' '.join(args)
    stamped = dt.now().strftime('%Y/%m/%d %H:%M:%S')+' '+log_msg
    try:
        with open(f'{log_dir}/{log_file}', 'a') as l:
            l.write('\n')
            l.write(stamped)
    except PermissionError:
        print(f'Permission denied accessing {log_file}. Logging disabled.')
        is_logging = False
        return None
    except Exception as e:
        print(f'Unexpected error writing to {log_file}.\n{e}\nLogging disabled.')
        is_logging = False
        return None

def do_upload(file):
    rclone_cmd = ['rclone', 'copy', file, 'gdrive:/kbm_backups']
    try:
        with Capturing() as output:
            run_cmd(rclone_cmd)
        for o in output:
            verboseprint(o)
        verboseprint(f'{file} uploaded.')
        return True
    except:
        verboseprint(f'Upload of {file} failed.')
        return False

# Pass 'tag' to this function to generate a time/datestamped archive file
# in the format tag_YYYY-mm-dd_hhmmss.tar.xz
# Standard use for 
def make_tarball(tag, targets, working_dir=homedir):
    if os.getcwd() != working_dir: os.chdir(working_dir)
    if not os.path.isdir(backup_dir):
        try:
            os.mkdir(backup_dir)
        except Exception as e:
            verboseprint('Error creating backup directory, aborting')
            verboseprint(e)
            sys.exit()
    filename = f'{tag}_{timestamp}.tar.xz'
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
    with Capturing() as output:
        tar.list()
    for o in output:
        verboseprint(o)
    path = f'{working_dir}/{filename}'
    tar.close()
    do_upload(path)
    shutil.move(path, f'{backup_dir}/{filename}')
    return path

def do_backup(c, g):
    ctar = lambda do_cfg: make_tarball('config',['printer_data/config'], working_dir=homedir) if do_cfg else None
    gtar = lambda do_gco: make_tarball('gcode',['printer_data/gcodes'], working_dir=homedir) if do_gco else None
    ctar(c)
    gtar(g)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Option not recognized.')
        print('Try\x1b[1m',sys.argv[0],'--help\x1b[0m')
        sys.exit()
    timestamp = dt.now().strftime('%Y-%m-%d_%H%M%S')
    config='klipper-backup-manager/kbm.toml'
    exclude_exts=['.tmp','.ignore','.swp']

    main()

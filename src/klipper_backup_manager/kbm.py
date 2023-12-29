#!/usr/bin/env python3

import os, sys, shutil
import tarfile
from datetime import datetime as dt
from subprocess import run as run_cmd
default_log_level = logging.CRITICAL
homedir = os.path.expanduser('~')
kbm_dir = f'{homedir}/klipper-backup-manager'
log_dir=f'{kbm_dir}/logs'
backup_dir=f'{kbm_dir}/backups'
@click.command()
@click.option('--config', '-c', default=False, is_flag=True, help='back up Klipper config files')
@click.option('--gcode', '-g', default=False, is_flag=True, help='back up gcodes')
@click.option('--verbose', '-v', default=False, is_flag=True, help='enable verbose mode')
@click.option('--log', '-l', default=False, is_flag=True, help='enable logging')
def main(config, gcode, verbose, log):
    global is_verbose
    is_verbose = verbose
    if os.getcwd() != homedir: os.chdir(homedir)
    if log:
        log_file = dt.now().strftime('kbm_%Y-%m-%d_%H%M%S.log')
        if not os.path.isdir(log_dir):
            try:
                os.mkdir(log_dir)
                log_path = f'{log_dir}/{log_file}'
            except PermissionError as e:
                verboseprint('Could not create log directory.')
                verboseprint(e)
                log_path = f'{homedir}/{log_file}'
        logging.basicConfig(filename=log_path, filemode='w', level=logging.DEBUG)
    else:
        log_path = f'{homedir}/log_file'
        logging.basicConfig(filename=log_path, filemode='w', level=default_log_level)
    logging.info('Starting backup.')
    do_backup(config, gcode)
    logging.info('End of backup.')

def verboseprint(*args, **kwargs):
    if is_verbose: print(*args, **kwargs)

def do_upload(file):
    rclone_cmd = ['rclone', 'copy', file, 'gdrive:/kbm_backups']
    result = run_cmd(rclone_cmd)
    if result.returncode == 0:
        success = f'{file} uploaded successfully.'
        verboseprint(success)
        logging.info(success)
        return True
    except:
        uploadfailed = f'Failed to upload {file}.'
        verboseprint(uploadfailed)
        cmd_string = ' '.join(rclone_cmd)
        logging.error(uploadfailed)
        logging.error('Subprocess %s failed with return code %s.', cmd_string, result.returncode)

# Pass 'tag' to this function to generate a time/datestamped archive file
# in the format tag_YYYY-mm-dd_hhmmss.tar.xz
def make_tarball(tag, targets, working_dir=homedir):
    if os.getcwd() != working_dir: os.chdir(working_dir)
    if not os.path.isdir(backup_dir):
        try:
            os.mkdir(backup_dir)
        except PermissionError as e:
            verboseprint('Error creating backup directory, aborting')
            logging.critical('Could not create backup directory. Aborting backup.')
            verboseprint(e)
            sys.exit()
    filename = f'{tag}_{timestamp}.tar.xz'
    try:
        tar = tarfile.open(filename, 'w:xz')
    except Exception as e:
        verboseprint(f'Error opening {filename} in write mode. Aborting.')
        verboseprint(e)
        logging.critical('Could not open %s. Aborting backup.', filename)
        sys.exit()
    for t in targets:
        try:
            tar.add(t, filter=lambda tarinfo: None if os.path.splitext(tarinfo.name)[1] in exclude_exts else tarinfo)
            
        except FileNotFoundError:
            verboseprint(f'{t} not found.')
            logging.warning('Target %s not found. Not added to %s.', t, tar.name)
        except PermissionError:
            verboseprint(f'Permission denied adding {t} to 
            sys.exit()
    verboseprint(f'Backed up the following to {filename}:')
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

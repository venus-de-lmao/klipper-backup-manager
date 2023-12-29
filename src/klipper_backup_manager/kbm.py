#!/usr/bin/env python3

import os, sys, shutil, logging, errno
import click
import tarfile
from datetime import datetime as dt
from subprocess import run as run_cmd
homedir = os.path.expanduser('~')
kbm = 'klipper-backup-manager'
kbmdir = os.path.join(homedir, kbm)
kbmlocal = os.path.join(homedir, '.kbmlocal')
logdir = os.path.join(kbmlocal, 'logs')
backupdir = os.path.join(kbmlocal, 'backups')
timestamp = dt.now().strftime('%Y-%m-%d_%H%M%S')
kbmconfig = os.path.join(kbmdir, 'kbm.toml') # the next objective is to implement reading options from this file and using them
exclude_exts=['.tmp','.ignore','.swp']

@click.command()
@click.option('--config', '-c', default=False, is_flag=True,
        help='Backs up Klipper config files')
@click.option('--gcode', '-g', default=False, is_flag=True,
        help='Backs up all stored gcodes.')
@click.option('--verbose', '-v', default=False, is_flag=True, 
        help='Enables verbose mode, printing output to stdout.')
@click.option('--log', default='ERROR', metavar='LEVEL', 
        help='Sets the minimum severity of events to log. By default only errors are logged. Type \x1b[1m{argv} --levels\x1b[0m for more info.')
@click.option('--levels', is_flag=True, help='Get more information about logging severity levels.')
def main(config, gcode, verbose, log, levels):
    if levels:
        lvl_list = [
                ['DEBUG', 'Detailed information, typically only of interest when diagnosing a problem.'],
                ['INFO', 'Confirmation message that the software is operating as expected.'],
                ['WARNING', 'Notification when something unexpected has happened; for now the software is still working.'],
                ['ERROR', 'Alerts you when something has gone wrong; the software has failed to perform some task, but is still running.'],
                ['CRITICAL', 'Something serious has gone wrong; the software has encountered a critical error and may have to close.']]
        msg_list = ['\x1b[1m{:<16}\x1b[0m{}'.format(lvl_list[m][0], lvl_list[m][1]) for m in range(len(lvl_list))]
        for msg in msg_list:
            print(msg)
        print('\nThe software will log events that meet or exceed the minimum threshold you set. ERROR is the default.')
        sys.exit(0)
    global is_verbose
    is_verbose = verbose
    loglevel = getattr(logging, log.upper())
    logname = f'kbm_{timestamp}.log'
    logfile = f'{logdir}/{logname}'
    # now we check that all required dirs either exist or can be created
    isdir = lambda x : os.path.isdir(x) # this is just because I'm lazy and don't feel like typing out
    exist = lambda x : os.path.exists(x)    # the full os.path.isdir() and os.path.exists() every time
    logging.basicConfig(filename=log_path, filemode='w', level=loglevel) # first we initialize logging
    if os.getcwd() != homedir: os.chdir(homedir)
    try:
        for d in [logdir, backupdir]:
            if not exist(d):
                os.makedirs(d)
                local_succ = 'Created {succ} successfully.'.format(succ = d)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            verboseprint('Critical: OSError [Errno {err_no}]: {err_str}'.format(err_no = exc.errno, err_str = exc.strerror))
            logging.critical('Critical: OSError [Errno {err_no}]: {err_str}'.format(err_no = exc.errno, err_str = exc.strerror))
            raise
        else:
            verboseprint('Critical: Something is in the way. Aborting.')
            logging.critical('Critical: Something is in the way. Aborting.')
            logging.critical(exc)
            raise

    logging.info('Starting backup.')
    do_backup(config, gcode)
    logging.info('End of backup.')

verboseprint = lambda *a, **kw : print(*a, **kw) if is_verbose else None

def do_upload(file):
    rclone_cmd = ['rclone', 'copy', file, 'gdrive:/kbm_backups'] # plan to implement more backup methods than just rclone
    result = run_cmd(rclone_cmd)
    if result.returncode == 0:
        success = f'{file} uploaded successfully.'
        verboseprint(success)
        logging.info(success)
        return True
    else:
        uploadfailed = f'Failed to upload {file}.'
        verboseprint(uploadfailed)
        cmd_string = ' '.join(rclone_cmd)
        logging.error(uploadfailed)
        logging.error('Subprocess {process} failed with return code {c}.'.format(process = cmd_string, c = result.returncode))

# Pass 'tag' to this function to generate a time/datestamped archive file
# in the format tag_YYYY-mm-dd_hhmmss.tar.xz
def make_tarball(tag, targets, working_dir=homedir):
    if os.getcwd() != working_dir: os.chdir(working_dir)
    filename = f'{tag}_{timestamp}.tar.xz'
    for t in targets:
        try:
            tar.add(t, filter=lambda tarinfo: None if os.path.splitext(tarinfo.name)[1] in exclude_exts else tarinfo)
        except FileNotFoundError:
            verboseprint(f'{t} not found.')
            logging.warning('Target %s not found. Not added to %s.', t, tar.name)
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
    main()

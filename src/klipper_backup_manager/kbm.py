#!/usr/bin/env python3

import os, sys, shutil, logging, errno
import logging.config
import yaml
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
@click.option('--save-config', '-s', required=True, metavar='TARGET'
        help='Run config backup. Saves your Klipper config files.')
@click.option('--save-gcode', '-g', default=False, is_flag=True,
        help='Backs up all stored gcodes.')
@click.option('--verbosity', '-v',  default=0, metavar='N',
        help='Sets verbosity level of console messages. 0 outputs warnings and errors. 1 outputs normal messages, warnings, and errors, and 2 is debug mode. Default is 0.')
@click.option('--log', '-l',  default=1, metavar='N', 
        help='Sets the verbosity level of saved log files. Works the same as \x1b[1m--verbosity\x1b[0m. Default is 1.')
def main(save_config, save_gcode, verbosity, log):
    """Klipper Backup Manager will allow you to back up
    and restore your Klipper settings and uploaded gcodes
    easily from the command line.

    The entire process is run automatically with a single command,
    so it can be automated with \x1b[1mcron\x1b[0m, for example,
    or called from a shell script or even a Klipper macro.
    """
    get_verbosity = lambda x : logging.DEBUG if x == 2 else (logging.INFO if x == 1 else logging.WARNING)
    ch_level = get_verbosity(verbosity) # Severity level of console logging handler; WARNING by default
    fh_level = get_verbosity(log)       # Severity level of logfile handler; INFO by default.
    logfile = os.path.abspath(os.path.expanduser(logger_config['handlers']['file']['filename']))
    logger_config['handlers']['file']['filename'] = logfile # make sure the path makes sense to the logging methods
    logger_config['handlers']['file']['level'] = fhlevel    # update the level for each handler
    logger_config['handlers']['console']['level'] = chlevel # based on user input 
    logging.config.dictConfig(logger_config)
    logging.debug('Loaded logger settings from logging.yaml.')
    logger = logging.getLogger('KBM')
    logger.debug('KBM logger active.')
    logger.info('Starting backup...')
    # now we check that all required dirs either exist or can be created
    isdir = lambda x : os.path.isdir(x) # this is just because I'm lazy and don't feel like typing out
    exist = lambda x : os.path.exists(x)    # the full os.path.isdir() and os.path.exists() every time
    if os.getcwd() != homedir: os.chdir(homedir)
    try:
        for d in [logdir, backupdir]:
            if not exist(d):
                logger.debug(f'{d} not found. Attempting to create.')
                os.makedirs(d)
                local_succ = 'Created {succ} successfully.'.format(succ = d)
                logger.debug(local_succ)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            logger.critical('Critical: OSError [Errno {err_no}: {err_str}'.format(err_no = exc.errno, err_str = exc.strerror))
            raise
        else:
            logger.critical('Critical: Something is in the way. Aborting. {}'.format(exc.strerror))
            raise
    do_backup(config, gcode)

def do_upload(file):
    rclone_cmd = ['rclone', 'copy', file, 'gdrive:/kbm_backups'] # plan to implement more backup methods than just rclone
    cmd_string = ' '.join(rclone_cmd)
    logger.debug('Calling {}'.format(cmd_string))
    result = run_cmd(rclone_cmd)
    if result.returncode == 0:
        success = f'{file} uploaded successfully.'
        logger.info(success)
        return True
    else:
        uploadfailed = f'Failed to upload {file}.'
        logger.error(uploadfailed)
        logger.error("Subprocess '{process}' failed with return code {c}.".format(process = cmd_string, c = result.returncode))

# Pass 'tag' to this function to generate a time/datestamped archive file
# in the format tag_YYYY-mm-dd_hhmmss.tar.xz
def make_tarball(tag, targets, working_dir=homedir):
    if os.getcwd() != working_dir:
        logger.debug('Current working directory is {}. Switching to {}.'.format(os.getcwd(), working_dir)
        os.chdir(working_dir)
    filename = f'{tag}_{timestamp}.tar.xz'
    tar = tarfile.open(filename, 'w:xz')
    logger.debug('Opened {} in write mode with lzma compression.'.format(filename))
    for t in targets:
        logger.debug('Adding target {}'.format(t))
        try:
            tar.add(t, filter=lambda tarinfo: None if os.path.splitext(tarinfo.name)[1] in exclude_exts else tarinfo)
        except FileNotFoundError:
            logger.warning('Target {} not found. Not added.'.format(tar.name))
        logger.info('{} created successfully.'.format(filename)) # remember to implement a handler to capture the output here
    path = f'{working_dir}/{filename}'
    tar.close()
    logger.debug('Closed tar file {}.'.format(tar.name))
    do_upload(path)
    shutil.move(path, f'{backup_dir}/{filename}') # we should already have permission to do this
    logger.debug('Moved {} to {}'.format(tar.name, backup_dir))
    return path

def do_backup(c, g):
    msg = lambda x, y : 'full backup' if x and y else ('config backup' if x and not y else 'gcode backup')
    logger.debug('Running {}...'.format(msg(c, g)))
    ctar = lambda do_cfg: make_tarball('config',['printer_data/config'], working_dir=homedir) if do_cfg else None
    gtar = lambda do_gco: make_tarball('gcode',['printer_data/gcodes'], working_dir=homedir) if do_gco else None
    ctar(c)
    gtar(g)

if __name__ == '__main__':
    with open('logging.yaml', 'r') as file:
        logger_config = yaml.safe_load(file)
    if len(sys.argv) < 2:
        print('Option not recognized.')
        print('Try\x1b[1m',sys.argv[0],'--help\x1b[0m')
        sys.exit()
    main()

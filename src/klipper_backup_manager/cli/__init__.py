import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler as TRFileHandler

import cloup
from cloup import option

@cloup.group()
@option(
    '--debug', '-d', is_flag=True,
    required=False, help='Enables debug messages.')
@option(
    '--profile', '-p',
    required=False, default='default',
    help='Specifies which settings profile from '\
        'kbm.yaml to use. Uses default settings if not specified.'
    )
def cli(debug, profile='default'):
    for h in (log.handlers):
        (h.setLevel(logging.DEBUG) if debug else None)
        (h.setFormatter(timestamped) if debug else None)
    global cfg # I know this is discouraged but cfg needs to be accessible globally
    cfg = kbmsettings.SettingsFile(profile)
    cfg.load()

      # timestamp everything in debug mode

@cli.command()
@cloup.argument('tag')
def backup(tag):
    log.debug("Attempting to start backup: '%s'", tag)
    if tag not in list(cfg.profile) and tag != 'all':
        log.warning("Invalid task backup '%s'", tag)
        sys.exit()
    log.debug("Validated backup task: '%s'", tag)
    pdata = cfg.pull_entry('printer').get('printer_data')
    log.debug('Initializing Archive object.')
    arc_file = kbmarchiver.Archive(tag, pdata)
    log.info('Creating file.')
    arc_file.create_file()

def get_file_list(tag='all'):
    tags = ([t for t in list(cfg.profile) if 'maxbackups' in cfg.profile[t]]) if tag == 'all' else [tag]
    tag_files = [f for f in os.listdir(kbm.backupdir) if os.path.isfile(os.path.join(kbm.backupdir, f))]
    for tf in tag_files:
        if tf.startswith(tuple(tags)):
            yield tf

@cli.command()
def restore():
    files = list(get_file_list())
    n = 0
    for f in files:
        print(f'{n}: {f!s}')
        n += 1
    while True:
        sel = input('Select a number:')
        if str(sel).lower() in ('q', 'quit', 'exit', 'cancel'):
            break
        try:
            sel = int(sel)
        except ValueError:
            print("Not an integer.")
            break
        if -1 <= sel <= n:
            tgt = os.path.abspath(os.path.join(kbm.backupdir, files[sel]))
            log.info("Attempting to restore file %s", tgt)
            kbm.archiver.extract_file(tgt)
            break
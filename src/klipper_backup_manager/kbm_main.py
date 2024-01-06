#!/usr/bin/env python3
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler as TRFileHandler
import click
import cloup
import kbm
import kbm.archiver
import kbm.settings
from cloup import option

logdir = os.path.join(os.path.expanduser("~/.kbmlocal"), "logs")
logfile = os.path.join(logdir, "kbm.log")
log = logging.getLogger(__name__)
clog = logging.StreamHandler(sys.stdout)
clog.setLevel(logging.INFO)
flog = TRFileHandler(logfile, when="midnight", interval=1, backupCount=7)
timestamped = logging.Formatter(fmt="%(asctime)s %(name)-8s %(levelname)-10s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
flog.setLevel(logging.INFO)
flog.setFormatter(timestamped)
log = logging.getLogger('kbm')
log.setLevel(logging.DEBUG)
log.addHandler(clog)
log.addHandler(flog)

cfg = kbm.settings.SettingsFile('default')
cfg.load()

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
    arc_file = kbm.archiver.Archive(tag, pdata)
    log.debug('Creating file.')
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
        log.info('%s: %s', n, str(f))
        n += 1
    while True:
        sel = int(input('Select a number:'))
        if 0 <= sel <= n:
            tgt = os.path.abspath(os.path.join(kbm.backupdir, files[sel]))
            log.debug("Attempting to restore file %s", tgt)
            kbm.archiver.extract_file(tgt)
            break


if __name__ == '__main__':
    cli()
#!/usr/bin/env python3
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler as TRFileHandler

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
    global settings
    settings=kbm.settings.SettingsFile(profile)
    settings.load()
    for h in (log.handlers):
        (h.setLevel(logging.DEBUG) if debug else None)
        (h.setFormatter(timestamped) if debug else None)
        # timestamp everything in debug mode




@cli.command()
@cloup.argument('tag')
def backup(tag):
    log.debug("Attempting to start backup: '%s'", tag)
    if tag not in list(settings.profile):
        log.warning("Invalid archive type '%s'", tag)
        sys.exit()
    log.debug("Valid backup type: '%s'", tag)
    pdata = settings.pull_entry('printer').get('printer_data')
    log.debug('Initializing Archive object.')
    arc_file = kbm.archiver.Archive(tag, pdata)
    log.debug('Creating file.')
    arc_file.create_file(tag)

@cli.command()
@cloup.argument('tag')
def restore(tag):
    log.warning("Restore command run for '%s' but not fully implemented.", tag)

if __name__ == '__main__':
    
    cli()

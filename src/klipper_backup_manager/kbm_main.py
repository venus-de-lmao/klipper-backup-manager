#!/usr/bin/env python3
import cloup
import kbm
import kbm.archiver
import kbm.settings
from cloup import option
import logging, os, sys
from logging.handlers import TimedRotatingFileHandler as TRFileHandler
logdir = os.path.join(os.path.expanduser("~/.kbmlocal"), "logs")
logfile = os.path.join(logdir, "kbm.log")
log = logging.getLogger('kbm.'+__name__)
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
    settings=kbm.settings.SettingsFile(profile)
    settings.load()
    for h in (log.handlers):
        (h.setLevel(logging.DEBUG) if debug else None)




@cli.command()
def backup():
    log.warning('Backup command run.')

@cli.command()
def restore():
    log.warning('Restore command run.')
if __name__ == '__main__':
    cli()

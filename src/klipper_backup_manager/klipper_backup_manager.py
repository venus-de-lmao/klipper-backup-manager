#!/usr/bin/env python3
import kbm
import kbm.settings
import kbm.archiver
import cloup
from cloup import option_group, option

log = kbm.log.getChild(__name__)

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
def cli(debug, profile):
    if debug:
        log.handlers.clog.setLevel('DEBUG')
        log.handlers.flog.setLevel('DEBUG') 
    settings=kbm.settings.SettingsFile(profile)
    settings.load()


@cli.command()
def backup():
    print('backup command')

@cli.command()
def restore():
    print('restore command')
if __name__ == '__main__':
    cli()
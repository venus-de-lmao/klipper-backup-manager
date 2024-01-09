# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import yaml
from pathlib import Path as p
import click, cloup
from cloup import option
from datetime import datetime as d

from logging.handlers import TimedRotatingFileHandler as TRFileHandler

kbmlocal = p.home().joinpath('.kbmlocal')
backupdir = kbmlocal.joinpath('backups')
logdir = kbmlocal.joinpath('logs')
kbmyaml = kbmlocal.joinpath('kbm.yaml')
if not backupdir.exists():
    backupdir.mkdir(parents=True)

if not logdir.exists():
    logdir.mkdir(parents=True)

class Settings:
    def default_settings(self):
        return {
            'default': {
                'gcodes_dir': '~/printer_data/gcodes',
                'config_dir': '~/printer_data/config',
                'max_backups': 5,
                'extras': {
                    'kiauh': {
                        'location': '~/kiauh',
                        'git_repo': 'https://github.com/dw-0/kiauh.git'
                    },
                    'kamp': {
                        'location': '~/Klipper-Adaptive-Meshing-Purging',
                        'git_repo': 'https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging'
                    }
                }
            }
        }
    def __init__(self, profile):
        if not kbmyaml.exists(): # dump the default profile into a file
            self.profile = self.default_settings()['default']
            with open(kbmyaml, 'w') as file:
                yaml.safe_dump(self.default_settings(), file)
        else:
            with open(kbmyaml, 'r') as file:
                self.profile = yaml.safe_load(file)[profile]
    def write(self):
        with open(kbmyaml, 'r+') as cfg_file:
            self.newcfg = yaml.safe_load(cfg_file)
        self.newcfg.update(self.profile, self.settings)
        yaml.safe_dump(self.newcfg, kbmyaml)
    def get(self, entry_name):
        return self.profile.get(entry_name)


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
    cfg = Settings(profile)

def test():
    cfg = Settings('default')


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


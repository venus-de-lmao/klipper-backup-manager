# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import tarfile
from datetime import datetime
from os import chdir
from pathlib import Path

import cloup
from cloup import option_group, option
from cloup.constraints import RequireAtLeast

import yaml

# TODO:
# Rewrite command-line interface w/ option groups
# Reimplement logging and tqdm progress bars.
# Write restore function.
# Look into remote upload options besides rclone.

kbmlocal = Path.home().joinpath('.kbmlocal')
backup_dir = kbmlocal.joinpath('backups')
logdir = kbmlocal.joinpath('logs')
kbmyaml = kbmlocal.joinpath('kbm.yaml')
if not backup_dir.exists():
    backup_dir.mkdir(parents=True)

if not logdir.exists():
    logdir.mkdir(parents=True)

class Settings:
    def def_settings(self):
        return {
            'printer_data': '~/printer_data',
            'configs': ['config','database'],
            'max_backups': 5,
            'mostrecent': {
                'config': None,
                'gcode': None
            },
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
    def __init__(self):
        self.profile = self.def_settings() # start with default settings
        if not kbmyaml.exists(): # dump the default profile into a file
            with open(kbmyaml, 'w') as f:
                yaml.safe_dump(self.profile, f)
    def get(self, entry_name, value=None):
        return self.profile.get(entry_name, value)
    def write(self):
        with open(kbmyaml, 'w') as file:
            yaml.safe_dump(self.profile, file)
    def __enter__(self):
        with open(kbmyaml) as file:
            self.profile = yaml.safe_load(file)
        return self
    def __exit__(self, exc_type, exc_value, exc_traceback):
        return



def backup():
    file_tag = "config" if not gcode else "gcode"
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M")
    backup_filename = f"{file_tag}_backup_{timestamp}.tar.xz"
    backup_path = backup_dir
    with Settings() as cfg:
        maxbackups = cfg.get("max_backups", 5)
        configs = cfg.get("configs", None)
        extras = cfg.get("extras", None)
        printer_data = Path(cfg.get("printer_data")).expanduser()
    with tarfile.open(backup_filename, "w:xz") as tar:
        chdir(printer_data.parent)
        if gcode:
            tar.add(printer_data.stem.join("gcodes"))
        else:
            for t in configs:
                tar.add(printer_data.stem.join(t))
    with Settings() as cfg:
        cfg.profile["mostrecent"].update(file_tag, backup_filename)
        cfg.write()

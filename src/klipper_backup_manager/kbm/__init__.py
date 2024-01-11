# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import tarfile
from datetime import datetime
from os import chdir
import sys
import pathlib
from pathlib import Path
from time import sleep
import yaml
from tqdm import tqdm

# To do:
# Rewrite command-line interface w/ option groups
# Reimplement logging and tqdm progress bars.
# Write restore function.
# Look into remote upload options besides rclone.

kbmlocal = Path.home().joinpath('.kbmlocal')
backup_dir = kbmlocal.joinpath('backups')
logdir = kbmlocal.joinpath('logs')
kbmyaml = kbmlocal.joinpath('kbm.yaml')
def directory_files(target):
    # generator function to
    top_dir = Path(target)
    outlist = []
    for dirpath, dirs, files in pathlib.os.walk(top_dir):
        for f in files:
            outlist.append(str(Path(dirpath).joinpath(f)))
    return sorted(outlist)
def directory_size(target):
    file_size = 0
    for f in directory_files(target):
        file_size += f.stat().st_size
    return file_size

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



def backup(gcode: False):
    file_tag = "config" if not gcode else "gcode"
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M")
    backup_filename = f"{file_tag}_backup_{timestamp}.tar.xz"
    with Settings() as cfg:
        maxbackups = cfg.get("max_backups", 5)
        configs = cfg.get("configs", None)
        extras = cfg.get("extras", None)
        printer_data = Path(cfg.get("printer_data")).expanduser()
        pdata_stem = Path(printer_data.stem)
    tgt = [pdata_stem.joinpath(f) for f in configs] if not gcode\
        else [pdata_stem.joinpath("gcodes")]
    #with tarfile.open(backup_filename, "w:xz") as tar:
    chdir(printer_data.parent)
    for t in tgt:
        print("Backing up: {}".format(t))
        with tqdm(total=directory_size(t), unit="B", unit_scale=True) as pbar:
            with tarfile.open(backup_filename, 'w:xz') as tar:
                for f in directory_files(t):
                    tqdm.write(f)
                    tar.add(f)
                    pbar.update(f.stat().st_size)

   # with Settings() as cfg:
    #    cfg.profile["mostrecent"].update(file_tag, backup_filename)
    #   cfg.write()

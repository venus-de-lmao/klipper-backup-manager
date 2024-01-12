# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path

import yaml
from tqdm import tqdm

# To do:
# Look into remote upload options besides rclone.

kbmlocal = Path.home().joinpath('.kbmlocal')
backup_dir = kbmlocal.joinpath('backups')
logdir = kbmlocal.joinpath('logs')
kbmyaml = kbmlocal.joinpath('kbm.yaml')
exc_suffixes = (".bkp", ".bak", ".tmp", ".log", )
def directory_files(target):
    top_dir = Path(target)
    outlist = []
    outsize = 0
    for dirpath, dirs, files in os.walk(top_dir):
        for f in files:
            outpath = Path(Path(dirpath).joinpath(f))
            if (not outpath.is_symlink()) and (outpath.suffix not in exc_suffixes):
                outlist.append(outpath)
                outsize += outpath.stat().st_size
    return (sorted(outlist), outsize)

if not backup_dir.exists():
    backup_dir.mkdir(parents=True)

if not logdir.exists():
    logdir.mkdir(parents=True)

class Settings:
    # Here we define the default settings YAML that will be dumped
    # into a file the first time KBM is run.
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
                    'git_repo': 'https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging.git'
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
        del self.profile

def arc_cleanup(files: list, maximum: int):
    if len(files) <= maximum:
        return None
    for f in files[maximum::]:
        os.remove(f)

def get_most_recent(files: list):
    for f in files:
        if Path(f).exists():
            return f

def do_archive(tag: str):
    if tag not in ("config", "gcode"):
        raise ValueError
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M%S")
    backup_filename = f"{tag}_backup_{timestamp}.tar.xz"
    backup_file_path = Path(backup_dir.joinpath(backup_filename))
    with Settings() as cfg:
        maxbackups = cfg.get("max_backups", 5)
        configs = cfg.get("configs", None)
        printer_data = Path(cfg.get("printer_data")).expanduser()
        pdata_stem = Path(printer_data.stem)
    if tag == "config":
        tgt = pdata_stem.joinpath("config")
    elif tag == "gcode":
        tgt = pdata_stem.joinpath("gcodes")
    else:
        print("This code should never execute!")
        sys.exit(1)
    os.chdir(printer_data.parent)
    dfiles = directory_files(tgt)
    tgt_files = dfiles[0]
    tgt_size = dfiles[1]
    if tag == "config":
        db_dir = pdata_stem.joinpath("database")
        db_ = directory_files(db_dir)
        tgt_files = tgt_files + db_[0]
        tgt_size += db_[1]
    if not tgt_files: # this should prevent accidentally creating empty tarballs
        print("No files to back up!")
        return None
    print(f"Backing up files to: \x1b[33m{backup_file_path}\x1b[39m")
    with (tqdm(total=tgt_size, unit="B", unit_scale=True, unit_divisor=1024) as pbar,
    tarfile.open(backup_file_path, 'w:xz') as tar):
        for f in tgt_files:
            tqdm.write(str(f))
            tar.add(f)
            pbar.update(f.stat().st_size)
       
    backups = sorted(backup_dir.glob(f"{tag}_backup_*.tar.*"), reverse=True)
    arc_cleanup(backups, maxbackups)

def do_unarchive(tag: str):
    if tag not in ("config", "gcode"):
        raise ValueError
    with Settings() as cfg:
        pdata = Path(cfg.get("printer_data")).expanduser()
        pdata_stem = Path(pdata).stem
    backups = sorted(backup_dir.glob(f"{tag}_backup_*.tar.*"), reverse=True)
    archive_path = get_most_recent(backups)
    os.chdir(pdata.parent)
    t_size = 0
    with tarfile.open(archive_path, "r") as tar:
        for member in tar.getmembers():
            t_size = (t_size+member.size if member.isfile() else t_size)
    print(f"Extracting: \x1b[33;1m{archive_path}\x1b[39;22m")
    with (
        tqdm(
            total=t_size,
            unit="B", unit_scale=True, unit_divisor=1024
        ) as pbar,
        tarfile.open(archive_path, 'r') as tar):
            restore_kamp = False
            for f in tar.getmembers():
                # check to see if user has backed up a KAMP cfg file
                # and set a flag to reinstall KAMP
                if "KAMP_Settings.cfg" in f.name:
                    restore_kamp = True
                tqdm.write(f.name)
                pbar.update(f.size)
                tar.extract(f, pdata.parent, filter="data")
    if restore_kamp:
        do_restore_kamp()
    # Check to see if fluidd-config is installed and restore the symlink
    # to fluidd.cfg
    if tag == "config":
        fluidd_cfg = Path(Path.home().joinpath("fluidd-config", "fluidd.cfg"))
        if fluidd_cfg.is_file:
            os.symlink(fluidd_cfg, Path(pdata_stem).joinpath("config", "fluidd.cfg"))
   
def backup(config, gcode):
    with Settings() as cfg:
        printer_data = Path(cfg.get("printer_data")).expanduser()
    if not printer_data.exists():
        print(f"Klipper does not appear to be installed! \x1b[33;1m{printer_data.resolve()!s}\x1b[39;22m directory not found.")
        print("It is recommended to install Klipper with KIAUH (Klipper Install And Update Helper).")
        do_restore_kiauh()
        sys.exit(0)
    if config:
        do_archive("config")
    if gcode:
        do_archive("gcode")

def restore(config, gcode):
    if config:
        do_unarchive("config")


# KIAUH and KAMP restores are hardcoded
# because they have specific installation steps
def do_restore_kiauh():
    # Prompt user to reinstall KIAUH. Default is no.
    os.chdir(Path.home())
    with Settings() as cfg:
        if "extras" not in cfg.profile:
            return False
        extras = cfg.get("extras")
        if "kiauh" not in extras:
            return False
        kdir = Path(extras["kiauh"].get("location")).expanduser()
        k_repo = extras["kiauh"].get("git_repo")
    if not Path(kdir).exists():
        # Check to see if KIAUH is already installed, and install if not.
        if not input("Install Klipper Install And Update Helper? [y\x1b[1mN\x1b[22m]: ").lower().startswith("y"):
            return False
        gitclone = subprocess.run(["git", "clone", k_repo], check=True)
        if gitclone.returncode:
            sys.exit(gitclone.returncode)
        print(f"KIAUH installed successfully. Run \x1b[1;33m{kdir}/kiauh.sh\x1b[22;39m to reinstall Klipper.")
    return True

def do_restore_kamp():
    # Prompt user to reinstall KAMP; default is yes.
    if input("Reinstall \x1b[33;1mKlipper-Adaptive-Meshing-Purging\x1b[39;22m? [\x1b[1mY\x1b[22mn]").lower().startswith("n"):
        return None
    os.chdir(Path.home())
    with Settings() as cfg:
        k_repo = cfg.profile["extras"]["kamp"]["git_repo"]
        pdata = Path(cfg.get("printer_data"))
        kampdir = Path(cfg.profile["extras"]["kamp"]["location"]).resolve().stem
        full_path_kampdir = Path(kampdir).absolute()
    if full_path_kampdir.exists():
        print(f"KAMP directory \x1b[33;1m{full_path_kampdir}\x1b[39;22m already exists.")
        sys.exit()
    gitclone = subprocess.run(["git", "clone", k_repo], check=True)
    if gitclone.returncode:
        sys.exit(gitclone.returncode)
    ln_dest = pdata.resolve().joinpath("config", "KAMP")
    os.symlink(Path(kampdir).joinpath("Configuration"), ln_dest, target_is_directory=True)
    # Assuming user has previously installed KAMP, this just restores the symlink
    # All of the KAMP settings are in the printer_data/config directory, so we don't
    # want to overwrite those with the default installation


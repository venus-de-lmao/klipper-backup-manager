# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import subprocess
import sys
from pathlib import Path

import kbm.filer
from kbm.config import Settings


def do_the_thing(runmode: str, tags: tuple):
    if runmode == "backup":
        backup(tags)
    elif runmode == "restore":
        restore(tags)
    elif runmode == "list_backups":
        for t in tags:
            kbm.filer.do_list(t) if t else None
            #print("") if t else None
    else:
        # We should never get here! Time to panic!
        print("Code that should be unreachable in kbm.do_the_thing() has been executed. I'm scared.")
        sys.exit(-1)

def backup(tags: tuple):
    with Settings() as cfg:
        printer_data = Path(cfg.get("printer_data")).expanduser()
    if not printer_data.exists():
        print(f"Klipper does not appear to be installed! \x1b[33;1m{printer_data.resolve()!s}\x1b[39;22m directory not found.")
        print("It is recommended to install Klipper with KIAUH (Klipper Install And Update Helper).")
        do_restore_kiauh()
        sys.exit(0)
    for tag in tags:
        kbm.filer.do_archive(tag)

def restore(tags: tuple):
    for tag in tags:
        kbm.filer.do_unarchive(tag)


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
        pdata = Path(cfg.get("printer_data")).expanduser()
        kampdir = Path(cfg.profile["extras"]["kamp"]["location"]).resolve().stem
        full_path_kampdir = Path(kampdir).absolute()
    if full_path_kampdir.exists():
        print(f"KAMP directory \x1b[33;1m{full_path_kampdir}\x1b[39;22m already exists.")
        sys.exit()
    os.chdir(Path(pdata).parent)
    gitclone = subprocess.run(["git", "clone", k_repo], check=True)
    if gitclone.returncode:
        sys.exit(gitclone.returncode)
    ln_dest = Path(pdata).joinpath("config", "KAMP")
    os.symlink(Path(kampdir).joinpath("Configuration"), ln_dest, target_is_directory=True)
    # Assuming user has previously installed KAMP, this just restores the symlink
    # All of the KAMP settings are in the printer_data/config directory, so we don't
    # want to overwrite those with the default installation


#!/usr/bin/env python3
import kbm
import sys
import cloup
from cloup import option_group, option
from cloup.constraints import mutually_exclusive, RequireAtLeast

@cloup.command()
@option_group("Archive options:",
    option(
        "--backup", "-b", is_flag=True,
        help="Backs up your selected target."
    ),
    option(
        "--restore", "-r", is_flag=True,
        help="Restores your selected target."
    ),
    help="Specify whether to back up or restore files.",
    constraint=mutually_exclusive
)
@option_group(
    "Target options:",
    option(
        "--config","-c", is_flag=True, help="Backs up Klipper configuration files."
    ),
    option(
        "--gcode", "-g", is_flag=True, help="Backs up gcode files."
        ),
        help="Specify which files to back up or restore.",
        constraint=mutually_exclusive
)
def cli(backup, restore, config, gcode):
    if backup:
        kbm.backup(mode=("config" if config else "gcode"))
        sys.exit(0)
    if restore:
        kbm.restore(mode=("config" if config else "gcode"))
        sys.exit(0)

if __name__ == "__main__":
    cli()

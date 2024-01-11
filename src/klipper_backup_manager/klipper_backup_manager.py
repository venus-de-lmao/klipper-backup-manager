#!/usr/bin/env python3
import sys

import cloup
import kbm
from cloup import option, option_group
from cloup.constraints import RequireExactly


@cloup.command()
@option_group("Archive options",
    option(
        "--backup", "-b", is_flag=True,
        help="Backs up your selected target."
    ),
    option(
        "--restore", "-r", is_flag=True,
        help="Restores your selected target."
    ),
    help="Specify whether to back up or restore files.",
    constraint=RequireExactly(1)
)
@option_group(
    "Target options",
    option(
        "--config","-c", is_flag=True, help="Backs up Klipper configuration files."
    ),
    option(
        "--gcode", "-g", is_flag=True, help="Backs up gcode files."
        ),
        help="Specify which files to back up or restore.",
        constraint=RequireExactly(1)
)
def cli(backup, restore, config, gcode):
    if config:
        run_mode = "config"
    elif gcode:
        run_mode = "gcode"
    if backup:
        kbm.backup(mode=run_mode)
        sys.exit(0)
    if restore:
        kbm.restore(mode=run_mode)
        sys.exit(0)

if __name__ == "__main__":
    cli()

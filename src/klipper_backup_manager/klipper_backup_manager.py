#!/usr/bin/env python3
import sys

import cloup
import kbm
from cloup import option, option_group
from cloup.constraints import RequireExactly, RequireAtLeast, mutually_exclusive


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
    option("--list-backups", "-l", is_flag=True,
    help="Lists all currently-saved files."),
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
    option(
        "--database", "-d", is_flag=True, help="Backs up database files."
    ),
        help="Specify which files to back up or restore.",
        constraint=RequireAtLeast(1)
)
def cli(backup, restore, list_backups, config, gcode, database):
    tags = (
        ("config" if config else None),
        ("gcode" if gcode else None),
        ("database" if database else None)
    )
    modes = [backup, restore, list_backups]
    mode_index = [modes.index(i) for i in modes if i][0]
    runmode = ["backup", "restore", "list_backups"]
    kbm.do_the_thing(runmode[mode_index], tags)

if __name__ == "__main__":
    cli()

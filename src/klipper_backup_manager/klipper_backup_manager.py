#!/usr/bin/env python3

import cloup
import kbm
from cloup import option, option_group
from cloup.constraints import RequireAtLeast, RequireExactly


@cloup.command()
@option_group("Archive options",
    option(
        "--backup", "-b", is_flag=True,
        help="Backs up your selected target."
    ),
    option(
        "--restore", "-r", is_flag=True,
        help="Restores the most recent backup from the selected category."
    ),
    option("--list-backups", "-l", is_flag=True,
    help="Lists all currently-saved files."),
    help="Specify whether to back up or restore files.",
    constraint=RequireExactly(1)
)
@option_group(
    "Target options",
    option(
        "--config","-c", is_flag=True, help="Klipper configuration files."
    ),
    option(
        "--gcode", "-g", is_flag=True, help="Gcode files."
        ),
    option(
        "--database", "-d", is_flag=True, help="Database files."
    ),
        help="Specify which files to back up, restore, or list.",
        constraint=RequireAtLeast(1)
)
def cli(backup, restore, list_backups, config, gcode, database):
    tag_pairs = [(config, "config"), (gcode, "gcode"), (database, "database")]
    tags = []
    for cond, tag_value in tag_pairs:
        if cond:
            tags.append(tag_value)
    modes = [backup, restore, list_backups]
    mode_index = next(modes.index(i) for i in modes if i)
    runmode = ["backup", "restore", "list_backups"]
    kbm.do_the_thing(runmode[mode_index], tags)

if __name__ == "__main__":
    cli()

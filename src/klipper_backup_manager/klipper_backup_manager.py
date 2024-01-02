#!/usr/bin/env python3
import click
from cloup import (
    HelpFormatter, HelpTheme, Style, command, option, option_group
    )
from cloup.constraints import mutually_exclusive, RequireAtLeast

import kbm
import kbmarc
from kbm import SettingsParser
log = kbm.log.getChild(__name__)

formatter_settings=HelpFormatter.settings(
    theme=HelpTheme(
        invoked_command=Style(fg='bright_yellow'),
        heading=Style(fg='bright_white', bold=True),
        constraint=Style(fg='magenta'),
        col1 = Style(fg='bright_yellow')
    )
)

@command(formatter_settings=formatter_settings)
@option_group(
    "Console output options",
    option(
        '-v', '--verbose',
        is_flag=True,
        help='Sets console output to verbose mode. This prints all '\
            'messages of INFO severity or above to console.'),
    option(
        '-d', '--debug',
        is_flag=True,
        help='Sets console output to debug mode. This generates '\
            'significantly more output than verbose mode and is useful for developers. '\
            'Also defaults to logging all debug info to file unless you set -l/--log.'),
    constraint=mutually_exclusive,)
def main(**kwargs):
    """Klipper Backup Manager"""

    with SettingsParser('default') as s:
        print(s.pull_entry('gcodes'))

if __name__ == "__main__":
    main(prog_name='klipper_backup_manager')
# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
#

# SPDX-License-Identifier: GPL-3.0-or-later
import click, cloup
import kbm
import click
from cloup import (
    HelpFormatter, HelpTheme, Style, command, group, option, option_group, argument
    )
from cloup.constraints import mutually_exclusive, RequireAtLeast
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

# Need to implement entire command structure for cloup handling. Deal with this later.
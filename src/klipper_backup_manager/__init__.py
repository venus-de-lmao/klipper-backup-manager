# SPDX-FileCopyrightText: 2023-present Laurel Ash <laurel.ash@proton.me>
#

# SPDX-License-Identifier: GPL-3.0-or-later
import KBM
from cloup import HelpFormatter, HelpTheme, Style

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

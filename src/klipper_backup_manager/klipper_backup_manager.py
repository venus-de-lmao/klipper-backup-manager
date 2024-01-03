#!/usr/bin/env python3
import click
import cloup
import kbm
from kbm import SettingsParser

@command()
@option_group(
    "Output options",
    option(
        "--verbose", "-v",is_flag=True,
        help="Sets console output to 'verbose' mode. Prints to console "\
        "all messages pertaining to normal operation, in addition to "\
        "warnings and errors."
    ),
    option(
        "--debug","-d",is_flag=True,
        help="Sets console output to 'debug' mode. Prints ALL messages "\
            "to console, including debugging messages. Useful for developers "\
            "or tracking down errors."
    ),
    option(
        "--log-verbose","-l",is_flag=True,
        help="Sets logging to verbose mode. Only logs warnings and above by default; "\
            "this option will save debug and normal messages to the log file as well."
    )
)
def cli(**kwargs):
    pass


def main(**kwargs):
    pass
if __name__ == "__main__":
    cli()
    settings = SettingsParser.SettingsFile(settings_profile)
    settings.load()

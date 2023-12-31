#!/usr/bin/env python3

import logging
import logging.config
import os
import sys
from logging.handlers import TimedRotatingFileHandler as TRFileHandler

import kbmanager
from kbmanager import KBMSettings

bold = "\x1b[1m"
unbold = "\x1b[22m"

settings = KBMSettings("default")
logdir = os.path.join(kbmanager.kbmlocal, "logs")
backupdir = os.path.join(kbmanager.kbmlocal, "backups")
log = logging.getLogger(__name__)
logfile = os.path.join(logdir, "kbm.log")

if settings.profile["logger"]["console"]["enabled"]:
    log.setLevel(logging.DEBUG)
    clog = logging.StreamHandler()
    clog.setLevel(settings.profile["logger"]["console"].setdefault("level", "WARNING"))
    log.addHandler(clog)
    log.debug("Console output initiated.")

if settings.profile["logger"]["file"]["enabled"]:
    flog = TRFileHandler(
        logfile, when="midnight", interval=1, backupCount=settings.profile["logger"]["file"].setdefault("max", 7)
    )
    timestamped = logging.Formatter(
        fmt="%(asctime)s %(name)-8s %(levelname)-10s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    flog.setLevel(settings.profile["logger"]["file"].setdefault("level", "INFO"))
    flog.setFormatter(timestamped)
    log.addHandler(flog)
    log.debug("Logging to file initiated.")
    log.info("Console output test.")

if __name__ == "__main__":
    if not os.path.isdir(backupdir):
        try:
            os.makedirs(backupdir)
        except FileExistsError:
            log.critical("Something is in the way.")
            log.critical("e")
            sys.exit()
    if not os.path.isdir(logdir):
        try:
            os.makedirs(logdir)
        except FileExistsError as e:
            log.critical("Something is in the way.")
            log.critical(e)
            sys.exit()

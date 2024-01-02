kbm_backup = cloup.command(
    'b', 'backup',
    help='Backs up the selected Klipper data.'
    )
kbm_restore = cloup.command(
    'r', 'restore', metavar='FILE N',
    help="Attempts to restore the selected Klipper data from local archives. "\
        "Specify type and an integer between 1 (most recent) "\
            "and the max_backups specified in your config profile")
 
kbm_dl = cloup.command('d', 'download',
    help="Doesn't do anything yet."
)
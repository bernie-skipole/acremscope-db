

#
# as root run this with crontab
# crontab -e
#
# 5-59/15 * * * * /usr/bin/python3 /opt/dbmaintenance/copybackups.py >/dev/null 2>&1
#
# ie every 15 minutes with a 5 minute offset
# so 1:20
#    1:35
#    1:50
#    2:05
#    2:20 etc..

#
# checks if file /opt/dbmaintenance/backup.sql.gz.cpt exists
# if not, exits
#
# check if directory /home/bernard/backups exists
# if not, exits

# check if file /opt/dbmaintenance/backup_old.sql.gz.cpt exists
# if it does, deletes it
#
# copies /opt/dbmaintenance/backup.sql.gz.cpt to /opt/dbmaintenance/backup_old.sql.gz.cpt
#
# generates a datetime filename
#
# copies /opt/dbmaintenance/backup.sql.gz.cpt to /home/bernard/backups/datetime.sql.gz.cpt
# ensures ownership is bernard:bernard
#
# deletes file /opt/dbmaintenance/backup.sql.gz.cpt
# exits

import sys, pathlib, shutil, datetime

sourcefile = pathlib.Path("/opt/dbmaintenance/backup.sql.gz.cpt")
oldfile = pathlib.Path("/opt/dbmaintenance/backup_old.sql.gz.cpt")
destination = pathlib.Path("/home/bernard/backups")
newowner = "bernard"

if not sourcefile.is_file():
    sys.exit(0)

if not destination.is_dir():
    sys.exit(0)

if oldfile.is_file():
    oldfile.unlink()

shutil.copy(sourcefile, oldfile)

destinationfile = destination / datetime.datetime.now().strftime("%Y%m%d%H%M.sql.gz.cpt")

shutil.copy(sourcefile, destinationfile)

shutil.chown(destinationfile, user=newowner, group=newowner)

sourcefile.unlink()

sys.exit(0)



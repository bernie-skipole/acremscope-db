

#
# as root run this with crontab
# crontab -e
#
# 30 14 * * 6 /usr/bin/python3 /opt/dbmaintenance/copybackups.py >/dev/null 2>&1
#
# ie 2:30 afternoon every saturday

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
# ensure the new /opt/dbmaintenance/backup_old.sql.gz.cpt has ownership postgres:postgres
#
# generates a datetime filename
#
# copies /opt/dbmaintenance/backup.sql.gz.cpt to /home/bernard/backups/datetime.sql.gz.cpt
# ensures ownership is bernard:bernard
#
# deletes file /opt/dbmaintenance/backup.sql.gz.cpt
#
# if more than 5 backup files in /home/bernard/backups/, delete the oldest
#
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

shutil.chown(oldfile, user="postgres", group="postgres")

destinationfile = destination / datetime.datetime.now().strftime("%Y%m%d%H%M.sql.gz.cpt")

shutil.copy(sourcefile, destinationfile)

shutil.chown(destinationfile, user=newowner, group=newowner)

sourcefile.unlink()

serverfiles = [f.name for f in destination.iterdir() if f.is_file()]
if len(serverfiles) <= 5:
    sys.exit(0)
# delete the last one
serverfiles.sort(reverse=True)
oldest_file = destination / serverfiles[-1]
oldest_file.unlink()

sys.exit(0)



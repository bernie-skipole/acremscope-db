

# as bernard run this with crontab -e
# 30 15 * * 6 /bin/bash /home/bernard/acremscope-db/sendbackups.sh >/dev/null 2>&1
# ie 3:30 afternoon every saturday



rsync -ua --del -e ssh ~/backups/ bernard@10.105.192.83:www/astrodata/served/backups


# This sends the backup files to the acremscope container at 10.105.192.83
# where they will be available to download if required
# the ip address must be changed if the container has another ip address




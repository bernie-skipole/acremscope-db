

# as bernard run this with crontab -e
# 30 15 * * 6 /bin/bash /home/bernard/savetopi.sh >/dev/null 2>&1
# ie 3:30 afternoon every saturday


file="/home/bernard/backup.sql.gz.cpt"

# send the backup to the pi

if [ -s $file ];
 then
    scp $file pi@192.168.1.64:backup.sql.gz.cpt
 fi







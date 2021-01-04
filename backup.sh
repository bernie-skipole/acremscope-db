
# backup.sh

# shell script to dump and encrypt the database to a backup file
# using pg_dump to dump, then gzip to compress and ccrypt to encrypt

# as postgres run this with crontab
# crontab -u postgres -e
# 30 13 * * 6 /bin/bash /opt/dbmaintenance/backup.sh >/dev/null 2>&1
# ie 1:30 afternoon every saturday

keypassphrase="set passphrase here"

file="/home/bernard/backups/backup.sql.gz.cpt"
oldfile="/home/bernard/backups/backup_old.sql.gz.cpt"


if [ -e $file ];
 then
    if [ -e $oldfile ];
     then
      rm $oldfile
     fi
    mv $file $oldfile
 fi

export keypassphrase

pg_dump -o astrodb | gzip | ccrypt -e -E keypassphrase > "$file"


# To decrypt manually use ccrypt -d from the command line
# you will be prompted for the keypassphrase,
# followed by gzip -d
#
# or use a similar shell file to this, setting the passphrase
# into environment keypassphrase, followed by:

# cat "$file" | ccrypt -d -E keypassphrase | gzip -d > "/home/bernard/backups/backup.sql"




# backup.sh

# shell script to dump and encrypt the database to a backup file
# using pg_dump to dump, then gzip to compress and ccrypt to encrypt

# as postgres run this with crontab
# crontab -u postgres -e
# 30 13 * * 6 /bin/bash /opt/dbmaintenance/backup.sh >/dev/null 2>&1
# ie 1:30 afternoon every saturday

keypassphrase="set passphrase here"

file="/opt/dbmaintenance/backup.sql.gz.cpt"
oldfile="/opt/dbmaintenance/backup_old.sql.gz.cpt"


if [ -e $file ];
 then
    if [ -e $oldfile ];
     then
      rm -f $oldfile
     fi
    mv $file $oldfile
 fi

export keypassphrase

pg_dump astrodb | gzip | ccrypt -e -E keypassphrase > "$file"


# To decrypt manually use ccrypt -d from the command line
# you will be prompted for the keypassphrase,
# followed by gzip -d

# note ccrypt -d changes the file in place, so if you want to retain the
# original backup - or if you dont have permission to write,
# copy the backup file first
#
# or use a similar shell file to this, setting the passphrase
# into environment keypassphrase, followed by:

# cat "$file" | ccrypt -d -E keypassphrase | gzip -d > "/opt/dbmaintenance/backup.sql"



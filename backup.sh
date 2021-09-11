
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

pg_dump -d astrodb --clean | gzip | ccrypt -e -E keypassphrase > "$file"


# To restore a backup file, edit restore.sh to have the filename and key passphrase


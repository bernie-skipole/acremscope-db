
# restore.sh

# shell script to decrypt and restore a database backup file, should be run as user postgres with
# source restore.sh

keypassphrase="set passphrase here"

# set the backup file to be restored to the database here
file="/opt/dbmaintenance/backup.sql.gz.cpt"

export keypassphrase

cat "$file" | ccrypt -d -E keypassphrase | gzip -d | psql -d astrodb

# this takes the file, de-crypts it, unzips it, and puts it into the database

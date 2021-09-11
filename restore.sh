
# restore.sh

# shell script to decrypt and restore a database backup file, should be run as user postgres with
# source restore.sh


# if necessary, delete an existing database, as user postgres
# psql
# drop database astrodb;
# \q

# then create a database ‘astrodb’ owned by user astro:
# createdb -O astro astrodb

# Then, still as postgres, enter the posgres client and connect to astrodb:
# psql -d astrodb
# The initial tables and content for astrodb are listed as sql commands in file ‘start_astrodb’
# At the astrodb prompt use the i option to input commands from start_astrodb:
# \i start_astrodb
# \q

keypassphrase="set passphrase here"

# set the backup file to be restored to the database here
file="/opt/dbmaintenance/backup.sql.gz.cpt"

export keypassphrase

cat "$file" | ccrypt -d -E keypassphrase | gzip -d | psql -d astrodb

# this takes the file, de-crypts it, unzips it, and puts it into the database

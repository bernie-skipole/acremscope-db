# Container build documentation

This documents creating a container on webparametrics.co.uk, for the full build of the server, see

[https://bernie-skipole.github.io/webparametrics/](https://bernie-skipole.github.io/webparametrics/)

This container will run a postgresql database for the Astronomy Centre Remscope application

On server webparametrics.co.uk, as user bernard

lxc launch ubuntu:20.04 acremscope-db

lxc list

This gives container ip address 10.105.192.252

lxc exec acremscope-db -- /bin/bash

This gives a bash console as root in the acremscope-db container. Update, install pip and add a user, in this case 'bernard'.

apt-get update

apt-get upgrade

apt-get install python3-pip

adduser bernard

record the password


## Install git, and clone acremscope-db repository

Then as user bernard create an ssh key

runuser -l bernard

ssh-keygen -t rsa -b 4096 -C "bernie@skipole.co.uk"

copy contents of .ssh/id_rsa.pub to github

copy contents of .ssh/id_rsa.pub to the acremscope container in /home/bernard/.ssh/authorized_keys, this allows this container to send backup files to the other container.

clone any required repositories

git clone git@github.com:bernie-skipole/acremscope-db.git


## Install postgresql

As root

apt-get install postgresql postgresql-client

psycopg2 is the python client for the postgresql database. Obtain this using apt-get rather than pip, so the binaries are installed without any build problems.

apt-get install python3-psycopg2

create directory /opt/dbmaintenance

Set the directory to be owned by postgres with permission 700 - as only root and postgres should have access.

cd /opt

chown postgres:postgres dbmaintenance

chmod 700 dbmaintenance

In future, set any files within dbmaintenance to postgres ownership and permissions 600.

copy start_astrodb to this directory

cp /home/bernard/acremscope-db/start_astrodb /opt/dbmaintenance

cd /opt/dbmaintenance

chown postgres:postgres start_astrodb

chmod 600 start_astrodb

for postgresql user authentication, see:

less /etc/postgresql/12/main/pg_hba.conf

Change the line of IPv4 local connections from

host   all   all   127.0.0.1/32   md5

to instead be

host   all   all   samenet   md5

in file /etc/postgresql/12/main/postgresql.conf

change the commented out line

listen_addresses = 'localhost' 

to the uncommented line

listen_addresses = '*'

then restart for configuation to take effect

systemctl restart postgresql

Then use the following commands to create the database and user:

su - postgres

create a non-system postgresql user 'astro',

createuser -P -W astro

This asks for the database password, for initial development use 'xxSgham',

P option: createuser will issue a prompt for the password of the new user.

W option: Force createuser to prompt for a password

Then create a database 'astrodb' owned by user astro:

createdb -O astro astrodb

Then, still as postgres, enter the posgres client and connect to astrodb:

psql -d astrodb

The initial tables and content for astrodb are listed as sql commands in file 'start_astrodb'

At the astrodb prompt use the i option to input commands from start_astrodb:

\i /opt/dbmaintenance/start_astrodb

Then use \q to exit the client, and fall out of user postgres (ctrl-D), right back to user bernard, and try:

psql -h localhost -U astro astrodb

give password xxSgham when prompted

and check you can access the database with:

select * from users;

and quit with \q

## automate backups

As bernard on the container, create directory backups

mkdir ~/backups

Check the file ~/acremscope-db/sendbackups.sh it should contain the ip address of the acremscope container.

As root:

apt-get install ccrypt

and put backup.sh, restore.sh and copybackups.py into /opt/dbmaintenance

cp /home/bernard/acremscope-db/backup.sh /opt/dbmaintenance

cp /home/bernard/acremscope-db/restore.sh /opt/dbmaintenance

cp /home/bernard/acremscope-db/copybackups.py /opt/dbmaintenance

cd /opt/dbmaintenance

chown postgres:postgres backup.sh

chmod 600 backup.sh

chown postgres:postgres restore.sh

chmod 600 restore.sh

chown postgres:postgres copybackups.py

chmod 600 copybackups.py

edit the key passphrase in backup.sh and restore.sh to one of your choice

And set the following using

crontab -u postgres -e

30 13 * * 6 /bin/bash /opt/dbmaintenance/backup.sh >/dev/null 2>&1

This will dump a backup at 1:30 afternoon every saturday into /opt/dbmaintenance

And set the following (note root crontab) using

crontab -e

30 14 * * 6 /usr/bin/python3 /opt/dbmaintenance/copybackups.py >/dev/null 2>&1

Which will run the script at 2:30 afternoon every saturday, this script copies
the backup file from /opt/dbmaintenance, sets a timestamp in its name, and stores it
into /home/bernard/backups.

And set the following (note bernard crontab)

crontab -u bernard -e

30 15 * * 6 /bin/bash /home/bernard/acremscope-db/sendbackups.sh >/dev/null 2>&1

Which will run the script at 3:30 afternoon every saturday, this script copies
the backups directory to the acremscope container where the backup files can be
made available to be downloaded.


## restore from a database backup file

As user postgres, move to directory /opt/dbmaintenance

Edit the file restore.sh so it points at the required backup file, then run with

source restore.sh


If this does not work, it may be necessary to delete the existing database.

psql

drop database astrodb;

\q

Then create a database ‘astrodb’ owned by user astro:

createdb -O astro astrodb

Then, still as postgres, enter the client and connect to astrodb:

psql -d astrodb

At the astrodb prompt use the i option to input commands from start_astrodb:

\i start_astrodb

\q

and again, restore from the backup file

source restore.sh


## automate database maintenance

clearguests.py is a python script using psycopg2 to query the database and delete expired guests at mid day each day.

As root on the container:

copy clearguests.py to /opt/dbmaintenance

cp /home/bernard/acremscope-db/clearguests.py /opt/dbmaintenance

cd /opt/dbmaintenance

chown postgres:postgres clearguests.py

And add the following to crontab using

crontab -u postgres -e

0 12,13 * * * /usr/bin/python3 /opt/dbmaintenance/clearguests.py >/dev/null 2>&1

So clearguests.py is run by postgres cron every mid day, and mid day + 1 hour, the script itself checks the time is 12:00 - so that it is only run once at utc 12, this is done as cron uses local time, so this ensures utc is used.


## password reset

The 'admin' user of the acremscope telescope users is a special user that cannot be deleted from the acremscope remote telescope system, and is intended as the fall back admin user in case other admin users mess the system up. If this admin user gets its password and pin changed and forgotten, the script resetpwd.py can be run to reset it.

So as user bernard, in directory ~/acremscope.py

python3 resetpwd.py

And input a password and prompt when requested. The script will save these to the database, and also output the hashes saved, which can be ignored.



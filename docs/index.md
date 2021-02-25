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

psql astrodb

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

As root on the container

apt-get install ccrypt

and put backup.sh and copybackups.py into /opt/dbmaintenance

cp /home/bernard/acremscope-db/backup.sh /opt/dbmaintenance

cp /home/bernard/acremscope-db/copybackups.py /opt/dbmaintenance

cd /opt/dbmaintenance

chown postgres:postgres backup.sh

chmod 600 backup.sh

edit the key passphrase in backup.sh to one of your choice

And set the following using

crontab -u postgres -e

30 13 * * 6 /bin/bash /opt/dbmaintenance/backup.sh >/dev/null 2>&1

This will dump a backup at 1:30 afternoon every saturday into /opt/dbmaintenance

chown postgres:postgres copybackups.py

chmod 600 copybackups.py

And set the following (note root crontab) using

crontab -e

5-59/15 * * * * /usr/bin/python3 /opt/dbmaintenance/copybackups.py >/dev/null 2>&1

Which will run the script every 15 minutes with a 5 minute offset, this script copies
the backup file from /opt/dbmaintenance, sets a timestamp in its name, and stores it
into /home/bernard/backups ready to be served by a password protected web service.

# create web service

As root, install redis, which is needed by the web service

apt-get install redis

As bernard on the container, create directory www

mkdir ~/www

cp ~/acremscope-db/resetpwd.py ~/www

cp ~/acremscope-db/servebackups.py ~/www

cp -r ~/acremscope-db/servebackups ~/www

A hashed password needs to be set into servebackups.py, to do so, decide on a username and password and use the script

python3 ~/acremscope-db/hashpassword.py

Which will ask for a username and password and then output a long string of the hashed password. Copy that string and paste it, together with the username into the head of the file ~/www/servebackups.py

and install redis client, skipole and waitress

python3 -m pip install --user skipole

python3 -m pip install --user redis

python3 -m pip install --user waitress

as root, copy the file

cp /home/bernard/www/servebackups.service /lib/systemd/system

Enable the service with

systemctl daemon-reload

systemctl enable servebackups.service

systemctl start servebackups

This starts /home/bernard/www/servebackups.py on boot up.

The site will be visible at.

[https://webparametrics.co.uk/acremscope/backups](https://webparametrics.co.uk/acremscope/backups)


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

So as user bernard, in directory ~/www

python3 resetpwd.py

And input a password and prompt when requested. The script will save these to the database, and also output the hashes saved, which can be ignored.





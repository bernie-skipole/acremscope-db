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

psycopg2 is the python client for the postgresql database.

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

Then use \q to exit the client, and fall out of user postgres (ctrl-D)and try:

psql "dbname=astrodb user=astro password=xxSgham host=127.0.0.1"

and check you can access the database with:

select * from users;

and quit with \q

## automate backups

As bernard on the container, create directory backups, with permissions 777 so
a postgres backup routine can write files into it

mkdir backups

chmod 777 backups

As root on the container

apt-get install ccrypt

and put backup.sh into /opt/dbmaintenance

cp /home/bernard/acremscope-db/backup.sh /opt/dbmaintenance

cd /opt/dbmaintenance

chown postgres:postgres backup.sh

chmod 600 backup.sh

edit the key passphrase in backup.sh to one of your choice

And set the following using

crontab -u postgres -e

30 13 * * 6 /bin/bash /opt/dbmaintenance/backup.sh >/dev/null 2>&1


## automate clearing guest accounts

0 12,13 * * * python3 /opt/dbmaintenance/clearguests.py >/dev/null 2>&1




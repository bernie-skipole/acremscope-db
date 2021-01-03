# Container build documentation

This documents creating a container on webparametrics.co.uk, for the full build of the server, see

[https://bernie-skipole.github.io/webparametrics/](https://bernie-skipole.github.io/webparametrics/)

This container will run a postgres database for the Astronomy Centre Remscope application

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



# Clears out expired guests

# as postgres run this with crontab
# crontab -u postgres -e
# 0 12,13 * * * /usr/bin/python3 /opt/dbmaintenance/clearguests.py >/dev/null 2>&1

# run by postgres cron every mid day, and mid day + 1
# cron works on local time, so mid day, and mid day + 1 should get 12 utc between them


import sys

from datetime import datetime

now = datetime.utcnow()

# ensure time is utc 12:00
if now.hour != 12:
    sys.exit(0)

import psycopg2, redis

# the following should match the settings used to create the database

dbname = 'astrodb'
dbuser = 'astro'
dbpassword ='xxSgham'


message = "Clearing expired guests"

con = None
try:
    con = psycopg2.connect(dbname=dbname, user=dbuser, password=dbpassword, host='127.0.0.1')
    cur = con.cursor()
    cur.execute("select user_id from guests where exp_date < %s", (now,))
    guests = cur.fetchall()
    if guests:
        for guest in guests:
            user_id = guest[0]
            cur.execute("delete from slots where user_id = %s", (user_id,))
            cur.execute("delete from users where user_id = %s", (user_id,))
        con.commit()
        message = "deleted expired guests"
    else:
        message = "check made for expired guests - none found"
except Exception:
    message = "check for expired guests has failed"
finally:
    if con:
        con.close()

print(message)

# sends a log to redis, this is available to the database web service which lists backup
# files. The web service does not currently use it, but may in future

try:
    rconn = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
    # create a log entry to set in the redis server
    fullmessage = now.strftime("%Y-%m-%d %H:%M:%S") + " " + message
    rconn.rpush("log_info", fullmessage)
    # and limit number of messages to 50
    rconn.ltrim("log_info", -50, -1)
except Exception:
    print("Unable to store log in redis")

sys.exit(0)


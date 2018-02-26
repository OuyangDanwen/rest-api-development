#!/bin/bash

apachectl start
mongod --smallfiles --bind_ip_all --fork --logpath /log/mongod.log
mongo diary_app --eval 'db.counter.insert({"value": 0})'
python /service/app.py

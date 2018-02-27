#!/bin/bash

apachectl start
mongod --smallfiles --fork --logpath /log/mongod.log
mongo diary_app --eval 'db.counter.insert({"value": 0})'
python /service/app.py

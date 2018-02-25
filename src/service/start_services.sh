#!/bin/bash

apachectl start
mongod --smallfiles --bind_ip_all --fork --logpath /log/mongod.log
python /service/app.py

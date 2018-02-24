#!/bin/bash

apachectl start
mongod --smallfiles --fork --logpath /log/mongod.log
python /service/app.py

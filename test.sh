#!/usr/bin/env bash

# ./run.sh &
# RUNPID=$!

python src/test/*.test.py
RESULT=$?

# kill $RUNPID
exit "$RESULT"


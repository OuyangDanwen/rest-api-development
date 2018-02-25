#!/usr/bin/env bash

# ./run.sh &
# RUNPID=$!

if [ -z ${CIRCLE_TEST_REPORTS+x} ]
then
    python src/test/*.py
else
    pytest --junitxml $CIRCLE_TEST_REPORTS/reports/src_test.xml src/test
fi
RESULT=$?

# kill $RUNPID
exit "$RESULT"


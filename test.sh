#!/bin/bash

python -m doctest -o IGNORE_EXCEPTION_DETAIL -f test/test.txt

[ $? -eq 0 ] && echo 'Test passed.'

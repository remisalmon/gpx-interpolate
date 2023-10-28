#!/usr/bin/env bash

python3.8 -m venv venv

source venv/bin/activate

python -m pip install -U pip setuptools
python -m pip install -r requirements.txt

python -m doctest -o IGNORE_EXCEPTION_DETAIL -f tests/tests.txt || exit 1

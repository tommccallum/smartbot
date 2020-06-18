#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"
PYTHON=$( which python3 )

$PYTHON $DIR/client/src/make_speech.py


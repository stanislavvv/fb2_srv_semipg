#!/bin/bash

if [[ -d venv ]]; then
    . venv/bin/activate
fi

./datachew.py "$@"



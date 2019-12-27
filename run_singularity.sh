#!/bin/sh

# Small shell wrapper to assist with executing Endgame: Singularity

DIR="$(dirname "$0")"
PYTHON=${PYTHON:-python3}
PYPATH=${DIR}${PYTHONPATH:+:${PYTHONPATH}}
PYTHONPATH="${PYPATH}" "${PYTHON}" -m singularity

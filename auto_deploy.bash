#!/bin/env bash

LINK=$(readlink -f "$0")
BASE_DIR=$(dirname "$LINK")
cd "$BASE_DIR" || echo "Unable to change directory to $BASE_DIR" && exit 1

lock () {

    LOCKDIR=/tmp/deployment.lock

    trap 'rm -r $LOCKDIR' SIGINT
    trap 'rm -r $LOCKDIR; exit' ERR EXIT

    if mkdir $LOCKDIR
    then
        echo >&2 "Lock Acquired"
    else
        echo >&2 "Can not Acquire Lock."
        exit 1
    fi
}


has_change () {

    # Has Any Change?
    git fetch --all
    git diff ^main origin/main --exit-code
    EXITCODE=$?
    if [ $EXITCODE -eg 0 ]
    then
     echo "No change."
     exit 0
    fi
}


deploy () {

    git checkout origin/master
    source env/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    python manage.py migrate
    systemctl restart ath_status.service

}

lock
has_change
deploy

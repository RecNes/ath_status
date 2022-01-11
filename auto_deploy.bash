#!/usr/bin/env bash

LINK=$(readlink -f "$0")
BASE_DIR=$(dirname "$LINK")
cd $BASE_DIR || echo "Unable to switch to $BASE_DIR"; exit 1

LOCKDIR=/tmp/deployment.lock

trap 'rm -r $LOCKDIR' SIGINT
trap 'rm -r $LOCKDIR; exit' ERR EXIT

if mkdir $LOCKDIR
then
  echo "Lock Acquired"
else
  echo "Can not Acquire Lock."
  exit 1
fi

git fetch --all
git diff ^main origin/main --exit-code
EXITCODE=$?
test $EXITCODE -eq 0 && echo "No change."; exit 0

git checkout origin/master
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
systemctl restart ath_status.service

echo "Done!"

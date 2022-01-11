#!/usr/bin/env bash

LINK=$(readlink -f "$0")
BASE_DIR=$(dirname "$LINK")
cd "${BASE_DIR}" || exit "Unable to switch to ${BASE_DIR}"

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

if [ $(git log HEAD..origin/main --oneline) ]
then
  echo "asdfas"
else
  echo "qweq"
fi
EXITCODE=$?
test $EXITCODE -eq 0 && echo "No change."; exit 0

git checkout origin/master
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
systemctl restart ath_status.service

echo "Done!"

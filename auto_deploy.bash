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

if [ ! $(git log HEAD..origin/main --oneline) ]
then
  echo "No Change!"
  exit 0
else
  echo "qweq"
fi

git checkout origin/master
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
systemctl restart ath_status.service

echo "Done!"

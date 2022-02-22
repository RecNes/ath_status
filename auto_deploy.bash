#!/usr/bin/env bash

LINK=$(readlink -f "$0")
BASE_DIR=$(dirname "$LINK")
cd "${BASE_DIR}" || exit "Unable to switch to ${BASE_DIR}"

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

git fetch --all
GIT_STATUS=$(git log HEAD..origin/main --oneline)
if [ -z "$GIT_STATUS" ]
then
  echo >&2 "No Change!"
  exit 0
else
  echo >&2 "Deploying changes..."
fi

git checkout main
git reset --hard origin/main
git pull
cp -fab .env_vars.txt env_vars.txt
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
echo >&2 "Restarting service."
systemctl restart ath_status.service

echo >&2 "Done!"

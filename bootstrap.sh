#!/usr/bin/env bash

set -e

if ! grep -Fxq "UseDNS no" /etc/ssh/sshd_config
then
    echo -e "\n\nUseDNS no" >> /etc/ssh/sshd_config
    echo "GSSAPIAuthentication no" >> /etc/ssh/sshd_config
    service ssh restart
fi

echo "Provisioning PostgreSQL..."

PG_REPO_APT_SOURCE=/etc/apt/sources.list.d/pgdg.list

if [ ! -f "$PG_REPO_APT_SOURCE" ];
then
    echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" > "$PG_REPO_APT_SOURCE"
    wget --quiet -O - https://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | apt-key add -

    apt-get update
    # apt-get -y upgrade

    apt-get -y install "postgresql-9.4" "postgresql-contrib-9.4"

    PG_CONF="/etc/postgresql/9.4/main/postgresql.conf"
    PG_HBA="/etc/postgresql/9.4/main/pg_hba.conf"

    echo "host    all             all             all                     trust" > "$PG_HBA"
    echo "local    all             all                                  trust" >> "$PG_HBA"
    echo "client_encoding = utf8" >> "$PG_CONF"
else
    apt-get update
fi

service postgresql restart

cat << EOF | su - postgres -c psql
-- Create the database user:
CREATE USER synapse WITH ENCRYPTED PASSWORD 'foobar';

-- Create the database:
CREATE DATABASE synapse WITH OWNER=synapse
                                  LC_COLLATE='C'
                                  LC_CTYPE='C'
                                  ENCODING='UTF8'
                                  TEMPLATE=template0;
EOF

echo "Provisioning Synapse..."

apt-get -y install build-essential python2.7-dev libffi-dev \
    python-pip python-setuptools sqlite3 \
    libssl-dev python-virtualenv libjpeg-dev libyaml-dev libpq-dev

[ `id -u synapse` ] || adduser --disabled-password --gecos "" synapse

cp /vagrant/*.yaml ~synapse/
chmod a+r ~synapse/*.yaml
chown synapse ~synapse/*.yaml

su - synapse <<EOF
set -e
[ ! -f ~/.synapse/bin/activate ] && virtualenv ~/.synapse
source ~/.synapse/bin/activate
pip install --upgrade pip setuptools
python /mnt/synapse/synapse/python_dependencies.py | xargs -n1 pip install
pip install setuptools_trial mock psycopg2
mkdir -p ~/config/
cd ~/config
export PYTHONPATH=/mnt/synapse/
test -f homeserver.yaml && python /mnt/synapse/synctl stop
if [ ! -f homeserver.yaml ];
then
    cp ~/homeserver.yaml .
    cp ~/logging.yaml .
fi
python /mnt/synapse/synctl start
EOF

echo "Finished provisioning"

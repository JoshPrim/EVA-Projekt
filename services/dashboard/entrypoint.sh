#!/bin/sh

echo "Waiting for postgres an mongodb..."

while ! nc -z station-db 5432 && ! nc -z mongo-db 27017; do
  sleep 0.1
done

echo "PostgreSQL & Mongo startet!"

python ./dashboard_server.py

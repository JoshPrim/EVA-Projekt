#!/bin/sh

echo "Waiting for mongo-db..."

while ! nc -z mongo-db 27017; do
  sleep 0.1
done

echo "Mongo started"

python ./app.py
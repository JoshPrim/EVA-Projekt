#!/bin/sh

echo "Waiting for mongo-db..."

#while ! nc -z mongo-db 27018; do
#  sleep 0.1
#done

echo "Mongo started"

python manage.py
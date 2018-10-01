#!/bin/bash

echo "Initializing Mongo"

mongo admin  -u bart -p 'downy37)tory'

use eva_dev

db.createUser({ user: "bart", pwd: "downy37)tory", roles: [{ role: "dbOwner", db: "eva_dev" }] })

db.auth("bart","downy37)tory")

db.createCollection("facilities")


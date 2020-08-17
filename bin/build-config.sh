#!/bin/bash

export SA_CREDS=$(cat ./credentials.json)
export ROLES=$(cat ./roles.json)
CONFIG=$(envsubst < ./config_template.json)
export CONFIG
